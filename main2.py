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
            await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)

async def handle_online_random(member, after, normal_id):
    global online_trigger_id
    
    if after.channel and after.channel.id == online_trigger_id and not member.bot:
        available = []
        for vc in member.guild.voice_channels:
            if vc.id not in [normal_id, online_trigger_id] and len(vc.members) > 0:
                user_perms = vc.permissions_for(member)
                bot_perms = vc.permissions_for(member.guild.me)

                if user_perms.view_channel and user_perms.connect and bot_perms.view_channel:
                    if vc.user_limit == 0 or len(vc.members) < vc.user_limit:
                        available.append(vc)

        if available:
            target = random.choice(available)
            try:
                await member.move_to(target)
                # 📢 ส่งข้อความเข้าแชทของห้องเสียงที่สุ่มได้ (Voice Chat)
                await target.send(f"ผู้ใช้บัญชีชื่อ **{member.display_name}** สุ่มหาเพื่อนและลงมาที่นี่ครับ")
            except:
                pass
        else:
            try:
                # ถ้าหาไม่เจอ บอกในแชทห้องต้นทาง
                await after.channel.send(f"⚠️ **{member.display_name}** ไม่พบห้องที่มีคนออนไลน์ครับ")
            except:
                pass