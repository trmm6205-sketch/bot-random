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
        # 1. พยายามหาห้องที่มีคนออนอยู่ก่อน
        available = [
            vc for vc in member.guild.voice_channels 
            if vc.id not in [normal_id, online_trigger_id] 
            and len(vc.members) > 0 
            and (vc.user_limit == 0 or len(vc.members) < vc.user_limit)
        ]
        
        # 2. ถ้าเจอห้องที่มีคนออน ให้ย้ายไป
        if available:
            target = random.choice(available)
            try:
                await member.move_to(target)
                await target.send(f"ผู้ใช้ชื่อ **{member.name}** สุ่มมาหาเพื่อนที่ห้องนี้ครับ!")
            except:
                pass
        
        # 3. 🚨 ถ้าไม่มีคนออนเลย หรือห้องเต็มหมด (เตะออก)
        else:
            try:
                # ย้ายไปที่ None คือการเตะออกจากห้องเสียง
                await member.move_to(None)
                
                # ส่งข้อความเตือน (เลือกส่งไปใน DM ของคนนั้น หรือ Log ในเซิร์ฟ)
                print(f"⚠️ เตะ {member.name} เพราะไม่มีห้องที่มีคนออนไลน์")
                
                # ถ้าอยากให้บอทส่งข้อความบอกเขาในแชท ให้เปิดคอมเมนต์ด้านล่างนี้ครับ
                # await member.send("ขออภัยครับ ตอนนี้ไม่มีเพื่อนออนไลน์ในห้องอื่นเลย ผมจึงต้องเชิญคุณออกจากห้องสุ่มครับ")
            except Exception as e:
                print(f"❌ Kick Error: {e}")