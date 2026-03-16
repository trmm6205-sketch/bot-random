import discord
import random
import os
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

# --- 1. โหลดค่า TOKEN ---
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
            print(f"✅ ซิงค์คำสั่ง Slash เรียบร้อย!")
        except Exception as e:
            print(f"❌ Sync Error: {e}")

bot = MyBot()
random_trigger_channel_id = None 

@bot.event
async def on_ready():
    print(f"✅ บอท {bot.user} พร้อมทำงาน!")
    print("---------------------------------")

# --- 2. คำสั่งสร้างห้องสุ่ม (เช็กสิทธิ์ในตัวโค้ด) ---
@bot.tree.command(name="create_room", description="สร้างห้องสุ่มย้าย (เฉพาะแอดมิน)")
async def create_room(interaction: discord.Interaction):
    global random_trigger_channel_id
    
    # 🚨 เช็กสิทธิ์: ถ้าคนกดไม่ใช่แอดมิน ให้ส่งข้อความเตือน
    if not interaction.user.guild_permissions.administrator:
        # ephemeral=True คือส่งข้อความที่เห็นแค่คนกดคนเดียว จะได้ไม่รกแชท
        await interaction.response.send_message("❌ ขออภัยครับ คุณไม่สามารถใช้คำสั่งนี้ได้ (เฉพาะแอดมินเท่านั้น)", ephemeral=True)
        return

    # --- ส่วนนี้จะทำงานเฉพาะ "แอดมิน" เท่านั้น ---
    try:
        channel = await interaction.guild.create_voice_channel(name="🎲 สุ่มห้องลง")
        random_trigger_channel_id = channel.id
        await interaction.response.send_message(f"✅ สร้างห้อง {channel.mention} สำเร็จแล้ว!", ephemeral=True)
        print(f"📢 แอดมิน {interaction.user.name} สร้างห้องสุ่มใหม่")
    except Exception as e:
        await interaction.response.send_message(f"❌ เกิดข้อผิดพลาด: {e}", ephemeral=True)

# --- 3. ระบบสุ่มย้าย (คนทั่วไปเดินเข้าห้องแล้วเด้งสุ่มได้ปกติ) ---
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
                print(f"❌ ย้ายไม่ได้: {e}")

if TOKEN:
    bot.run(TOKEN)