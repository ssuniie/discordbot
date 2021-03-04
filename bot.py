import discord
from discord.ext import commands, tasks
from discord import Spotify

import time
import datetime
from datetime import datetime
from itertools import cycle

import pytz
from pytz import timezone

import random
import json
import praw

# ! Load secret/client_secret.json file
with open('secret/client_secret.json') as f:
    client_secret = json.load(f)

# ! Load secret/server_secret file
with open('secret/server_secret.json') as f:
    server_secret = json.load(f)

# ! Load secret/reddit_secret file
with open('secret/reddit_secret.json') as f:
    reddit_secret = json.load(f)

# * Import assets/client_playing.json file
with open('assets/client_playing.json') as f:
    client_playing = json.load(f)

# * Intents Settings
intents = discord.Intents.all()

# * Bot's Infomations
TOKEN = client_secret['client_token']
PASSWORD = client_secret['admin_password']
client = commands.Bot(
    command_prefix='.',
    intents=intents,
    case_insensitive=True
)
status = cycle(client_playing)
reddit = praw.Reddit(
    client_id=reddit_secret['client_id'],
    client_secret=reddit_secret['client_secret'],
    username=reddit_secret['username'],
    password=reddit_secret['password'],
    user_agent=reddit_secret['user_agent'],
    check_for_async=False
)

# * Remove Commands
client.remove_command('help')

# * Author's Informations
AUTHOR_ICON = 'https://i.ibb.co/tMbrntz/jang-wonyoung-nationality-cover2.jpg'

# * Server's Infomations
GUILD_ID = server_secret['GUILD_ID']
CHANNEL_ID = server_secret['CHANNEL_ID']

current_timezone_time = datetime.now()
on_ready_time = current_timezone_time.astimezone(
    timezone('Asia/Bangkok'))


# * When bot is online
@client.event
async def on_ready():
    guild = client.get_guild(GUILD_ID)
    channel = guild.get_channel(CHANNEL_ID)

    change_status.start()
    print('Client is online!')
    print(on_ready_time.strftime("%d/%m/%Y, %H:%M:%S"))

    embed = discord.Embed(
        title='Yeong Bot Reboot',
        description=(':warning: Yeong Bot rebooted at\n:clock1: `{}`'.format(
            on_ready_time.strftime("%d/%m/%Y, %H:%M:%S"))
        ),
        color=0xff0033
    )
    await channel.send(embed=embed)


# * Change status of client
@tasks.loop(seconds=180)
async def change_status():
    await client.change_presence(
        status=discord.Status.online,
        activity=discord.Activity(
            type=discord.ActivityType.listening,
            name=next(status)))


# * When users joined the server.
@client.event
async def on_member_join(member):
    guild = client.get_guild(GUILD_ID)
    channel = guild.get_channel(CHANNEL_ID)
    role = discord.utils.get(member.guild.roles, name="Citizen")

    # * datetime Infomations
    current_omj_timezone_time = datetime.now()
    new_omj_timezone_time = current_omj_timezone_time.astimezone(
        timezone('Asia/Bangkok'))

    embed_channel = discord.Embed(
        title="ยินดีต้อนรับ!",
        description=f"อันยองน้อง {member.mention}\n เข้ามาที่ร้านโกโก้ของน้องซันนร้าาา",
        color=0x90ee90
    )
    embed_channel.set_author(
        name="น้องหยอง", icon_url=AUTHOR_ICON)
    embed_channel.set_thumbnail(url=member.avatar_url)
    embed_channel.set_footer(
        text=member.name + " เข้ามาในร้านโกโก้ตอน " +
        new_omj_timezone_time.strftime("%d/%m/%Y, %H:%M")
    )

    embed_dm = discord.Embed(
        title="อันยองจ้า!",
        description=(f"นี่คือร้านโกโก้ของน้องซันเองจ้าาา\n"
                     f"ถ้าอยากให้น้องหยองช่วยอะไรก็พิมพ์ .help ได้เลยนร้าาาาา"),
        color=0xd9598c)
    embed_dm.set_author(
        name="น้องหยอง",
        icon_url=AUTHOR_ICON
    )
    embed_dm.set_footer(text="น้องได้เข้ามาในร้านโกโก้ตอน " +
                        new_omj_timezone_time.strftime("%d/%m/%Y, %H:%M")
                        )

    embed_dm_image = discord.Embed()
    embed_dm_image.set_image(
        url='https://thumbs.gfycat.com/FarflungScaredDartfrog-size_restricted.gif')

    # ! This is important!,
    # ! do not !!forget!! this!,
    # ! Set This before send message.
    await client.wait_until_ready()

    await member.add_roles(role)
    await channel.send(embed=embed_channel)
    await member.send(embed=embed_dm)
    await member.send(embed=embed_dm_image)


