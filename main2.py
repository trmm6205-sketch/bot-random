import discord
import random
from discord import app_commands

# ตัวแปรจำ ID ห้อง
online_trigger_id = None

def setup_online_commands(tree: app_commands.CommandTree):
    @tree.command(name="create_room_online", description="สร้างห้องสุ่มหาเพื่อนที่มีคนอยู่")
    async def create_room_online(interaction: discord.Interaction):
        global online_trigger_id
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ เฉพาะแอดมินเท่านั้น", ephemeral=True)
            return
        try:
            # สร้างห้องเสียงใหม่
            channel = await interaction.guild.create_voice_channel(name="🎲 สุ่มไปหาเพื่อน")
            online_trigger_id = channel.id
            await interaction.response.send_message(f"✅ สร้างห้อง {channel.mention} สำเร็จ!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ เกิดข้อผิดพลาด: {e}", ephemeral=True)

async def handle_online_random(member, after, normal_id):
    global online_trigger_id
    
    # ถ้ายังไม่ได้สร้างห้อง หรือ เข้าไม่ตรงห้อง ให้หยุดทำงานทันที (ไม่เตะ)
    if online_trigger_id is None or (after.channel and after.channel.id != online_trigger_id):
        return

    if after.channel and after.channel.id == online_trigger_id and not member.bot:
        print(f"🔍 {member.name} กำลังหาเพื่อนสุ่ม...")

        available = []
        for vc in member.guild.voice_channels:
            # เงื่อนไข: ไม่ใช่ห้องสุ่มเอง และ ต้องมีคนอื่นนั่งอยู่
            if vc.id not in [normal_id, online_trigger_id] and len(vc.members) > 0:
                
                # เช็กสิทธิ์ User (ห้ามมุดเข้าห้องที่เขาไม่มีสิทธิ์เข้า)
                user_perms = vc.permissions_for(member)
                # เช็กสิทธิ์บอท (บอทต้องมองเห็นห้องนั้น)
                bot_perms = vc.permissions_for(member.guild.me)

                if user_perms.connect and user_perms.view_channel and bot_perms.view_channel:
                    # ถ้าห้องไม่เต็ม ให้เพิ่มเข้าลิสต์
                    if vc.user_limit == 0 or len(vc.members) < vc.user_limit:
                        available.append(vc)

        # --- ส่วนการตัดสินใจย้าย ---
        if available:
            target = random.choice(available)
            try:
                await member.move_to(target)
                print(f"✅ ย้าย {member.name} ไปหาเพื่อนสำเร็จ")
            except Exception as e:
                print(f"❌ ย้ายไม่ได้: {e}")
        else:
            # 🕊️ ถ้าหาห้องไม่ได้ บอทจะนิ่งเฉย ปล่อยให้ User อยู่ในห้องเดิม (ไม่เตะออก!)
            print(f"ℹ️ ไม่พบห้องที่เหมาะสมสำหรับ {member.name} (ปล่อยให้อยู่ในห้องเดิม)")