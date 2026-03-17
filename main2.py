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
        
        print(f"🔍 {member.name} กำลังหาเพื่อนสุ่ม...")

        available = []
        for vc in member.guild.voice_channels:
            # เงื่อนไขหลัก: 
            # 1. ไม่ใช่ห้องสุ่มเอง 
            # 2. ต้องมีคนออนอยู่ 
            # 3. ห้องต้องไม่เต็ม
            if vc.id not in [normal_id, online_trigger_id] and len(vc.members) > 0:
                if vc.user_limit == 0 or len(vc.members) < vc.user_limit:
                    
                    # --- 🛡️ ระบบกันห้องล็อค (สำคัญมาก) ---
                    # เช็กว่า "User คนที่สุ่ม" มีสิทธิ์ Connect (เข้า) และ View (เห็น) ห้องนั้นหรือไม่
                    user_perms = vc.permissions_for(member)
                    
                    # เช็กสิทธิ์ของ "บอท" ด้วย (ถ้าบอทมองไม่เห็นหรือเข้าไม่ได้ ก็จะย้ายไม่ได้)
                    bot_perms = vc.permissions_for(member.guild.me)

                    if user_perms.connect and user_perms.view_channel and bot_perms.view_channel:
                        available.append(vc)

        if available:
            target = random.choice(available)
            try:
                await member.move_to(target)
                print(f"✅ สุ่มสำเร็จ! ย้าย {member.name} ไปหาเพื่อนที่ห้อง {target.name}")
            except Exception as e:
                print(f"❌ ย้ายไม่ได้: {e}")
        else:
            # 🕊️ ไม่พบห้องที่เหมาะสม (ไม่มีคนออน/ห้องล็อคหมด) 
            # เราจะไม่สั่งเตะออก (member.move_to(None)) เพื่อให้เขาค้างอยู่ในห้องสุ่มได้ตามที่นายต้องการ
            print(f"ℹ️ ไม่พบห้องที่มีคนออนไลน์ที่ {member.name} สามารถเข้าได้ (ปล่อยให้อยู่ในห้องเดิม)")