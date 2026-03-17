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
        
        # --- [ชั่วคราว] ปิดการเช็กยศเพื่อทดสอบระบบย้าย ---
        # (ถ้ามั่นใจเรื่องยศแล้วค่อยกลับมาเปิดครับ)

        available = []
        all_voice_channels = member.guild.voice_channels
        
        for vc in all_voice_channels:
            # เงื่อนไข: ไม่ใช่ห้องสุ่มเอง และ ต้องมีคนอื่นนั่งอยู่
            if vc.id not in [normal_id, online_trigger_id] and len(vc.members) > 0:
                
                # เช็กสิทธิ์บอทแบบพื้นฐานที่สุด
                bot_perms = vc.permissions_for(member.guild.me)
                if bot_perms.view_channel and bot_perms.connect:
                    # เช็กว่าห้องไม่เต็ม
                    if vc.user_limit == 0 or len(vc.members) < vc.user_limit:
                        available.append(vc)

        # ดูใน Logs ของ Render ว่าบอทเจอห้องกี่ห้อง
        print(f"DEBUG: เจอห้องที่มีคนและบอทเข้าได้ทั้งหมด {len(available)} ห้อง")

        if available:
            target = random.choice(available)
            try:
                await member.move_to(target)
                await target.send(f"ผู้ใช้ชื่อ **{member.name}** สุ่มมาหาเพื่อนที่ห้องนี้ครับ!")
            except Exception as e:
                print(f"❌ ย้ายไม่ได้: {e}")
        else:
            # ถ้ายังหาไม่เจอ อย่าเพิ่งเตะออก ให้แค่ Print บอกใน Logs
            print(f"⚠️ {member.name} โดดลงห้องสุ่ม แต่บอทหาห้องที่มีคนออนไลน์ไม่เจอเลย")
            # await member.move_to(None) # ปิดไว้ก่อน จะได้ไม่โดนเตะมั่ว