# * When users left the server.
@client.event
async def on_member_remove(member):
    # * guild and channel Infomations
    guild = client.get_guild(GUILD_ID)
    channel = guild.get_channel(CHANNEL_ID)

    # * datetime Infomations
    current_omr_timezone_time = datetime.now()
    new_omr_timezone_time = current_omr_timezone_time.astimezone(
        timezone('Asia/Bangkok'))

    embed = discord.Embed(
        title="ลาก่อน...",
        description=f"{member.mention} ออกไปจากร้านโกโก้ของน้องซันแล้ว :crying_cat_face:",
        color=0xff0033
    )
    embed.set_author(
        name="น้องหยอง",
        icon_url=AUTHOR_ICON)
    embed.set_thumbnail(url=member.avatar_url)
    embed.set_footer(text=member.name + " ออกจากเซิฟไปตอน " +
                     new_omr_timezone_time.strftime("%d/%m/%Y, %H:%M"))

    # ! This is important!,
    # ! do not !!forget!! this!,
    # ! Set This before send message.
    await client.wait_until_ready()

    await channel.send(embed=embed)


# * When client joined the server.
@client.event
async def on_guild_join(guild):
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            await channel.send('เย้!! น้องหยองเข้ามาเป็นผู้ช่วยของเซิฟคุณแล้ว')
        break


# * When users send message (or something).
@client.event
async def on_message(message):
    sender = message.author
    text = message.content.lower().startswith

    # ? Check is sender = client?
    if sender == client.user:
        return

    # ? When users mention the client.
    if client.user.mentioned_in(message):
        if message.content.lower().startswith('.whois'):
            return
        else:
            await message.channel.send(
                f"น้อง {sender.display_name} เรียกน้องหยองหรอคะ?\n"
                + "สามารถเรียกน้องหยองได้โดยพิมพ์ .help ในช่องแชทเลย"
            )
            return
        return

    # ? When users type "ควย"
    kuy = ['kuy', 'ควย']
    for kuy in kuy:
        if kuy in message.content.lower():
            await message.channel.send("เป็นเหี้ยอะไรหล่ะ")
            return

    # ? If user type "เหี้ย"
    here = ['เชี่ย', 'เหี้ย', 'here']
    for here in here:
        if here in message.content.lower():
            here_msg = [
                'มีปัญหาหรอสัส!',
                'เป็นควยไรหล่ะ',
                'อยากมีปัญหาหรอวะ'
            ]
            rd = random.choice(here_msg)

            await message.channel.send(f'{rd}')
            return

    # ? If user type "เงียบ"
    if 'เงียบ' in message.content.lower():
        await message.channel.send(f"ก็กูอยากเงียบอ่ะ มีปัญหาหรอวะ แน่จริง 1-1 หลังเซเว่นปิดดิ {sender.mention}")
        return

    # ? If user type "sundick"
    sundick = ['sundick', 'ซันดิ้ก']
    for sundick in sundick:
        if sundick in message.content.lower():
            rd = random.randint(1, 3)

            if rd < 3:
                counting = int()
                crit_rd = random.randint(1, 4)

                await sender.edit(mute=True, deafen=True)

                if crit_rd == 1:
                    timer = int(12)
                    pass
                else:
                    timer = int(6)
                    pass

                if timer == 6:
                    await message.channel.send(
                        f"น้อง {sender.display_name} โดนปิดไมค์ไป `{timer}` วินาที"
                    )
                else:
                    await message.channel.send(
                        f":crossed_swords: `ติดคริติคอล` **200%**\n"
                        + f"น้อง {sender.display_name} โดนปิดไมค์ไป `{timer}` วินาที"
                    )

                for _ in range(timer):
                    counting += 1
                    time.sleep(1)

                    while counting >= timer:
                        await sender.edit(mute=False, deafen=False)
                        break

            elif rd == 3:
                await message.channel.send(f"น้อง {sender.mention} โชคดีที่ไม่โดนปิดไมค์ไปนะ "
                                           + "แต่ครั้งหน้าก็ระวังไว้ด้วยละกันหล่ะ")
            return

    await client.process_commands(message)


