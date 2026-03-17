import discord
import random
from discord import app_commands

# ตัวแปรเก็บไอดีห้องสุ่มหาเพื่อน
online_trigger_id = None

def setup_online_commands(tree: app_commands.CommandTree):
    @tree.command(name="create_room_online", description="สร้างห้องสุ่มหาเพื่อนที่มีคนอยู่")
    async def create_room_online(interaction: discord.Interaction):
        global online_trigger_id
        # เช็กสิทธิ์แอดมินก่อนสร้างห้อง
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ เฉพาะแอดมินเท่านั้น", ephemeral=True)
            return
        try:
            # สร้างห้องเสียงสำหรับสุ่มไปหาเพื่อน
            channel = await interaction.guild.create_voice_channel(name="🎲 สุ่มไปหาเพื่อน")
            online_trigger_id = channel.id
            await interaction.response.send_message(f"✅ สร้างห้อง {channel.mention} สำเร็จ! (แจ้งเตือนในแชทห้องเสียง)", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)

async def handle_online_random(member, after, normal_id):
    global online_trigger_id
    
    # ทำงานเมื่อสมาชิกกระโดดเข้าห้องสุ่มหาเพื่อน และไม่ใช่บอท
    if after.channel and after.channel.id == online_trigger_id and not member.bot:
        available = []
        for vc in member.guild.voice_channels:
            # เงื่อนไข: ไม่ใช่ห้องสุ่มเอง และต้องมีคนอยู่ในห้องนั้นอย่างน้อย 1 คน
            if vc.id not in [normal_id, online_trigger_id] and len(vc.members) > 0:
                user_perms = vc.permissions_for(member)
                bot_perms = vc.permissions_for(member.guild.me)
                # เช็กสิทธิ์การเข้าถึงห้อง
                if user_perms.view_channel and user_perms.connect and bot_perms.view_channel:
                    # เช็กว่าห้องเต็มหรือยัง
                    if vc.user_limit == 0 or len(vc.members) < vc.user_limit:
                        available.append(vc)

        if available:
            target = random.choice(available)
            try:
                # ย้ายสมาชิกไปยังห้องที่สุ่มได้
                await member.move_to(target)
                # 📢 หัวใจสำคัญ: ส่งข้อความแจ้งเตือนเข้า "แชทของห้องเสียง" นั้นๆ
                await target.send(f"ผู้ใช้บัญชีชื่อ **{member.display_name}** ได้ทำการสุ่มหาเพื่อนมาครับ")
            except: 
                pass
        else:
            # กรณีไม่มีใครออนไลน์ในห้องอื่นเลย ให้แจ้งเตือนในแชทห้องสุ่มนั้นเอง
            try:
                await after.channel.send(f"⚠️ **{member.display_name}** ไม่พบห้องที่มีคนออนไลน์ครับ")
            except: 
                pass