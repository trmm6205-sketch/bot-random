import discord
import random
from discord import app_commands

# ตัวแปรเก็บ ID ห้องสุ่มหาคนออน
online_trigger_id = None

# ฟังก์ชันเพิ่มคำสั่งเข้าไปในบอทหลัก
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

# ฟังก์ชันจัดการการย้าย (เรียกใช้จาก main.py)
async def handle_online_random(member, after, normal_id):
    global online_trigger_id
    if after.channel and after.channel.id == online_trigger_id and not member.bot:
        # หาห้องที่มีคนออนและไม่เต็ม
        available = [
            vc for vc in member.guild.voice_channels 
            if vc.id not in [normal_id, online_trigger_id] 
            and len(vc.members) > 0 
            and (vc.user_limit == 0 or len(vc.members) < vc.user_limit)
        ]
        
        # ถ้าไม่มีคนออนเลย ให้สุ่มห้องว่างแทน
        if not available:
            available = [
                vc for vc in member.guild.voice_channels 
                if vc.id not in [normal_id, online_trigger_id]
                and (vc.user_limit == 0 or len(vc.members) < vc.user_limit)
            ]

        if available:
            target = random.choice(available)
            try:
                await member.move_to(target)
                await target.send(f"ผู้ใช้บัญชีชื่อ **{member.name}** สุ่มมาหาเพื่อนที่ห้องนี้ครับ!")
            except:
                pass