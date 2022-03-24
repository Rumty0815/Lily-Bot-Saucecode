import discord
import json

import asyncio
from discord.ext import commands
from discord import Message, Guild, TextChannel, Permissions
import Keep_alive
import random
import os
import urllib.error
import urllib.parse
from datetime import datetime
import sqlite3
import pytz
import requests

ch_name = "・🤖・lily-log"

def _prefix_callable(bot: commands.Bot, msg: discord.Message) -> str:
    if msg.guild is None:
        return "lily."
    else:
        if msg.guild.me.nick is None:
            return "lily."
        nick = msg.guild.me.display_name
        result = nick.replace("[", "").replace(f"]{bot.user.name}", "")
        return result

def jst():
    now = datetime.datetime.utcnow()
    now = now + datetime.timedelta(hours=9)
    return now

conn=sqlite3.connect("level.db", check_same_thread=False)
c=conn.cursor()

intents = discord.Intents.all()
client = discord.Client(intents=intents)

bot = commands.Bot(command_prefix=_prefix_callable, allowed_mentions=discord.AllowedMentions(everyone=False,users=False,roles=False), case_insensitive=True, intents=intents)

bot.load_extension('dispander')

bot.remove_command('help')

if os.path.isfile("servers.json"):
    with open('servers.json', encoding='utf-8') as f:
        servers = json.load(f)
else:
    servers = {"servers": []}
    with open('servers.json', 'w') as f:
        json.dump(servers, f, indent=4)

@bot.command()
async def gcjoin(ctx):
    if ctx.author.guild_permissions.administrator:
        if not guild_exists(ctx.guild.id):
            server = {
                "guildid": ctx.guild.id,
                "channelid": ctx.channel.id,
                "invite": f'{(await ctx.channel.create_invite()).url}'
            }
            servers["servers"].append(server)
            with open('servers.json', 'w') as f:
                json.dump(servers, f, indent=4)
            embed = discord.Embed(title="**Lilyグローバルへようこそ！**",
                                  description="Lilyグローバルに参加しました！よろしくね！",
                                  color=0x2ecc71)
            embed.set_footer()
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(description="あなたのサーバーにはすでにLilyグローバルチャンネルがあります。\r\n"
                                              "各サーバーは1つのGlobalChatチャンネルを持つことができます。",
                                  color=0x2ecc71)
            await ctx.send(embed=embed)


gBanList = [882348819851935785]

@bot.event
async def on_message(message):
    if message.author.id in gBanList:
            await message.delete()
            await message.channel.send(f"{message.author.mention}さんはGBANされています、メッセージを送信することができません。")
            return
            return
    if message.author.bot:
        return
    if not message.content.startswith('_'):
        if get_globalChat(message.guild.id, message.channel.id):
            await sendAll(message)
    if message.content == 'こんにちは':
        await message.channel.send('こんにちは～！！')
    if message.content == 'こんばんは':
        await message.channel.send('こんばんは～！！')
    await bot.process_commands(message)


