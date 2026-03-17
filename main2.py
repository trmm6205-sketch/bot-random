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
        
        # --- 1. เช็กยศคนใช้งาน (เปลี่ยน 'Member' เป็นชื่อยศในเซิร์ฟนาย) ---
        allowed_role = discord.utils.get(member.roles, name="Member") 
        
        if not allowed_role:
            try:
                await member.move_to(None)
                print(f"🚫 เตะ {member.name} เพราะไม่มียศที่กำหนด")
                return
            except: return

        # --- 2. คัดกรองห้อง (เช็กสิทธิ์แบบละเอียด) ---
        available = []
        for vc in member.guild.voice_channels:
            # ไม่ใช่ห้องสุ่มเอง และต้องมีคนออนอยู่
            if vc.id not in [normal_id, online_trigger_id] and len(vc.members) > 0:
                # ห้องต้องไม่เต็ม
                if vc.user_limit == 0 or len(vc.members) < vc.user_limit:
                    
                    # เช็กว่า "บอท" และ "User" มองเห็นและเข้าห้องนั้นได้จริงไหม
                    bot_perms = vc.permissions_for(member.guild.me)
                    user_perms = vc.permissions_for(member)
                    
                    if bot_perms.connect and bot_perms.view_channel and user_perms.connect:
                        available.append(vc)
        
        # --- 3. ดำเนินการย้ายหรือเตะออก ---
        if available:
            target = random.choice(available)
            try:
                await member.move_to(target)
                await target.send(f"ผู้ใช้ชื่อ **{member.name}** สุ่มมาหาเพื่อนที่ห้องนี้ครับ!")
            except: pass
        else:
            try:
                await member.move_to(None)
                print(f"⚠️ เตะ {member.name} เพราะหาห้องที่มีคนออนไม่เจอ (หรือบอทไม่มีสิทธิ์เข้า)")
            except: pass