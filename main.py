import discord
import random
import os
import main2  # ต้องมีบรรทัดนี้เพื่อดึงไฟล์ที่สองมาใช้
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

# --- 1. ระบบ Keep Alive (สำหรับ Render) ---
app = Flask('')
@app.route('/')
def home(): return "Bot is Online!"

def run():
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
        # โหลดคำสั่ง Slash Command จาก main2
        main2.setup_online_commands(self.tree)
        try:
            synced = await self.tree.sync()
            print(f"✅ ซิงค์คำสั่งสำเร็จ! (พบ {len(synced)} คำสั่ง)")
        except Exception as e:
            print(f"❌ Sync Error: {e}")

bot = MyBot()
normal_trigger_id = None 

@bot.event
async def on_ready():
    print(f"✅ บอท {bot.user} พร้อมลุยในเขมรคลับแล้ว!")

# --- 3. คำสั่งสร้างห้องสุ่มทั่วไป (Main) ---
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
        await interaction.response.send_message(f"❌ สร้างไม่สำเร็จ: {e}", ephemeral=True)

# --- 4. ระบบจัดการการย้าย (จุดเชื่อมต่อสำคัญ) ---
@bot.event
async def on_voice_state_update(member, before, after):
    global normal_trigger_id
    
    # 🚨 ส่งไปให้ main2 ทำงาน (สุ่มหาคนออนไลน์)
    await main2.handle_online_random(member, after, normal_trigger_id)
    
    # ระบบสุ่มทั่วไป (ใน main)
    if after.channel and after.channel.id == normal_trigger_id and not member.bot:
        all_channels = [
            vc for vc in member.guild.voice_channels 
            if vc.id not in [normal_trigger_id, main2.online_trigger_id] 
            and (vc.user_limit == 0 or len(vc.members) < vc.user_limit)
        ]
        
        if all_channels:
            target = random.choice(all_channels)
            try:
                await member.move_to(target)
                print(f"✅ ย้าย {member.name} ไปห้อง {target.name}")
            except Exception as e:
                print(f"❌ ย้ายไม่ได้ (Main): {e}")

if TOKEN:
    keep_alive()
    bot.run(TOKEN)