async def sendAll(message: Message):
    conent = message.content
    author = message.author
    attachments = message.attachments
    de = pytz.timezone('Europe/Berlin')
    embed = discord.Embed(description=conent, timestamp=datetime.now().astimezone(tz=de), color=0xb18cfe)

    icon = author.avatar_url
    embed.set_author(name= "送信主："+author.name, icon_url=icon)
    if message.attachments != []:
        embed.set_image(url=message.attachments[0].url)
      
    if message.reference: 
                    reference_msg = await message.channel.fetch_message(message.reference.message_id) 
                    if reference_msg.embeds and reference_msg.author == client.user: 
                        reference_message_content = reference_msg.embeds[0].description 
                        reference_message_author = reference_msg.embeds[0].author.name 
                    elif reference_msg.author != client.user: 
                        reference_message_content = reference_msg.content 
                        reference_message_author = reference_msg.author.name+'#'+reference_msg.author.discriminator 
                    reference_content = ""
                    for string in reference_message_content.splitlines(): 
                        reference_content += "> " + string + "\n" 
                    reference_value = "**@{}**\n{}".format(reference_message_author, reference_content) 
                    embed.add_field(name='返信しました', value=reference_value, inline=True) 


    icon_url = "https://cdn.discordapp.com/attachments/942729422325297162/948155085194690560/unnamed.png"
    icon = message.guild.icon_url
    if icon:
        icon_url = icon
    embed.set_footer(text=f'送信されたサーバー: {message.guild.name}', icon_url=icon_url)
    if len(attachments) > 0:
        img = attachments[0]
        embed.set_image(url=img.url)

    for server in servers["servers"]:
        guild: Guild = bot.get_guild(int(server["guildid"]))
        if guild:
            channel: TextChannel = guild.get_channel(int(server["channelid"]))
            if channel:
                perms: Permissions = channel.permissions_for(guild.get_member(bot.user.id))
                if perms.send_messages:
                    if perms.embed_links and perms.attach_files and perms.external_emojis:
                        await channel.send(embed=embed)
                    else:
                        await channel.send('{0}: {1}'.format(author.name, conent))
                        await channel.send('I am missing following permissions: '
                                           '`Send messages` `Embed Links` `Attach Files`'
                                           '`Use external Emojis`')
    #await message.delete()
    await message.add_reaction('<a:S_GIF_up:944248702585942096>')
    await message.add_reaction('<a:S_GIF_check:947863076747767890>')

def guild_exists(guildid):
    for server in servers['servers']:
        if int(server['guildid'] == int(guildid)):
            return True
    return False


def get_globalChat(guild_id, channelid=None):
    globalChat = None
    for server in servers["servers"]:
        if int(server["guildid"]) == int(guild_id):
            if channelid:
                if int(server["channelid"]) == int(channelid):
                    globalChat = server
            else:
                globalChat = server
    return globalChat


def get_globalChat_id(guild_id):
    globalChat = -1
    i = 0
    for server in servers["servers"]:
        if int(server["guildid"]) == int(guild_id):
            globalChat = i
        i += 1
    return globalChat

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.MissingPermissions):
        embed = discord.Embed(title="エラー",
                              description=f"実行者の必要な権限が無いため実行出来ません。",
                              timestamp=ctx.message.created_at,
                              color=discord.Colour.purple())
        await ctx.send(embed=embed)
    elif isinstance(error, discord.ext.commands.errors.BotMissingPermissions):
        embed = discord.Embed(title="エラー",
                              description=f"Botの必要な権限が無いため実行出来ません。",
                              timestamp=ctx.message.created_at,
                              color=discord.Colour.purple())
        embed.set_footer(text="お困りの場合は、サーバー管理者をメンションしてください。")
        await ctx.send(embed=embed)
    elif isinstance(error, discord.ext.commands.errors.CommandNotFound):
        embed = discord.Embed(title="エラー",
                              description=f"不明なコマンドもしくは現在使用不可能なコマンドです。",
                              timestamp=ctx.message.created_at,
                              color=discord.Colour.purple())
        embed.set_footer(text="_helpと送信してコマンドを確認しましょう。")
        await ctx.send(embed=embed)
    elif isinstance(error, discord.ext.commands.errors.MemberNotFound):
        embed = discord.Embed(title="エラー",
                              description=f"指定されたメンバーが見つかりません。",
                              timestamp=ctx.message.created_at,
                              color=discord.Colour.purple())
        await ctx.send(embed=embed)
    elif isinstance(error, discord.ext.commands.errors.BadArgument):
        embed = discord.Embed(title="エラー",
                              description=f"指定された引数がエラーを起こしているため実行出来ません。",
                              timestamp=ctx.message.created_at,
                              color=discord.Colour.purple())
        await ctx.send(embed=embed)
    elif isinstance(error,
                    discord.ext.commands.errors.MissingRequiredArgument):
        embed = discord.Embed(title="エラー",
                              description=f"指定された引数が足りないため実行出来ません。",
                              timestamp=ctx.message.created_at,
                              color=discord.Colour.purple())
        await ctx.send(embed=embed)
    else:
        raise error

