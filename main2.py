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
    # เช็กว่าเข้าห้องสุ่มหาเพื่อนจริงไหม และไม่ใช่บอท
    if after.channel and after.channel.id == online_trigger_id and not member.bot:
        
        # --- 1. เช็กยศคนใช้งาน (ถ้ายังไม่ชัวร์เรื่องชื่อยศ ให้ปิดส่วนนี้ไปก่อนได้) ---
        # ตัวอย่าง: ถ้าไม่อยากล็อคยศ ให้ใส่เครื่องหมาย # ไว้หน้าบรรทัดด้านล่าง
        # allowed_role = discord.utils.get(member.roles, name="Member") 
        # if not allowed_role:
        #     try: await member.move_to(None); return
        #     except: return

        # --- 2. คัดกรองห้อง ---
        available = []
        for vc in member.guild.voice_channels:
            # เงื่อนไข: ไม่ใช่ห้องสุ่มเอง และ ต้องมีคนอื่นอยู่ (len > 0)
            if vc.id not in [normal_id, online_trigger_id] and len(vc.members) > 0:
                # เช็กว่าห้องไม่เต็ม
                if vc.user_limit == 0 or len(vc.members) < vc.user_limit:
                    
                    # เช็กสิทธิ์บอท (บอทต้องมองเห็นและเข้าได้)
                    bot_perms = vc.permissions_for(member.guild.me)
                    if bot_perms.view_channel and bot_perms.connect:
                        available.append(vc)
        
        # --- 3. การตัดสินใจ ---
        if available:
            target = random.choice(available)
            try:
                await member.move_to(target)
                await target.send(f"ผู้ใช้ชื่อ **{member.name}** สุ่มมาหาเพื่อนที่ห้องนี้ครับ!")
            except Exception as e:
                print(f"Error moving member: {e}")
        else:
            # 🚨 ถ้าหาห้องที่มีคนออนไม่เจอจริงๆ ให้ย้ายกลับไปห้องสุ่มปกติ หรือเตะออก
            try:
                # ผมแนะนำให้ลองเอา "เตะออก" ออกก่อน เพื่อทดสอบว่ามันหาห้องเจอไหม
                # await member.move_to(None) 
                print(f"⚠️ หาห้องที่มีคนออนไลน์ไม่เจอสำหรับ: {member.name}")
            except: pass