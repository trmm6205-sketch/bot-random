import discord
import random
import os
import main2
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

# --- 1. ระบบ Keep Alive ---
app = Flask('')

@app.route('/')
def home():
    return "KHMER CLUB Bot is Online!"

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
        try:
            synced = await self.tree.sync()
            print(f"✅ ซิงค์คำสั่ง Slash สำเร็จ! (พบ {len(synced)} คำสั่ง)")
        except Exception as e:
            print(f"❌ Sync Error: {e}")

bot = MyBot()
random_trigger_channel_id = None 

# --- 3. คำสั่งต่างๆ ---
@bot.event
async def on_ready():
    print(f"✅ บอท {bot.user} ออนไลน์แล้ว!")

@bot.tree.command(name="create_room", description="สร้างห้องสุ่มย้ายปกติ")
async def create_room(interaction: discord.Interaction):
    global random_trigger_channel_id
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ เฉพาะแอดมินเท่านั้น", ephemeral=True)
        return
    channel = await interaction.guild.create_voice_channel(name="🎲 สุ่มห้องลง")
    random_trigger_channel_id = channel.id
    await interaction.response.send_message(f"✅ สร้างห้อง {channel.mention} สำเร็จ!", ephemeral=True)

@bot.tree.command(name="create_room_online", description="สร้างห้องสุ่มหาเพื่อนที่มีคนอยู่")
async def create_room_online(interaction: discord.Interaction):
    await main2.create_online_room_logic(interaction)

# --- 4. ระบบจัดการการย้าย ---
@bot.event
async def on_voice_state_update(member, before, after):
    global random_trigger_channel_id
    
    # ส่งให้ main2 จัดการก่อน
    await main2.handle_online_random(member, after, random_trigger_channel_id)
    
    # ระบบสุ่มปกติ
    if after.channel and after.channel.id == random_trigger_channel_id and not member.bot:
        all_channels = [
            vc for vc in member.guild.voice_channels 
            if vc.id != random_trigger_channel_id 
            and vc.id != main2.random_online_channel_id
            and (vc.user_limit == 0 or len(vc.members) < vc.user_limit)
        ]
        if all_channels:
            target = random.choice(all_channels)
            try:
                await member.move_to(target)
                await target.send(f"ผู้ใช้บัญชีชื่อ **{member.name}** สุ่มห้องลงมาที่นี่ครับ")
            except:
                pass

if TOKEN:
    keep_alive()
    bot.run(TOKEN)