@bot.event
async def on_member_join(member):
    if member.guild.system_channel:
        guild = member.guild
        guild_name = member.guild.name
        member_count = guild.member_count
        embed = discord.Embed(
            title=f"誰かが{guild_name}にやってきたよ！",
            description=
            f"{member.mention}さんが入室しました！ \nサーバーの人数が{str(member_count)}人になりました！",
            colour=0xb18cfe)
        embed.set_thumbnail(url=member.avatar_url)
        await member.guild.system_channel.send(embed=embed)

@bot.event
async def on_member_remove(member):
    if member.guild.system_channel:
        embed = discord.Embed(
            title=f"誰かが{member.guild.name}から退出したよ...",
            description=f"{member.mention}さんが退室しました...\nサーバーの人数が1人減りました...",
            colour=0xb18cfe)
        embed.set_thumbnail(url=member.avatar_url)
        await member.guild.system_channel.send(embed=embed)


@bot.event
async def on_guild_join(guild):
    servers = len(bot.guilds)
    members = 0
    for guild in bot.guilds:
      members += guild.member_count - 1
    member_count = guild.member_count
    await bot.change_presence(activity=discord.Game(name=f"lily.help┃{str(servers)}servers┃{str(members)}users┃prefix：lily. ┃Ver.1.7.0"))

@bot.event
async def on_guild_remove(guild):
  servers = len(bot.guilds)
  members = 0
  for guild in bot.guilds:
    members += guild.member_count - 1
  await bot.change_presence(activity=discord.Game(name=f"lily.help┃{str(servers)}servers┃{str(members)}users┃prefix：lily. ┃Ver.1.7.0"))

@bot.event
async def on_ready():
  servers = len(bot.guilds)
  members = 0
  for guild in bot.guilds:
    members += guild.member_count - 1
    await bot.change_presence(activity=discord.Game(name=f"lily.help┃{str(servers)}servers┃{str(members)}users┃prefix：lily. ┃Ver.1.7.0"))
  print('起動完了')
  
  for channel in bot.get_all_channels():
    if channel.name == ch_name:
      runem=discord.Embed(title="<a:S_GIF_up:944248702585942096> Activation complete!", description=f"<@923766717312794674> is up and running!\nIf you have any glitches, I'd appreciate it if you'd mention or DM <@691137657484476466>!", timestamp=datetime.utcnow(), color=0xb18cfe)
      await channel.send(embed = runem)