# * When users uses command (.help)
@client.command()
async def help(ctx, arg=None):
    if arg == None:
        embed = discord.Embed(title="คำสั่งทั้งหมด ขึ้นต้นด้วย .",
                              color=0xd9598c)
        embed.set_author(name="น้องหยอง",
                         icon_url=AUTHOR_ICON)
        embed.add_field(name="help",
                        value=f"แสดงหน้าต่างนี้ไง", inline=True)  # ? (.help)
        embed.add_field(name="whois <member>",
                        value="แสดงข้อมูลเกี่ยวกับคนในเซิฟเวอร์", inline=True)  # ? (.userinfo / .user)
        embed.add_field(name="spotify / listening <member>",
                        value="แสดงเพลงที่ member \nกำลังเล่นอยู่บน Spotify", inline=True)  # ? (.spotify / .listening)
        embed.add_field(name="call",
                        value="เรียกคนที่ต้องการเรียกหา", inline=True)  # ? (.call)
        embed.add_field(name="clock / time",
                        value="แสดงวันที่และเวลาในปัจจุบัน", inline=True)  # ? (.clock / .time)
        embed.add_field(name="ping",
                        value="ทดสอบการตอบกลับ", inline=True)  # ? (.ping)
        embed.add_field(name="hello / hi",
                        value="สวัสดีไงเพื่อนรัก", inline=True)  # ? (.hello / .hi)
        embed.add_field(name="send",
                        value="ขอให้บอทส่งอะไรสักอย่าง", inline=True)  # ? (.send <arg>)
        embed.add_field(name="mute / unmute",
                        value="ปิด/เปิดไมค์ทุกคนในห้องแชท (ยกเว้นบอท)", inline=True)  # ? (.mute / .unmute)

        await ctx.send(embed=embed)

    elif arg == 'mute':
        await ctx.send('คำสั่งคือ .mute จะเป็นการปิดไมค์ทั้งห้อง')

    elif arg == 'unmute':
        await ctx.send(
            'คำสั่งคือ `.unmute` จะเป็นการเปิดไมค์ทั้งห้อง\n'
            + 'คำสั่ง `.unmute me` จะเป็นการเปิดไมค์ของตัวเอง (ในกรณีโดน Server Mute อยู่)')


@client.command()
async def info(ctx):
    embed = discord.Embed(
        title='รายละเอียดของบอท',
        color=0xFCF694
    )
    embed.add_field(
        name='Last Restart',
        value=f'Date: `{on_ready_time.strftime("%d/%m/%Y")}`\n'
        + f'Time: `{on_ready_time.strftime("%H:%M:%S")}`'
    )
    embed.add_field(
        name='Ping Time',
        value=f'`{round(client.latency * 1000)}` ms'
    )

    await ctx.send(embed=embed)


