import discord
from discord import app_commands
from discord.ext import commands
import os
import datetime
import asyncio
from dotenv import load_dotenv

# تحميل المتغيرات البيئية
load_dotenv()

# إعداد البوت
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# حدث: البوت جاهز
@bot.event
async def on_ready():
    print(f'{bot.user} تم الاتصال بالديسكورد!')
    try:
        synced = await bot.tree.sync()
        print(f"تم مزامنة {len(synced)} أمر")
    except Exception as e:
        print(e)

# أمر: طرد عضو
@bot.tree.command(name="طرد", description="طرد عضو من السيرفر")
@app_commands.describe(member="العضو المراد طرده", reason="سبب الطرد")
@app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = None):
    try:
        await member.kick(reason=reason)
        embed = discord.Embed(
            title="تم طرد العضو",
            description=f"تم طرد {member.mention} من السيرفر.",
            color=discord.Color.red()
        )
        if reason:
            embed.add_field(name="السبب", value=reason)
        await interaction.response.send_message(embed=embed)
    except discord.Forbidden:
        await interaction.response.send_message("ليس لدي صلاحية لطرد الأعضاء!")

# أمر: حظر عضو
@bot.tree.command(name="حظر", description="حظر عضو من السيرفر")
@app_commands.describe(member="العضو المراد حظره", reason="سبب الحظر")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = None):
    try:
        await member.ban(reason=reason)
        embed = discord.Embed(
            title="تم حظر العضو",
            description=f"تم حظر {member.mention} من السيرفر.",
            color=discord.Color.dark_red()
        )
        if reason:
            embed.add_field(name="السبب", value=reason)
        await interaction.response.send_message(embed=embed)
    except discord.Forbidden:
        await interaction.response.send_message("ليس لدي صلاحية لحظر الأعضاء!")

# أمر: كتم عضو
@bot.tree.command(name="كتم", description="كتم عضو مؤقتاً")
@app_commands.describe(member="العضو المراد كتمه", duration="مدة الكتم بالدقائق", reason="سبب الكتم")
@app_commands.checks.has_permissions(manage_roles=True)
async def mute(interaction: discord.Interaction, member: discord.Member, duration: int, reason: str = None):
    try:
        muted_role = discord.utils.get(interaction.guild.roles, name="مكتوم")
        if not muted_role:
            muted_role = await interaction.guild.create_role(name="مكتوم")
            for channel in interaction.guild.channels:
                await channel.set_permissions(muted_role, speak=False, send_messages=False)

        await member.add_roles(muted_role)
        embed = discord.Embed(
            title="تم كتم العضو",
            description=f"تم كتم {member.mention} لمدة {duration} دقيقة.",
            color=discord.Color.orange()
        )
        if reason:
            embed.add_field(name="السبب", value=reason)
        await interaction.response.send_message(embed=embed)

        await asyncio.sleep(duration * 60)
        await member.remove_roles(muted_role)
        await interaction.channel.send(f"تم إلغاء كتم {member.mention}.")
    except discord.Forbidden:
        await interaction.response.send_message("ليس لدي صلاحية لكتم الأعضاء!")