@bot.command("help", aliases=['へるぷ'])
async def command_list(ctx, type=None):
    async with ctx.typing():
        await asyncio.sleep(0)
    embed = discord.Embed(title="ヘルプパネル",
                          description=f"現在使用できるコマンドです。",
                          colour=0xb18cfe)
    embed.add_field(name="<:S_Bot:939322657567047752>：BOT",
                    value="`help`, `ping`, `invite`",
                    inline=False)
    embed.add_field(
        name="<:S_Blue_star_2:939324440943132713>：tool",
        value="`kick`, `ban`, `unban`, `timer`, `vote`, `si`, `ui`, `mute`, `unmute`, `avatar`, `banner`, `slowmode`, `embed`",
        inline=False,
    )
    embed.add_field(name="<a:S_GIF_LeSpin:939326498630942730>：variety",
                    value="`totusi`, `say`, `slot`, `topic`, `5000`",
                    inline=False)
    embed.add_field(name="✨：その他", value="`gcjoin`, `rank`", inline=False)
    embed1 = discord.Embed(title="ヘルプパネル-BOT", description="現在使用できるコマンドです。", colour=0xb18cfe)
    embed.set_footer(text="1ページ目")
    embed1.add_field(
        name="<:S_Bot:939322657567047752>：BOT",
        value=
        "`help`：現在表示しているメッセージです。\n`ping`：Lilyのping値を表示します。\n`invite`：Lilyの招待リンクを送信します。",
    )
    embed1.set_footer(text="2ページ目")
    embed2 = discord.Embed(title="ヘルプパネル-便利機能",
                           description="現在使用できるコマンドです。",
                           colour=0xb18cfe)
    embed2.add_field(
        name="<:S_Blue_star_2:939324440943132713>：便利機能",
        value="`timer`：タイマーをセットします。\n"
        "`kick`：ユーザーをキックします。\n"
        "`ban`：ユーザーをBANします。\n"
        "`unban`：ユーザーのBANを解除します。\n"
        "`vote`：投票パネルを作成します。\n"
        "`clear`：指定したメッセージを削除します。\n"
        "`si`：サーバー情報を表示します。\n"
        "`ui`：ユーザー情報を表示します。\n"
        "`mute`：メンバーをミュートします。\n"
        "`unmute`：メンバーのミュートを解除します。\n"
        "`avatar`：メンバーのアバターを表示します。\n"
        "`banner`：メンバーのプロフィールバナーを表示します。\n"
        "`gbanner`：メンバーのプロフィールバナー(GIF)を表示します。\n"
        "`slowmode`：低速モードを変更できます。\n"
        "`embed`：埋め込みメッセージを作成できます。\n",
    )
    embed2.set_footer(text="3ページ目")
    embed3 = discord.Embed(title="ヘルプパネル-お遊び",
                           description="現在使用できるコマンドです。",
                           colour=0xb18cfe)
    embed3.add_field(
        name="<a:S_GIF_LeSpin:939326498630942730>：お遊び",
        value="`say`：Botに喋らすことができます、悪用厳禁。\n"
        "`totusi`：突然の死AAを作成します。\n"
        "`slot`：スロットを開始します。\n"
      "`topic`：話題を提供します。\n"
      "`5000`：5000兆円欲しい！のジェネレーターです。",
    )
    embed3.set_footer(text="4ページ目")
    embed4 = discord.Embed(title="ヘルプパネル-その他",
                           description="現在使用できるコマンドです。",
                           colour=0xb18cfe)
    embed4.add_field(
        name="✨：その他",
        value="`gcjoin`：送信したチャンネルをグローバルチャットにします。\n `rank`：Lilyランクを表示します。"
    )
    embed4.set_footer(text="5ページ目")
    pages = [embed, embed1, embed2, embed3, embed4]
    page = 0
    message = await ctx.reply(embed=pages[page], mention_author=False)
    await message.add_reaction("<:S_left_arrow:949302842978631701>")
    await message.add_reaction("<:S_right_arrow:949302839660929064>")
    await message.add_reaction("<:g_:950725686694400090>")

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ["<:S_left_arrow:949302842978631701>", "<:S_right_arrow:949302839660929064>", "<:g_:950725686694400090>"]

    while True:
        try:
            reaction, user = await bot.wait_for("reaction_add",
                                                timeout=120,
                                                check=check)
            if str(reaction.emoji) == "<:S_right_arrow:949302839660929064>" and page != 4:
                page += 1
                await message.edit(embed=pages[page])
                await message.remove_reaction(reaction, user)
            elif str(reaction.emoji) == "<:S_left_arrow:949302842978631701>" and page > 0:
                page -= 1
                await message.edit(embed=pages[page])
                await message.remove_reaction(reaction, user)
            elif str(reaction.emoji) == "<:g_:950725686694400090>":
                await message.edit(embed=embed)
                await message.clear_reactions()
                break
            else:
                await message.remove_reaction(reaction, user)
        except asyncio.TimeoutError:
            await message.edit(embed=embed)
            await message.clear_reactions()
            break


@bot.command()
async def clear(ctx, target: int):
    if ctx.author.guild_permissions.administrator:
        channel = ctx.message.channel
        deleted = await channel.purge(limit=target)
        embed=discord.Embed(title="削除完了！", description=f"**{len(deleted)}** 件のメッセージを削除しました！", color=0xb18cfe)
        await ctx.send(embed=embed)

@bot.command()
async def say(ctx, message):
    await ctx.send(message)
    await message.delete()

@bot.command()
async def vote(ctx, title, *select):
    if len(select) > 10:
        return

    emoji_list = ["1⃣", "2⃣", "3⃣", "4⃣", "5⃣", "6⃣", "7⃣", "8⃣", "9⃣", "🔟"]

    value = ""
    for num in range(len(select)):
        value += emoji_list[num] + select[num] + "\n"
    embed = discord.Embed(title=value, color=0xb18cfe)

    msg = await ctx.send("**" + title + "**", embed=embed)
    for i in range(len(select)):
        await msg.add_reaction(emoji_list[i])
    return


