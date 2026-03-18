import discord
import random
import os
import main2
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

# --- ระบบ Keep Alive ---
app = Flask('')
@app.route('/')
def home(): return "Bot is Online!"

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.voice_states = True
        intents.guilds = True
        intents.members = True
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        main2.setup_online_commands(self.tree)
        try:
            await self.tree.sync()
            print("✅ Sync Success!")
        except Exception as e:
            print(f"❌ Sync Error: {e}")

bot = MyBot()
normal_trigger_id = None 

# --- คำสั่งสร้างห้องสุ่มปกติ และให้บอทเข้าทันที ---
@bot.tree.command(name="create_room", description="สร้างห้องสุ่มย้ายคนและให้บอทเฝ้า")
async def create_room(interaction: discord.Interaction):
    global normal_trigger_id
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ เฉพาะแอดมินเท่านั้น", ephemeral=True)
        return
    try:
        # 1. สร้างห้อง
        channel = await interaction.guild.create_voice_channel(name="🎲 สุ่มลงห้อง")
        normal_trigger_id = channel.id
        
        # 2. สั่งบอทกระโดดเข้าห้องที่เพิ่งสร้างทันที
        await channel.connect()
        
        await interaction.response.send_message(f"✅ สร้างห้อง {channel.mention} และบอทเข้าเฝ้าแล้ว!", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)

@bot.event
async def on_ready():
    print(f"✅ บอท {bot.user} พร้อมลุย!")

@bot.event
async def on_voice_state_update(member, before, after):
    global normal_trigger_id
    
    # 1. ป้องกันบอทหลุด (ถ้าบอทโดนเตะออกจากห้องสุ่ม ให้มันกลับเข้าไปใหม่)
    if member.id == bot.user.id and after.channel is None and normal_trigger_id:
        channel = bot.get_channel(normal_trigger_id)
        if channel: await channel.connect()

    # 2. ส่งไประบบ main2
    await main2.handle_online_random(member, after, normal_trigger_id)
    
    # 3. ระบบสุ่มปกติ
    if after.channel and after.channel.id == normal_trigger_id and not member.bot:
        available_channels = [vc for vc in member.guild.voice_channels 
                             if vc.id not in [normal_trigger_id, main2.online_trigger_id]]
        
        # กรองห้องที่เข้าได้และไม่เต็ม
        valid_channels = []
        for vc in available_channels:
            user_perms = vc.permissions_for(member)
            bot_perms = vc.permissions_for(member.guild.me)
            if user_perms.view_channel and user_perms.connect and bot_perms.view_channel:
                if vc.user_limit == 0 or len(vc.members) < vc.user_limit:
                    valid_channels.append(vc)

        if valid_channels:
            target = random.choice(valid_channels)
            try:
                await member.move_to(target)
                await target.send(f"ผู้ใช้ชื่อ **{member.display_name}** สุ่มย้ายมาที่ห้องนี้ครับ!")
            except: 
                pass