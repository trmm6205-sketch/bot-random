import discord
import random
from discord import app_commands

# ตัวแปรเก็บ ID ห้องสุ่มหาคนออน
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
        
        # --- 1. เช็กยศคนใช้งาน (เปลี่ยนชื่อยศให้ตรงกับในเซิร์ฟนาย) ---
        allowed_role = discord.utils.get(member.roles, name="ชื่อยศที่ต้องการ") 
        
        if not allowed_role:
            try:
                await member.move_to(None)
                print(f"🚫 เตะ {member.name} เพราะไม่มียศที่กำหนด")
                return
            except:
                return

        # --- 2. คัดกรองห้องที่สุ่มไปได้ ---
        available = [
            vc for vc in member.guild.voice_channels 
            if vc.id not in [normal_id, online_trigger_id] 
            and len(vc.members) > 0  # ต้องมีคนออนอยู่
            and (vc.user_limit == 0 or len(vc.members) < vc.user_limit) # ห้องไม่เต็ม
            and vc.permissions_for(member).connect  # <--- นายต้องมีสิทธิ์เข้าได้
            and vc.permissions_for(member).view_channel # <--- นายต้องมองเห็นห้องนั้น
        ]
        
        # --- 3. ดำเนินการย้ายหรือเตะออก ---
        if available:
            target = random.choice(available)
            try:
                await member.move_to(target)
                await target.send(f"ผู้ใช้ชื่อ **{member.name}** สุ่มมาหาเพื่อนที่ห้องนี้ครับ!")
            except:
                pass
        else:
            # ถ้าหาห้องที่มีคนออนไม่ได้เลย หรือห้องที่มีคนดันล็อค/เต็มหมด ให้ดีดออก
            try:
                await member.move_to(None)
                print(f"⚠️ เตะ {member.name} เพราะไม่มีห้องที่เหมาะสม (ไม่มีคนออน/ห้องล็อค/ห้องเต็ม)")
            except:
                pass