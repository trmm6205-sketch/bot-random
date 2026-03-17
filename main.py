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
def home(): return "Bot Online!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

def keep_alive():
    Thread(target=run).start()

# --- ตั้งค่าบอท ---
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.voice_states = intents.guilds = intents.members = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # ดึงคำสั่งสร้างห้องสุ่มหาคนออนมาจาก main2
        main2.setup_online_commands(self.tree)
        await self.tree.sync()
        print("✅ ซิงค์คำสั่งทั้งหมดสำเร็จ!")

bot = MyBot()
normal_trigger_id = None 

@bot.event
async def on_ready():
    print(f"✅ {bot.user} พร้อมใช้งานในเขมรคลับ!")

# --- คำสั่งสร้างห้องสุ่มทั่วไป (อยู่ใน main) ---
@bot.tree.command(name="create_room", description="สร้างห้องสุ่มย้ายปกติ")
async def create_room(interaction: discord.Interaction):
    global normal_trigger_id
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ เฉพาะแอดมินเท่านั้น", ephemeral=True)
        return
    channel = await interaction.guild.create_voice_channel(name="🎲 สุ่มห้องลง")
    normal_trigger_id = channel.id
    await interaction.response.send_message(f"✅ สร้างห้อง {channel.mention} สำเร็จ!", ephemeral=True)

# --- ระบบจัดการการย้าย ---
@bot.event
async def on_voice_state_update(member, before, after):
    global normal_trigger_id
    
    # 1. ส่งให้ main2 เช็ก (สุ่มหาคนออน)
    await main2.handle_online_random(member, after, normal_trigger_id)
    
    # 2. เช็กสุ่มปกติ (ใน main)
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
                await target.send(f"ผู้ใช้บัญชีชื่อ **{member.name}** สุ่มห้องลงมาที่นี่ครับ")
            except: pass

if TOKEN:
    keep_alive()
    bot.run(TOKEN)