# أمر: مسح الرسائل
@bot.tree.command(name="مسح", description="مسح عدد معين من الرسائل")
@app_commands.describe(amount="عدد الرسائل المراد مسحها")
@app_commands.checks.has_permissions(manage_messages=True)
async def clear(interaction: discord.Interaction, amount: int):
    try:
        await interaction.response.defer()
        await interaction.channel.purge(limit=amount)
        embed = discord.Embed(
            title="تم مسح الرسائل",
            description=f"تم مسح {amount} رسالة.",
            color=discord.Color.blue()
        )
        await interaction.followup.send(embed=embed, ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message("ليس لدي صلاحية لمسح الرسائل!")

# أمر: تحذير عضو
@bot.tree.command(name="تحذير", description="تحذير عضو")
@app_commands.describe(member="العضو المراد تحذيره", reason="سبب التحذير")
@app_commands.checks.has_permissions(manage_messages=True)
async def warn(interaction: discord.Interaction, member: discord.Member, reason: str = None):
    embed = discord.Embed(
        title="تم تحذير العضو",
        description=f"تم تحذير {member.mention}.",
        color=discord.Color.yellow()
    )
    if reason:
        embed.add_field(name="السبب", value=reason)
    await interaction.response.send_message(embed=embed)

# أمر: إضافة رتبة
@bot.tree.command(name="رتبة", description="إضافة رتبة لعضو")
@app_commands.describe(member="العضو المراد إضافة الرتبة له", role="الرتبة المراد إضافتها")
@app_commands.checks.has_permissions(manage_roles=True)
async def addrole(interaction: discord.Interaction, member: discord.Member, role: discord.Role):
    try:
        await member.add_roles(role)
        embed = discord.Embed(
            title="تم إضافة الرتبة",
            description=f"تم إضافة رتبة {role.mention} إلى {member.mention}",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)
    except discord.Forbidden:
        await interaction.response.send_message("ليس لدي صلاحية لإضافة الرتب!")

# أمر: إزالة رتبة
@bot.tree.command(name="نزع_رتبة", description="إزالة رتبة من عضو")
@app_commands.describe(member="العضو المراد إزالة الرتبة منه", role="الرتبة المراد إزالتها")
@app_commands.checks.has_permissions(manage_roles=True)
async def removerole(interaction: discord.Interaction, member: discord.Member, role: discord.Role):
    try:
        await member.remove_roles(role)
        embed = discord.Embed(
            title="تم إزالة الرتبة",
            description=f"تم إزالة رتبة {role.mention} من {member.mention}",
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed)
    except discord.Forbidden:
        await interaction.response.send_message("ليس لدي صلاحية لإزالة الرتب!")

# أمر: معلومات العضو
@bot.tree.command(name="معلومات", description="عرض معلومات العضو")
@app_commands.describe(member="العضو المراد عرض معلوماته")
async def userinfo(interaction: discord.Interaction, member: discord.Member = None):
    if member is None:
        member = interaction.user
    
    roles = [role.mention for role in member.roles[1:]]
    roles_str = " ".join(roles) if roles else "لا يوجد"
    
    embed = discord.Embed(
        title=f"معلومات {member.name}",
        color=member.color
    )
    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
    embed.add_field(name="الاسم", value=member.name, inline=True)
    embed.add_field(name="الآيدي", value=member.id, inline=True)
    embed.add_field(name="تاريخ الانضمام", value=member.joined_at.strftime("%Y-%m-%d"), inline=True)
    embed.add_field(name="تاريخ إنشاء الحساب", value=member.created_at.strftime("%Y-%m-%d"), inline=True)
    embed.add_field(name="الرتب", value=roles_str, inline=False)
    
    await interaction.response.send_message(embed=embed)

# أمر: معلومات السيرفر
@bot.tree.command(name="سيرفر", description="عرض معلومات السيرفر")
async def serverinfo(interaction: discord.Interaction):
    guild = interaction.guild
    embed = discord.Embed(
        title=f"معلومات سيرفر {guild.name}",
        color=discord.Color.blue()
    )
    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
    embed.add_field(name="عدد الأعضاء", value=guild.member_count, inline=True)
    embed.add_field(name="عدد الرتب", value=len(guild.roles), inline=True)
    embed.add_field(name="عدد القنوات", value=len(guild.channels), inline=True)
    embed.add_field(name="تاريخ الإنشاء", value=guild.created_at.strftime("%Y-%m-%d"), inline=True)
    embed.add_field(name="المالك", value=guild.owner.mention, inline=True)
    
    await interaction.response.send_message(embed=embed)

# أمر: قفل القناة
@bot.tree.command(name="قفل", description="قفل القناة الحالية")
@app_commands.checks.has_permissions(manage_channels=True)
async def lock(interaction: discord.Interaction):
    try:
        await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=False)
        embed = discord.Embed(
            title="تم قفل القناة",
            description=f"تم قفل القناة {interaction.channel.mention}",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)
    except discord.Forbidden:
        await interaction.response.send_message("ليس لدي صلاحية لقفل القناة!")

# أمر: فتح القناة
@bot.tree.command(name="فتح", description="فتح القناة الحالية")
@app_commands.checks.has_permissions(manage_channels=True)
async def unlock(interaction: discord.Interaction):
    try:
        await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=True)
        embed = discord.Embed(
            title="تم فتح القناة",
            description=f"تم فتح القناة {interaction.channel.mention}",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)
    except discord.Forbidden:
        await interaction.response.send_message("ليس لدي صلاحية لفتح القناة!")

# معالجة الأخطاء
@bot.event
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("ليس لديك صلاحية لاستخدام هذا الأمر!", ephemeral=True)
    elif isinstance(error, app_commands.MissingRequiredArgument):
        await interaction.response.send_message("الرجاء تقديم جميع المعلومات المطلوبة!", ephemeral=True)

# تشغيل البوت
bot.run(os.getenv('DISCORD_TOKEN')) 