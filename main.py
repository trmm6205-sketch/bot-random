import discord
import random
import os
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

# --- 1. ระบบ Keep Alive สำหรับ Render (ป้องกัน Timed Out) ---
app = Flask('')

@app.route('/')
def home():
    return "KHMER CLUB Bot is Online!"

def run():
    # ใช้พอร์ตที่ Render กำหนดมาให้ (Default: 10000)
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- 2. ตั้งค่าบอท ---
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
        try:
            # บังคับซิงค์คำสั่ง Slash ใหม่ทุกครั้ง
            synced = await self.tree.sync()
            print(f"✅ ซิงค์คำสั่ง Slash สำเร็จ! (พบ {len(synced)} คำสั่ง)")
        except Exception as e:
            print(f"❌ Sync Error: {e}")

bot = MyBot()
random_trigger_channel_id = None 

@bot.event
async def on_ready():
    print(f"✅ บอท {bot.user} ออนไลน์ในเขมรคลับแล้ว!")
    print("---------------------------------")

# --- 3. คำสั่งสร้างห้องสุ่ม (ล็อคเฉพาะแอดมิน) ---
@bot.tree.command(name="create_room", description="สร้างห้องสุ่มย้าย (เฉพาะแอดมินเท่านั้น)")
async def create_room(interaction: discord.Interaction):
    global random_trigger_channel_id
    
    # 🚨 ตรวจสอบสิทธิ์แอดมิน
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "❌ ขออภัยครับ คุณไม่สามารถใช้คำสั่งนี้ได้ (เฉพาะผู้ดูแลระบบที่มีสิทธิ์แอดมินเท่านั้น)", 
            ephemeral=True
        )
        return

    try:
        channel = await interaction.guild.create_voice_channel(name="🎲 สุ่มห้องลง")
        random_trigger_channel_id = channel.id
        await interaction.response.send_message(f"✅ สร้างห้อง {channel.mention} สำเร็จ! พร้อมใช้งานแล้ว", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ เกิดข้อผิดพลาด: {e}", ephemeral=True)

# --- 4. ระบบสุ่มย้ายคน (ทำงานปกติสำหรับทุกคน) ---
@bot.event
async def on_voice_state_update(member, before, after):
    global random_trigger_channel_id
    
    if after.channel and after.channel.id == random_trigger_channel_id and not member.bot:
        all_channels = [
            vc for vc in member.guild.voice_channels 
            if vc.id != random_trigger_channel_id and (vc.user_limit == 0 or len(vc.members) < vc.user_limit)
        ]
        
        if all_channels:
            target = random.choice(all_channels)
            try:
                await member.move_to(target)
                message = f"ผู้ใช้บัญชีชื่อ **{member.name}** นี้สุ่มห้องมา"
                await target.send(message)
            except Exception as e:
                print(f"❌ ไม่สามารถย้ายได้: {e}")

# --- 5. เริ่มทำงาน ---
if TOKEN:
    keep_alive() # เริ่มระบบ Keep Alive ก่อนรันบอท
    bot.run(TOKEN)
else:
    print("❌ ไม่พบ TOKEN ในไฟล์ .env หรือ Environment Variable!")