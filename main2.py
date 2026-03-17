import discord
import random

# ตัวแปรเก็บ ID ห้องสำหรับสุ่มหาเพื่อน (Online Only)
random_online_channel_id = None

# ฟังก์ชันสำหรับสร้างห้องสุ่มหาเพื่อน (เช็กสิทธิ์แอดมิน)
async def create_online_room_logic(interaction: discord.Interaction):
    global random_online_channel_id
    
    # 🚨 ตรวจสอบสิทธิ์แอดมิน (เหมือน main.py)
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "❌ ขออภัยครับ คุณไม่สามารถใช้คำสั่งนี้ได้ (เฉพาะผู้ดูแลระบบที่มีสิทธิ์แอดมินเท่านั้น)", 
            ephemeral=True
        )
        return

    try:
        channel = await interaction.guild.create_voice_channel(name="🎲 สุ่มไปหาเพื่อน")
        random_online_channel_id = channel.id
        await interaction.response.send_message(f"✅ สร้างห้อง {channel.mention} (แบบหาห้องที่มีคน) สำเร็จ!", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ เกิดข้อผิดพลาด: {e}", ephemeral=True)

# ฟังก์ชันจัดการการย้าย (Logic หลัก)
async def handle_online_random(member, after, normal_id):
    global random_online_channel_id
    
    # เช็กว่าเข้าห้องสุ่มหาเพื่อนหรือไม่
    if after.channel and after.channel.id == random_online_channel_id and not member.bot:
        
        # 🎯 หาห้องที่มีคนอยู่ และห้องไม่เต็ม
        available_channels = [
            vc for vc in member.guild.voice_channels 
            if vc.id not in [normal_id, random_online_channel_id] 
            and len(vc.members) > 0 
            and (vc.user_limit == 0 or len(vc.members) < vc.user_limit)
        ]
        
        # ถ้าไม่มีห้องที่มีคนอยู่เลย ให้หาห้องที่ว่าง (แบบสุ่มปกติ)
        if not available_channels:
            available_channels = [
                vc for vc in member.guild.voice_channels 
                if vc.id not in [normal_id, random_online_channel_id]
                and (vc.user_limit == 0 or len(vc.members) < vc.user_limit)
            ]

        if available_channels:
            target = random.choice(available_channels)
            try:
                await member.move_to(target)
                # แจ้งเตือนเพื่อนในห้องนั้น
                await target.send(f"ยินดีต้อนรับ {member.mention} สุ่มหาเพื่อนจนเจอแล้วครับ!")
            except:
                pass
        else:
            # 🛑 กรณีเต็มทุกห้องจริงๆ ให้เตะออกและแจ้งเตือน
            try:
                # พยายามหาห้องแชทเพื่อส่งข้อความแจ้งเตือน (ใช้ห้องระบบหรือห้องที่บอทส่งได้)
                # ในที่นี้เราส่งข้อความไปหาคนนั้นโดยตรงหรือส่งในห้องที่เขากำลังจะเข้า
                await member.move_to(None) # เตะออก
                print(f"เตะ {member.name} ออกเนื่องจากห้องเต็ม")
                
                # ถ้ามี Text Channel ที่ชื่อ 'แชทสุ่ม' หรือใกล้เคียง นายสามารถระบุเพิ่มได้ครับ
            except Exception as e:
                print(f"Error kicking: {e}")