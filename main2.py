import discord
import random
from discord import app_commands

online_trigger_id = None

def setup_online_commands(tree: app_commands.CommandTree):
    @tree.command(name="create_room_online", description="สร้างห้องสุ่มหาเพื่อนที่มีคนอยู่")
    async def create_room_online(interaction: discord.Interaction):
        global online_trigger_id
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ เฉพาะแอดมินเท่านั้น", ephemeral=True)
            return
        try:
            channel = await interaction.guild.create_voice_channel(name="🎲 สุ่มไปหาเพื่อน")
            online_trigger_id = channel.id
            await interaction.response.send_message(f"✅ สร้างห้อง {channel.mention} สำเร็จ!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ เกิดข้อผิดพลาด: {e}", ephemeral=True)

async def handle_online_random(member, after, normal_id):
    global online_trigger_id
    if after.channel and after.channel.id == online_trigger_id and not member.bot:
        
        # ค้นหาห้องทั้งหมดในเซิร์ฟเวอร์
        available = []
        for vc in member.guild.voice_channels:
            # เงื่อนไข: ไม่ใช่ห้องสุ่มเอง และ ต้องมีคนอื่นนั่งอยู่ (len > 0)
            if vc.id not in [normal_id, online_trigger_id] and len(vc.members) > 0:
                # เช็กสิทธิ์บอท: บอทต้อง "มองเห็น" และ "เข้าได้"
                bot_perms = vc.permissions_for(member.guild.me)
                if bot_perms.view_channel and bot_perms.connect:
                    # เช็กว่าห้องไม่เต็ม
                    if vc.user_limit == 0 or len(vc.members) < vc.user_limit:
                        available.append(vc)

        # รายงานจำนวนห้องที่บอท 'มองเห็น' ลงใน Render Log
        print(f"DEBUG: บอทมองเห็นห้องที่มีคนอยู่ {len(available)} ห้อง")

        if available:
            target = random.choice(available)
            try:
                await member.move_to(target)
                await target.send(f"ผู้ใช้ชื่อ **{member.name}** สุ่มมาหาเพื่อนที่ห้องนี้ครับ!")
            except Exception as e:
                print(f"❌ ย้ายไม่ได้: {e}")
        else:
            # ถ้ามันยังเตะออก แสดงว่า available เป็น 0 (บอทมองไม่เห็นห้องที่มีคน)
            print(f"⚠️ หาห้องที่มีคนออนไม่เจอ (หรือบอทมองไม่เห็น) บอทจะยังไม่เตะเพื่อให้คุณตรวจสอบ")
            # await member.move_to(None) # ปิดการเตะไว้ก่อนเพื่อทดสอบ