import discord
import random

# ตัวแปรเก็บ ID ห้องสำหรับสุ่มหาเพื่อน (Online Only)
random_online_channel_id = None

# --- 1. ฟังก์ชันสร้างห้อง (เช็กสิทธิ์แอดมิน) ---
async def create_online_room_logic(interaction: discord.Interaction):
    global random_online_channel_id
    
    # ตรวจสอบสิทธิ์แอดมิน
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "❌ ขออภัยครับ คุณไม่สามารถใช้คำสั่งนี้ได้ (เฉพาะแอดมินเท่านั้น)", 
            ephemeral=True
        )
        return

    try:
        channel = await interaction.guild.create_voice_channel(name="🎲 สุ่มไปหาเพื่อน")
        random_online_channel_id = channel.id
        await interaction.response.send_message(f"✅ สร้างห้อง {channel.mention} (สุ่มหาห้องที่มีคน) สำเร็จ!", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ เกิดข้อผิดพลาด: {e}", ephemeral=True)

# --- 2. ฟังก์ชันหลักสำหรับจัดการการย้าย ---
async def handle_online_random(member, after, normal_id):
    global random_online_channel_id
    
    # ตรวจสอบว่าเข้าห้องสุ่มหาเพื่อนหรือไม่ และไม่ใช่บอท
    if after.channel and after.channel.id == random_online_channel_id and not member.bot:
        
        # 🎯 ค้นหาห้องที่มีคนอยู่ (Online) และต้องไม่เต็ม
        available_channels = [
            vc for vc in member.guild.voice_channels 
            if vc.id not in [normal_id, random_online_channel_id] 
            and len(vc.members) > 0 # มีคนอยู่
            and (vc.user_limit == 0 or len(vc.members) < vc.user_limit) # ห้องไม่เต็ม
        ]
        
        # ถ้าไม่มีใครออนเลย ให้หาห้องว่างทั่วไป (ระบบสำรอง)
        if not available_channels:
            available_channels = [
                vc for vc in member.guild.voice_channels 
                if vc.id not in [normal_id, random_online_channel_id]
                and (vc.user_limit == 0 or len(vc.members) < vc.user_limit)
            ]

        # --- ส่วนการย้ายและการแจ้งเตือน ---
        if available_channels:
            target = random.choice(available_channels)
            try:
                await member.move_to(target)
                
                # ✅ ส่งข้อความแจ้งเตือนเหมือน main.py (แท็กชื่อและบอกห้องที่ลง)
                message = f"ผู้ใช้บัญชีชื่อ **{member.name}** สุ่มมาหาเพื่อนที่ห้องนี้ครับ!"
                await target.send(message)
                
            except Exception as e:
                print(f"❌ ย้ายไม่ได้: {e}")
        else:
            # 🛑 กรณีห้องในเซิร์ฟเต็มหมดจริงๆ
            try:
                await member.move_to(None) # เตะออกจากห้องเสียง
                
                # แจ้งเตือนในห้องที่เขาพยายามจะเข้า (ถ้าทำได้) หรือส่ง Log
                print(f"⚠️ เตะ {member.name} ออกจากเขมรคลับชั่วคราวเนื่องจากห้องเต็ม")
                
                # หากนายมีห้องแชทหลัก ให้ใส่ ID ห้องตรงนี้เพื่อส่งข้อความด่าได้ครับ
                # channel = member.guild.get_channel(ใส่_ID_ห้องแชท_ที่นี่)
                # await channel.send(f"⚠️ {member.mention} ห้องเต็มทุกห้องเลย ผมจำเป็นต้องเตะออกครับ!")
                
            except Exception as e:
                print(f"❌ Error Kicking: {e}")