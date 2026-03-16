import discord
import random
import os
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

# --- 1. โหลดค่าจากไฟล์ความลับ .env ---
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

class MyBot(commands.Bot):
    def __init__(self):
        # ตั้งค่า Intents ให้บอทมองเห็นสมาชิกและสถานะห้องเสียง
        intents = discord.Intents.default()
        intents.voice_states = True
        intents.guilds = True
        intents.members = True
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    # ฟังก์ชันเชื่อมต่อคำสั่ง Slash (/)
    async def setup_hook(self):
        try:
            synced = await self.tree.sync()
            print(f"✅ ซิงค์คำสั่ง Slash เรียบร้อย! ({len(synced)} คำสั่ง)")
        except Exception as e:
            print(f"❌ Sync Error: {e}")

bot = MyBot()
random_trigger_channel_id = None # ตัวแปรเก็บ ID ห้องสุ่ม

@bot.event
async def on_ready():
    print(f"✅ บอท {bot.user} พร้อมทำงานแล้ว!")
    print(f"สถานะ: ผู้ดูแลระบบ (Administrator)")
    print("---------------------------------")

# --- 2. คำสั่งสร้างห้องสุ่ม (Slash Command) ---
@bot.tree.command(name="create_room", description="สร้างห้องสำหรับกดเพื่อสุ่มย้าย")
async def create_room(interaction: discord.Interaction):
    global random_trigger_channel_id
    try:
        # สร้างห้องเสียงใหม่
        channel = await interaction.guild.create_voice_channel(name="🎲 สุ่มห้องลง")
        random_trigger_channel_id = channel.id
        await interaction.response.send_message(f"✅ สร้างห้อง {channel.mention} สำเร็จ! (ลองกดเข้าเพื่อสุ่มได้เลย)", ephemeral=True)
        print(f"📢 สร้างห้องสุ่มใหม่ ID: {channel.id}")
    except Exception as e:
        await interaction.response.send_message(f"❌ สร้างห้องไม่ได้: {e}", ephemeral=True)

# --- 3. ระบบตรวจจับการเข้าห้องและสุ่มย้ายคน ---
@bot.event
async def on_voice_state_update(member, before, after):
    global random_trigger_channel_id
    
    # เช็กว่า: เข้าห้องสุ่มตรงกับ ID ที่สร้าง + ไม่ใช่บอท
    if after.channel and after.channel.id == random_trigger_channel_id and not member.bot:
        
        # กรองหาห้องปลายทางที่: ไม่ใช่ห้องสุ่ม และ ห้องยังไม่เต็ม (User Limit)
        all_channels = [
            vc for vc in member.guild.voice_channels 
            if vc.id != random_trigger_channel_id and (vc.user_limit == 0 or len(vc.members) < vc.user_limit)
        ]
        
        if all_channels:
            target = random.choice(all_channels)
            try:
                # สั่งย้ายสมาชิกไปห้องใหม่
                await member.move_to(target)
                
                # ส่งข้อความไปยังแชทของห้องเสียงปลายทาง
                # ใช้ member.name เพื่อดึงชื่อบัญชีดิสคอร์ดตามที่ขอมาครับ
                message = f"ผู้ใช้บัญชีชื่อ **{member.name}** นี้สุ่มห้องมา"
                await target.send(message)
                
                print(f"🎲 [สุ่มสำเร็จ] ย้ายคุณ {member.name} ไปยังห้อง {target.name}")
            except Exception as e:
                print(f"❌ เกิดข้อผิดพลาดในการย้ายหรือส่งข้อความ: {e}")
        else:
            print("⚠️ ไม่มีห้องปลายทางที่ว่างพอให้สุ่มไป!")

# --- 4. รันบอท ---
if TOKEN:
    bot.run(TOKEN)
else:
    print("❌ ERROR: หา TOKEN ไม่เจอ! ตรวจสอบไฟล์ .env ของคุณ (อย่าลืมกด Save ไฟล์ด้วย)")