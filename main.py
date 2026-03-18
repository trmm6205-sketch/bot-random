import discord
import random
import os
import main2
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

# --- ระบบ Keep Alive เพื่อให้บอทไม่ง่วงบน Render ---
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

# 🚩 ไอดีห้องเสียงที่นายต้องการให้บอทอยู่ 24 ชม.
STAY_VOICE_CHANNEL_ID = 1483404597560344759 

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.voice_states = True
        intents.guilds = True
        intents.members = True
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # ดึงคำสั่งจาก main2 มาใช้ด้วย
        main2.setup_online_commands(self.tree)
        try:
            await self.tree.sync()
            print("✅ Sync Slash Commands เรียบร้อย!")
        except Exception as e:
            print(f"❌ Sync Error: {e}")

bot = MyBot()
normal_trigger_id = None 

# --- คำสั่งสร้างห้องสุ่มปกติ (Main) ---
@bot.tree.command(name="create_room", description="สร้างห้องสุ่มย้ายคนปกติ")
async def create_room(interaction: discord.Interaction):
    global normal_trigger_id
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ เฉพาะแอดมินเท่านั้น", ephemeral=True)
        return
    try:
        channel = await interaction.guild.create_voice_channel(name="🎲 สุ่มลงห้อง")
        normal_trigger_id = channel.id
        await interaction.response.send_message(f"✅ สร้างห้อง {channel.mention} สำเร็จ!", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)

@bot.event
async def on_ready():
    print(f"✅ บอท {bot.user} ออนไลน์แล้ว!")
    
    # --- ระบบเข้าห้องเสียง 24 ชม. ---
    channel = bot.get_channel(STAY_VOICE_CHANNEL_ID)
    if channel:
        try:
            vc = discord.utils.get(bot.voice_clients, guild=channel.guild)
            if not vc:
                await channel.connect()
                print(f"🎙️ บอทเข้าเฝ้าห้อง {channel.name} เรียบร้อย!")
        except Exception as e:
            print(f"❌ เข้าห้องไม่ได้: {e}")

@bot.event
async def on_voice_state_update(member, before, after):
    global normal_trigger_id
    
    # 1. ป้องกันบอทหลุดจากห้อง 24 ชม.
    if member.id == bot.user.id and after.channel is None:
        channel = bot.get_channel(STAY_VOICE_CHANNEL_ID)
        if channel: await channel.connect()

    # 2. ส่งไปให้ระบบ main2 (สุ่มหาเพื่อน) ทำงาน
    await main2.handle_online_random(member, after, normal_trigger_id)
    
    # 3. ระบบสุ่มปกติ (เขียนลงแชทห้องเสียงปลายทาง)
    if after.channel and after.channel.id == normal_trigger_id and not member.bot:
        available_channels = []
        for vc in member.guild.voice_channels:
            if vc.id not in [normal_trigger_id, main2.online_trigger_id]:
                user_perms = vc.permissions_for(member)
                bot_perms = vc.permissions_for(member.guild.me)
                if user_perms.view_channel and user_perms.connect and bot_perms.view_channel:
                    if vc.user_limit == 0 or len(vc.members) < vc.user_limit:
                        available_channels.append(vc)
        
        if available_channels:
            target = random.choice(available_channels)
            try:
                await member.move_to(target)
                await target.send(f"ผู้ใช้ชื่อ **{member.display_name}** สุ่มย้ายมาที่ห้องนี้ครับ!")
            except: pass

if TOKEN:
    keep_alive()
    bot.run(TOKEN)