# * When users uses command (.whois)
@client.command()
async def whois(ctx, *, member: discord.Member):
    if member != client.user:
        embed = discord.Embed(
            title=f"น้อง {member.name}",
            color=0xd9598c
        )
        embed.set_author(name="น้องหยอง", icon_url=AUTHOR_ICON)
        embed.add_field(name="ชื่อ", value=member.name, inline=True)
        embed.add_field(name="ชื่อที่แสดง",
                        value=member.display_name, inline=True)
        embed.add_field(name="วันที่สมัครไอดี",
                        value='{}'.format(
                            member.created_at.strftime("%d/%m/%Y")),
                        inline=False)
        embed.add_field(name="วันที่เข้ามาในร้าน",
                        value='{}'.format(
                            member.joined_at.strftime("%d/%m/%Y")),
                        inline=False)
        embed.add_field(name="ไอดี", value=member.id, inline=False)
        embed.set_footer(icon_url=ctx.author.avatar_url,
                         text="ขอดูประวัติโดย {}".format(ctx.author.name))
        embed.set_thumbnail(url=member.avatar_url)

    else:
        embed = discord.Embed(
            title="รายละเอียดของน้องหยอง",
            color=0xd9598c)
        embed.set_author(name="น้องหยอง",
                         icon_url=AUTHOR_ICON)
        embed.add_field(name="คนสร้างน้องหยอง", value="Sun#6284", inline=False)
        embed.add_field(name="สร้างไว้ทำอะไร ?",
                        value="ก็กูอยากสร้างอ่ะมีปัญหาอะไรไหม", inline=False)
        embed.set_image(
            url='https://thumbs.gfycat.com/PitifulSkinnyEuropeanpolecat-size_restricted.gif'
        )
        embed.set_thumbnail(url=client.user.avatar_url)

    await ctx.send(embed=embed)


# * When users uses command (.spotify / .listening)
@client.command(aliases=['listening'])
async def spotify(ctx, user: discord.Member = None):
    # ? If users did not put <username> argument,
    # ? user will be sender (ctx.author)
    if user == None:
        user = ctx.author
        pass

    if user.activities:
        for activity in user.activities:
            if isinstance(activity, Spotify):
                aca_timezone_time = activity.created_at
                aca_new_timezone_time = aca_timezone_time.astimezone(
                    timezone('Asia/Bangkok'))

                spotify_icon = 'https://i.pinimg.com/originals/83/3c/f5/833cf5fe43f8c92c1fcb85a68b29e585.png'

                m1, s1 = divmod(int(activity.duration.seconds), 60)

                # ? if second is odd number (0-9)
                if s1 < 10:
                    song_length = f'{m1}:0{s1}'
                    pass
                else:
                    song_length = f'{m1}:{s1}'
                    pass

                embed = discord.Embed(
                    title=f"น้อง {user.display_name} กำลังฟังเพลงอะไรอยู่กันนะ? :thinking:",
                    description=":musical_note: **น้อง `{}` กำลังฟัง {}**".format(
                        user.display_name,
                        f"[{activity.title}](https://open.spotify.com/track/{activity.track_id})"
                    ),
                    color=activity.color
                )
                embed.set_author(name="Spotfiy", icon_url=spotify_icon)
                embed.set_thumbnail(url=activity.album_cover_url)
                embed.add_field(name="ชื่อเพลง", value=activity.title)
                embed.add_field(name="ศิลปิน", value=activity.artist)
                embed.add_field(
                    name="อัลบั้ม", value=activity.album, inline=False)
                embed.add_field(
                    name="ระยะเวลา",
                    value=f"{song_length}",
                    inline=True
                )
                embed.set_footer(
                    icon_url=user.avatar_url,
                    text=(
                        "{} เริ่มฟังตอน {} UTC".format(
                            user.name,
                            aca_new_timezone_time.strftime("%H:%M")
                        )
                    )
                )

                await ctx.send(embed=embed)
    else:
        await ctx.send(f'ดูเหมือนว่า {user.name} จะไม่ได้ทำอะไรอยู่นะ')


# * When user use command (.call)
# TODO: User can multiple call in one command
@client.command()
async def call(ctx, user: discord.Member = None):
    if user == None:  # ? user = None (.call)
        await ctx.send("ถ้าต้องการเรียกใครมาตอบให้พิม .call <username> นะคะ")

    elif ctx.author != user:  # ? user != sender
        call_msg = [
            f"**{ctx.author.mention}** เรียกคุณที่ `{ctx.guild.name}`, "
            + f"{ctx.channel.mention} ค่ะ โปรดมาตอบกลับด้วย",
            f"ฮัลโหล... อยู่รึปล่าว, มีคนเรียกแกอ่ะ ลองมาดูที่ {ctx.channel.mention} ดูดิ"
        ]
        call_rd = random.choice(call_msg)

        await user.send(call_msg)

    else:  # user = sender
        embed = discord.Embed()
        embed.set_image(
            url='https://media1.tenor.com/images/75eb5955851b1daebd1af193e2d76019/tenor.gif?itemid=12319210'
        )

        await ctx.send(f"คุณไม่สามารถเรียกตัวเองได้นะคะ")
        await ctx.send(embed=embed)