@bot.command()
async def invite(ctx):
    await ctx.reply(
        "https://discord.com/oauth2/authorize?client_id=923766717312794674&scope=bot+applications.commands&permissions=2147483647"
    )


@bot.command(name="ping")
async def ping(ctx: commands.Context):
    pingem=discord.Embed(title="ぽんぐっ！🏓", description=f"Ping値は**{round(bot.latency * 1000)}ms**だよ〜！", color=0xb18cfe)
    await ctx.send(embed=pingem)


@bot.command()
async def kick(ctx, member: discord.Member, reason=None):
    async with ctx.typing():
        await asyncio.sleep(0)
    if ctx.author.guild_permissions.administrator:
        kick = discord.Embed(
            title="メンバーをキックしました。",
            description=f"{ctx.author.mention}さんが{member.mention}さんをキックしました。",
            color=0xb18cfe)
        kick.set_thumbnail(url=member.avatar_url)
        await ctx.reply(embed=kick)
        await member.kick(reason=reason)
    else:
        await ctx.reply("このコマンドを実行できるのは管理者のみです！")


@bot.command()
async def ban(ctx, member: discord.Member, reason=None):
    async with ctx.typing():
        await asyncio.sleep(0)
    if ctx.author.guild_permissions.administrator:
        ban = discord.Embed(
            title="メンバーをBANしました。",
            description=f"{ctx.author.mention}さんが{member.mention}さんをBANしました。",
            color=0xb18cfe)
        ban.set_thumbnail(url=member.avatar_url)
        await ctx.reply(embed=ban)
        await member.ban(reason=reason)
    else:
        await ctx.reply("このコマンドを実行できるのは管理者のみです！")

