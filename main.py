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
            print("✅ Sync Commands Success!")
        except Exception as e:
            print(f"❌ Sync Error: {e}")

bot = MyBot()
normal_trigger_id = None 

@bot.event
async def on_ready():
    print(f"✅ บอท {bot.user} พร้อมลุย!")

@bot.tree.command(name="create_room", description="สร้างห้องสุ่มย้ายปกติ")
async def create_room(interaction: discord.Interaction):
    global normal_trigger_id
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ เฉพาะแอดมินเท่านั้น", ephemeral=True)
        return
    try:
        channel = await interaction.guild.create_voice_channel(name="🎲 สุ่มห้องลง")
        normal_trigger_id = channel.id
        await interaction.response.send_message(f"✅ สร้างห้อง {channel.mention} สำเร็จ!", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)

@bot.event
async def on_voice_state_update(member, before, after):
    global normal_trigger_id
    
    # ส่งต่อให้ระบบสุ่มหาเพื่อน (main2)
    await main2.handle_online_random(member, after, normal_trigger_id)
    
    # ระบบสุ่มทั่วไป (Main)
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
                # 📢 บังคับส่งข้อความลงในแชทของห้องเสียง "ปลายทาง" เท่านั้น
                await target.send(f"ผู้ใช้บัญชีชื่อ **{member.display_name}** ได้ทำการสุ่มห้องมาครับ")
            except: pass

if TOKEN:
    keep_alive()
    bot.run(TOKEN)