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

# 🚩 ใส่ ID ห้องเสียงที่ต้องการให้บอทอยู่ 24 ชม. ตรงนี้
STAY_VOICE_CHANNEL_ID = 1483404597560344759  # <-- เปลี่ยนเลขนี้เป็น ID ห้องนาย

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

@bot.event
async def on_ready():
    print(f"✅ บอท {bot.user} พร้อมลุย!")
    
    # --- บังคับบอทเข้าห้องเสียงตอนเริ่มทำงาน ---
    channel = bot.get_channel(STAY_VOICE_CHANNEL_ID)
    if channel and isinstance(channel, discord.VoiceChannel):
        try:
            vc = discord.utils.get(bot.voice_clients, guild=channel.guild)
            if not vc:
                await channel.connect()
                print(f"🎙️ บอทเข้าเฝ้าห้อง {channel.name} แล้ว")
        except Exception as e:
            print(f"❌ เข้าห้องไม่ได้: {e}")

@bot.event
async def on_voice_state_update(member, before, after):
    global normal_trigger_id
    
    # 1. ระบบดึงบอทกลับห้องถ้าหลุด (24 ชม.)
    if member.id == bot.user.id and after.channel is None:
        channel = bot.get_channel(STAY_VOICE_CHANNEL_ID)
        if channel:
            await channel.connect()

    # 2. ส่งต่อระบบสุ่มหาเพื่อน (main2)
    await main2.handle_online_random(member, after, normal_trigger_id)
    
    # 3. ระบบสุ่มทั่วไป (เขียนลงแชทห้องเสียงปลายทาง)
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
                # 📢 เขียนลงแชทของห้องเสียงปลายทาง
                await target.send(f"ผู้ใช้บัญชีชื่อ **{member.display_name}** ได้ทำการสุ่มห้องมาครับ")
            except: pass

if TOKEN:
    keep_alive()
    bot.run(TOKEN)