@bot.command()
async def ui(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author 
    date_format = "%a, %d %b %Y %I:%M %p"
    memberAvatar = member.avatar_url 
    embed = discord.Embed(title="User Infomation",description=f"**ID :** ``{member.id}``", color=0xb18cfe)
    embed.set_thumbnail(url=memberAvatar)
    
    embed.add_field(name='Name', value=f'``{member}``', inline=True)
    embed.add_field(name='NickName',value=f'``{member.display_name}#{member.discriminator}``',inline=True)
    embed.add_field(name='Bot', value=f"``{member.bot}``" ,inline=True)

    if len(member.roles) > 1:
        role_string = ' '.join([r.mention for r in member.roles][1:])
        embed.add_field(name="Roles [{}]".format(len(member.roles)-1), value=role_string, inline=False)  

    embed.add_field(name='Creation account', value=f"``{member.created_at.strftime(date_format)}``", inline=True)
    embed.add_field(name='Joined server', value=f"``{member.joined_at.strftime(date_format)}``", inline=True)
    await ctx.send(embed=embed)

@bot.command()
async def unban(ctx, id: int):
    if ctx.author.guild_permissions.administrator:
        user = await bot.fetch_user(id)
        unban = discord.Embed(
            title="メンバーのBANを解除しました",
            description=f"{ctx.author.mention}さんが{user.mention}さんのBANを解除しました。",
            color=0xb18cfe)
        unban.set_thumbnail(url=user.avatar_url)
        await ctx.reply(embed=unban)
        await ctx.guild.unban(user)
    else:
        await ctx.reply("このコマンドを実行できるのは管理者のみです！")


@bot.command()
async def mute(ctx, member: discord.Member):
    async with ctx.typing():
        await asyncio.sleep(0)
    if ctx.author.guild_permissions.administrator:
        mute = discord.Embed(
            title="メンバーをミュートしたよ！",
            description=f"{ctx.author.mention}さんが{member.mention}さんをミュートしたよ！",
            color=0xb18cfe)
        mute.set_thumbnail(url=member.avatar_url)
        await ctx.reply(embed=mute)
        guild = ctx.guild
        for channel in guild.channels:
            await channel.set_permissions(member, send_messages=False)
    else:
        await ctx.reply("このコマンドを実行できるのは管理者のみです！")


@bot.command()
async def unmute(ctx, member: discord.Member):
    async with ctx.typing():
        await asyncio.sleep(0)
    if ctx.author.guild_permissions.administrator:
        mute = discord.Embed(
            title="メンバーのミュートを解除したよ！",
            description=
            f"{ctx.author.mention}さんが{member.mention}さんのミュートを解除したよ！",
            color=0xb18cfe,
        )
        mute.set_thumbnail(url=member.avatar_url)
        await ctx.reply(embed=mute)
        guild = ctx.guild
        for channel in guild.channels:
            await channel.set_permissions(member, overwrite=None)
    else:
        await ctx.reply("このコマンドを実行できるのは管理者のみです！")

#serverinfo
@bot.command()
async def si(ctx):
    async with ctx.typing():
        await asyncio.sleep(0)
    guild = ctx.guild
    name = str(ctx.guild.name)
    sid = str(ctx.guild.id)
    owner = str(ctx.guild.owner.id)
    region = str(ctx.guild.region)
    mcount = str(ctx.guild.member_count)
    ucount = str(sum(1 for member in guild.members if not member.bot))
    bcount = str(sum(1 for member in guild.members if member.bot))
    tchannels = len(ctx.guild.text_channels)
    vchannels = len(ctx.guild.voice_channels)
    categories = len(ctx.guild.categories)
    channels = tchannels + vchannels
    embed = discord.Embed(title="サーバーインフォメーション",
                          description="このサーバーの情報です！",
                          color=0xb18cfe)
    embed.add_field(
        name="📋",
        value=
        f"`サーバー名`：{name}\n`サーバーID`：{sid}\n`オーナー`：<@{owner}>\n`地域`：{region}",
        inline=False)
    embed.add_field(
        name="👤",
        value=f"`メンバー数`：{mcount}\n`ユーザー数`：{ucount}\n`BOT数`：{bcount}",
        inline=False)
    embed.add_field(
        name="💬",
        value=
        f"`チャンネル数`：{channels}\n`テキストチャンネル数`：{tchannels}\n`ボイスチャンネル数`：{vchannels}\n`カテゴリー数`：{categories}",
        inline=False,
    )
    await ctx.send(embed=embed)

@bot.command()
async def timer(ctx, number):
    async with ctx.typing():
        await asyncio.sleep(0)
    await ctx.reply(str(number) + "秒後に通知します！")
    await asyncio.sleep(int(number))
    await ctx.reply("時間ですよ〜！タイマーを終了します！", mention_author=True)

@bot.command()
async def totusi(ctx, *, arg="突然の死"):
    async with ctx.typing():
        await asyncio.sleep(0)
    ue = "人" * len(arg)
    sita = "^Y" * len(arg)
    await ctx.reply("＿人" + ue + "人＿\n＞　" + arg + "　＜\n￣^Y" + sita + "^Y￣")

@bot.command()
async def avatar(ctx, user:discord.Member = None):
    if user == None:
        user = ctx.author
    userAvatar = user.avatar_url
    avatarEmbed = discord.Embed(title = "画像リンク", url = userAvatar, color=0xb18cfe)
    avatarEmbed.set_author(name=str(user), icon_url=userAvatar)
    avatarEmbed.set_image(url = userAvatar)
    avatarEmbed.set_footer(text= "ID： "+str(user.id))
    await ctx.send(embed = avatarEmbed)

@bot.command()
async def slowmode(ctx, seconds: int):
  if ctx.author.guild_permissions.administrator:
    await ctx.channel.edit(slowmode_delay=seconds)
    embed=discord.Embed(title="設定完了！", description=f"このチャンネルの低速モードを**{seconds}秒**に設定しました！", color=0xb18cfe)
    await ctx.send(embed=embed)
    await ctx.send("管理者しかこのコマンドは使えないよ！")

@bot.command()
async def slot(ctx):
    async with ctx.typing():
        await asyncio.sleep(0)
    A = random.choice(("<:Aoi:941334135862079558>", "<:S_Blue_star:939324353458339890>", "<a:S_GIF_kerokeroGun:938720877166616596>"))
    B = random.choice(("<:Aoi:941334135862079558>", "<:S_Blue_star:939324353458339890>", "<a:S_GIF_kerokeroGun:938720877166616596>"))
    C = random.choice(("<:Aoi:941334135862079558>", "<:S_Blue_star:939324353458339890>", "<a:S_GIF_kerokeroGun:938720877166616596>"))
    embed = discord.Embed(title="スロット結果〜！", description="｜" + A + "｜" + B + "｜" + C + "｜", color=0xb18cfe)
    await ctx.reply(embed=embed, mention_author=False)
    if A == B == C:
        await ctx.reply("当選したよ！おめでと〜！！", mention_author=False)

@bot.command()
async def topic(ctx):
    async with ctx.typing():
        await asyncio.sleep(0)
    topic = random.choice(("みんなの好きなYouTuberは誰？", "みんなの家族構成を教えて！", "好きな食べ物！", "好きな人...いる？", "落ち着く場所はどこ？", "よく行く場所教えて！", "好きな飲み物！", "自分のいいところはある？", "お気に入りのDiscordBotは？もちろんわたs((殴", "結婚するならどんな人と結婚する？", "お気に入りの音楽は何？", "黒歴史はある？", "使ってるスマホは何？"))
    embed = discord.Embed(title="話題はこちら！", description="<:Aoi2:942971788416147527> ＜ " + topic, color=0xb18cfe)
    await ctx.reply(embed=embed, mention_author=False)

@bot.command()
async def slist(ctx, a=None):
    if ctx.author.id == 691137657484476466:
        if a == "id":
            guild_list = "\n".join(f"{guild.name} {guild.id}" for guild in bot.guilds)
            await ctx.reply(guild_list)
        else:
            guild_list = "\n".join(f"{guild.name}" for guild in bot.guilds)
            await ctx.reply(guild_list)

@bot.command(name="5000")
async def _5000(ctx, 上="5000兆円", 下="欲しい！"):
  embed = discord.Embed(title=f"__{上}{下}__を作成しました！", color=0xb18cfe)
  embed.set_image(url="https://gsapi.cyberrex.jp/image?"f"top={urllib.parse.quote(上)}&bottom={urllib.parse.quote(下)}")
  await ctx.send(embed=embed)

@bot.command()
async def embed(ctx, title="title", description="description"):
  embed=discord.Embed(title=f"{title}", description=f"{description}", color=0xb18cfe)
  embed.set_author(name=str(ctx.author))
  await ctx.send(embed=embed)

@bot.command(aliases=["b"])
async def banner(ctx, user:discord.Member=None):
    member = ctx.author
    if user == None:
        user = ctx.author
    try:
        req = await bot.http.request(discord.http.Route("GET", "/users/{uid}", uid=user.id))
        banner_id = req["banner"]
        if banner_id:
            banner_url = f"https://cdn.discordapp.com/banners/{user.id}/{banner_id}?size=1024"
        embed=discord.Embed(title="Banner Link", description=f"{user.name}'s banner", color=0xb18cfe, url = banner_url)
        embed.set_image(url = banner_url)
        embed.set_footer(text=str(f"コマンド実行者: {member}"))
        await ctx.send(embed=embed)
    except:
        embed=discord.Embed(title="エラー", color=0xb18cfe)
        embed.add_field(name="バナーが設定されていません。", value="バナーが設定されている人を指定してください。")
        await ctx.send(embed=embed)
        
@bot.command(aliases=["gb"])
async def gbanner(ctx, user:discord.Member=None):
  rq_user = ctx.author
  if user == None:
    user = ctx.author
    try:
      req = await bot.http.request(discord.http.Route("GET", "/users/{uid}", uid=user.id))
      banner_id = req["banner"]
      if banner_id:
        banner_url = f"https://cdn.discordapp.com/banners/{user.id}/{banner_id}.gif?size=1024"
        embed=discord.Embed(title="Banner Link", description=f"{user.mention}'s banner", url = banner_url, color=0xb18cfe)
        embed.set_image(url = banner_url)
        embed.set_footer(text=str(f"コマンド実行者：{rq_user}"))
        await ctx.send(embed=embed)
    except:
        embed=discord.Embed(title="エラー", color=0xb18cfe)
        embed.add_field(name="バナーが設定されていません", value="バナーが設定されている人を指定してください。")
        await ctx.send(embed=embed)
      
Keep_alive.keep_alive()

bot.run(os.getenv('TOKEN'))