# * When users uses command (.ping)
@client.command()
async def ping(ctx):
    message = await ctx.send('*Pinging...*')
    time.sleep(1)
    await message.edit(
        content=f":ping_pong: {round(client.latency * 1000)}ms"
    )


# * When users uses command (.hello)
@client.command(aliases=['hi'])
async def hello(ctx):
    hello_msg = [
        f'สวัสดีจ้า {ctx.author.mention}',
        f'สวัสดี, {ctx.author.mention}',
        f'Hello {ctx.author.mention}',
        f'Hello, World',
        f'你好！{ctx.author.mention}'
    ]
    await ctx.send(f"> {random.choice(hello_msg)}")


# * When users use command (.clock)
@client.command(aliases=['time'])
async def clock(ctx):
    # * datetime Infomations
    clock_current_timezone_time = datetime.now()
    new_clock_timezone_time = clock_current_timezone_time.astimezone(
        timezone('Asia/Bangkok'))

    embed = discord.Embed(
        title="ตอนนี้เป็นเวลา",
        description=":calendar_spiral: {}\n:alarm_clock: {}".format(
            new_clock_timezone_time.strftime("%d/%m/%Y"),
            new_clock_timezone_time.strftime("%H:%M:%S")),
        color=0xff7326)

    await ctx.send(embed=embed)


# * When users use command (.send)
@client.command()
async def send(ctx, arg1=None):
    # ? if arg1 is None (.send)
    if arg1 == None:
        embed = discord.Embed(title="คำสั่งหมวด send <arg>")
        embed.add_field(name="hug", value="ต้องการกอดหรอ?")
        embed.add_field(name="izone", value="IZ*ONE น้องหยองชอบมักๆ")
        embed.add_field(name="nude", value="ต้องการรูปสินะ... 555555")
        embed.add_field(name="quote", value="อยากได้คำคมหรอ?")
        embed.add_field(name="malee", value="แตกหนึ่ง! สวยพี่สวย!")

        await ctx.send(embed=embed)

    # ? If arg1 != None (.send <arg>)
    else:
        embed = discord.Embed()

        # ? If arg1 is hug (.send hug)
        if arg1 == 'hug':
            # * Import assets/hug.json file
            with open('assets/hug.json') as f:
                hug = json.load(f)

            hug_rd = random.choice(hug)

            embed.set_image(url=hug_rd)

        # ? If arg is izone (.send izone)
        elif arg1 == 'izone':
            # * Import assets/izone.json file
            with open('assets/izone.json') as f:
                izone = json.load(f)

            izone_rd = random.choice(izone)

            embed.set_image(url=izone_rd)

        # ? If arg is nude (.send nude)
        elif arg1 == 'nude':
            embed.set_image(
                url='https://i.makeagif.com/media/2-10-2021/g_z7xe.gif')

        # ? If arg is malee (.send malee)
        elif arg1 == 'malee':
            # * Import assets/malee.json file
            with open('assets/malee.json') as f:
                malee = json.load(f)

            malee_rd = random.choice(malee)

            embed.set_image(url=malee_rd)

        # ? If arg is quote (.send quote)
        elif arg1 == 'quote':
            # * Import assets/quote.json file
            with open('assets/quote.json', encoding='utf-8') as f:
                quote = json.load(f)

            quote_rd = random.choice(quote)

            await ctx.send(f'> *{quote_rd}*')
            return

        # ? If arg is video (.send video)
        elif arg1 == 'video':
            # * Import assets/video.json file
            with open('assets/video.json') as f:
                video = json.load(f)

            video_rd = random.choice(video)

            await ctx.send(video_rd)
            return

        # ? If arg is None of the above
        # ! Example (.send quoter)
        else:
            await ctx.send("พิมพ์ผิดป้ะเนี่ย! พิมพ์ให้ถูกหน่อยดิวะ")
            return

        await ctx.send(embed=embed)


'''
# * When users use command (.add)
# TODO: Make link dump to json file
# TODO: Make this on summer/closed semester.
@client.command()
async def add(ctx, arg1=None, arg2=None):
    if arg1 == None:
        await ctx.send('อยากเพิ่มอะไรลงในบอทหล่ะ')
    else:
        if arg1 == 'hug':
            if arg2 != None:
                with open('assets/hug.json', 'w') as f:
                    hug = json.load(f)
                json.dumps(arg2, hug)
                print('dump sucess!')
'''


# * When users use command (.list)
@client.command()
async def list(ctx):
    guild = client.get_guild(ctx.author.guild.id)

    total = len(guild.members)
    bot_total = 0
    user_total = 0

    for user in guild.members:
        if user.bot:
            bot_total += 1
        else:
            user_total += 1

    print(total, user_total, bot_total)
    await ctx.send(f'{guild.name} มีสมาชิกทั้งหมด {total} คน')


# * When users use command (.connect <password>)
# ! [need "ว่าที่โปรแกรมเมอร์" role]
@client.command(aliases=['join'])
@commands.has_role("ว่าที่โปรแกรมเมอร์")
async def connect(ctx, password_input=None):
    channel = client.get_channel(CHANNEL_ID)
    message = ctx.message
    password = PASSWORD

    if password_input == password:
        channel = ctx.author.voice.channel
        await channel.connect()
        await message.delete_message()
    else:
        print(f'{ctx.author.name} type wrong password (.connect)')
        await ctx.author.delete_message(message)


# * When users use command (.mute)
@client.command()
async def mute(ctx):
    channel = ctx.author.voice.channel

    for user in channel.members:
        if user.bot:
            await user.edit(mute=False)
        else:
            await user.edit(mute=True)

    await ctx.send(f'{ctx.author.name} ได้ทำการปิดไมค์ทุกคนในห้องแล้ว')


# * When users use command (.unmute)
@client.command()
async def unmute(ctx, onoff=None):
    channel = ctx.author.voice.channel
    if onoff == None:
        for member in channel.members:
            await member.edit(mute=False)
        await ctx.send(f'{ctx.author.name} ได้ทำการเปิดไมค์ทุกคนในห้องแล้ว')

    elif onoff == 'me':
        await ctx.author.edit(mute=False)


# * When users use command (.reddit <args>)
@client.command()
async def sendreddit(ctx, sreddit=None):
    for submission in reddit.subreddit(sreddit).new(limit=2):
        embed = discord.Embed(
            title=submission.title,
            description=submission.url)
        embed.set_image(url=submission.url)
        await ctx.send(embed=embed)


# * When users use command (.roll)
@client.command()
async def roll(ctx, num1: int = None, num2: int = None):
    if num1 == None:
        randnum = random.randint(1, 10)
        await ctx.send(f':roller_coaster: {ctx.author.name} สุ่มได้ {randnum} แต้ม (1-10)')

    elif num1 != None and num2 == None:
        randnum = random.randint(1, num1)
        await ctx.send(f':roller_coaster: {ctx.author.name} สุ่มได้ {randnum} แต้ม (1-{num1})')

    elif num1 != None and num2 != None:
        randnum = random.randint(num1, num2)
        await ctx.send(f':roller_coaster: {ctx.author.name} สุ่มได้ {randnum} แต้ม ({num1}-{num2})')


# * When users use command (.role)
@client.command()
@commands.has_permissions(administrator=True)
async def color(ctx, color=None):
    if color == None:
        return

    else:
        user = ctx.author
        role = discord.utils.get(user.guild.roles, name=color)

        if role in user.roles:
            await user.remove_roles(role)
            await ctx.send(f'{role.name} removed')

        else:
            await user.add_roles(role)
            await ctx.send(f'{role.name} added')


# ! Run / Required Token to run
client.run(TOKEN)