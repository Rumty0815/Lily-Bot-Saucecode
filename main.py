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

ch_name = "ã»ð¤ã»lily-log"

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
            embed = discord.Embed(title="**Lilyã°ã­ã¼ãã«ã¸ããããï¼**",
                                  description="Lilyã°ã­ã¼ãã«ã«åå ãã¾ããï¼ããããã­ï¼",
                                  color=0x2ecc71)
            embed.set_footer()
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(description="ããªãã®ãµã¼ãã¼ã«ã¯ãã§ã«Lilyã°ã­ã¼ãã«ãã£ã³ãã«ãããã¾ãã\r\n"
                                              "åãµã¼ãã¼ã¯1ã¤ã®GlobalChatãã£ã³ãã«ãæã¤ãã¨ãã§ãã¾ãã",
                                  color=0x2ecc71)
            await ctx.send(embed=embed)


gBanList = [882348819851935785]

@bot.event
async def on_message(message):
    if message.author.id in gBanList:
            await message.delete()
            await message.channel.send(f"{message.author.mention}ããã¯GBANããã¦ãã¾ããã¡ãã»ã¼ã¸ãéä¿¡ãããã¨ãã§ãã¾ããã")
            return
            return
    if message.author.bot:
        return
    if not message.content.startswith('_'):
        if get_globalChat(message.guild.id, message.channel.id):
            await sendAll(message)
    if message.content == 'ããã«ã¡ã¯':
        await message.channel.send('ããã«ã¡ã¯ï½ï¼ï¼')
    if message.content == 'ããã°ãã¯':
        await message.channel.send('ããã°ãã¯ï½ï¼ï¼')
    await bot.process_commands(message)


async def sendAll(message: Message):
    conent = message.content
    author = message.author
    attachments = message.attachments
    de = pytz.timezone('Europe/Berlin')
    embed = discord.Embed(description=conent, timestamp=datetime.now().astimezone(tz=de), color=0xb18cfe)

    icon = author.avatar_url
    embed.set_author(name= "éä¿¡ä¸»ï¼"+author.name, icon_url=icon)
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
                    embed.add_field(name='è¿ä¿¡ãã¾ãã', value=reference_value, inline=True) 


    icon_url = "https://cdn.discordapp.com/attachments/942729422325297162/948155085194690560/unnamed.png"
    icon = message.guild.icon_url
    if icon:
        icon_url = icon
    embed.set_footer(text=f'éä¿¡ããããµã¼ãã¼: {message.guild.name}', icon_url=icon_url)
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
        embed = discord.Embed(title="ã¨ã©ã¼",
                              description=f"å®è¡èã®å¿è¦ãªæ¨©éãç¡ãããå®è¡åºæ¥ã¾ããã",
                              timestamp=ctx.message.created_at,
                              color=discord.Colour.purple())
        await ctx.send(embed=embed)
    elif isinstance(error, discord.ext.commands.errors.BotMissingPermissions):
        embed = discord.Embed(title="ã¨ã©ã¼",
                              description=f"Botã®å¿è¦ãªæ¨©éãç¡ãããå®è¡åºæ¥ã¾ããã",
                              timestamp=ctx.message.created_at,
                              color=discord.Colour.purple())
        embed.set_footer(text="ãå°ãã®å ´åã¯ããµã¼ãã¼ç®¡çèãã¡ã³ã·ã§ã³ãã¦ãã ããã")
        await ctx.send(embed=embed)
    elif isinstance(error, discord.ext.commands.errors.CommandNotFound):
        embed = discord.Embed(title="ã¨ã©ã¼",
                              description=f"ä¸æãªã³ãã³ããããã¯ç¾å¨ä½¿ç¨ä¸å¯è½ãªã³ãã³ãã§ãã",
                              timestamp=ctx.message.created_at,
                              color=discord.Colour.purple())
        embed.set_footer(text="_helpã¨éä¿¡ãã¦ã³ãã³ããç¢ºèªãã¾ãããã")
        await ctx.send(embed=embed)
    elif isinstance(error, discord.ext.commands.errors.MemberNotFound):
        embed = discord.Embed(title="ã¨ã©ã¼",
                              description=f"æå®ãããã¡ã³ãã¼ãè¦ã¤ããã¾ããã",
                              timestamp=ctx.message.created_at,
                              color=discord.Colour.purple())
        await ctx.send(embed=embed)
    elif isinstance(error, discord.ext.commands.errors.BadArgument):
        embed = discord.Embed(title="ã¨ã©ã¼",
                              description=f"æå®ãããå¼æ°ãã¨ã©ã¼ãèµ·ããã¦ããããå®è¡åºæ¥ã¾ããã",
                              timestamp=ctx.message.created_at,
                              color=discord.Colour.purple())
        await ctx.send(embed=embed)
    elif isinstance(error,
                    discord.ext.commands.errors.MissingRequiredArgument):
        embed = discord.Embed(title="ã¨ã©ã¼",
                              description=f"æå®ãããå¼æ°ãè¶³ããªãããå®è¡åºæ¥ã¾ããã",
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
            title=f"èª°ãã{guild_name}ã«ãã£ã¦ãããï¼",
            description=
            f"{member.mention}ãããå¥å®¤ãã¾ããï¼ \nãµã¼ãã¼ã®äººæ°ã{str(member_count)}äººã«ãªãã¾ããï¼",
            colour=0xb18cfe)
        embed.set_thumbnail(url=member.avatar_url)
        await member.guild.system_channel.send(embed=embed)

@bot.event
async def on_member_remove(member):
    if member.guild.system_channel:
        embed = discord.Embed(
            title=f"èª°ãã{member.guild.name}ããéåºããã...",
            description=f"{member.mention}ãããéå®¤ãã¾ãã...\nãµã¼ãã¼ã®äººæ°ã1äººæ¸ãã¾ãã...",
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
    await bot.change_presence(activity=discord.Game(name=f"lily.helpâ{str(servers)}serversâ{str(members)}usersâprefixï¼lily. âVer.1.7.0"))

@bot.event
async def on_guild_remove(guild):
  servers = len(bot.guilds)
  members = 0
  for guild in bot.guilds:
    members += guild.member_count - 1
  await bot.change_presence(activity=discord.Game(name=f"lily.helpâ{str(servers)}serversâ{str(members)}usersâprefixï¼lily. âVer.1.7.0"))

@bot.event
async def on_ready():
  servers = len(bot.guilds)
  members = 0
  for guild in bot.guilds:
    members += guild.member_count - 1
    await bot.change_presence(activity=discord.Game(name=f"lily.helpâ{str(servers)}serversâ{str(members)}usersâprefixï¼lily. âVer.1.7.0"))
  print('èµ·åå®äº')
  
  for channel in bot.get_all_channels():
    if channel.name == ch_name:
      runem=discord.Embed(title="<a:S_GIF_up:944248702585942096> Activation complete!", description=f"<@923766717312794674> is up and running!\nIf you have any glitches, I'd appreciate it if you'd mention or DM <@691137657484476466>!", timestamp=datetime.utcnow(), color=0xb18cfe)
      await channel.send(embed = runem)

@bot.command("help", aliases=['ã¸ãã·'])
async def command_list(ctx, type=None):
    async with ctx.typing():
        await asyncio.sleep(0)
    embed = discord.Embed(title="ãã«ãããã«",
                          description=f"ç¾å¨ä½¿ç¨ã§ããã³ãã³ãã§ãã",
                          colour=0xb18cfe)
    embed.add_field(name="<:S_Bot:939322657567047752>ï¼BOT",
                    value="`help`, `ping`, `invite`",
                    inline=False)
    embed.add_field(
        name="<:S_Blue_star_2:939324440943132713>ï¼tool",
        value="`kick`, `ban`, `unban`, `timer`, `vote`, `si`, `ui`, `mute`, `unmute`, `avatar`, `banner`, `slowmode`, `embed`",
        inline=False,
    )
    embed.add_field(name="<a:S_GIF_LeSpin:939326498630942730>ï¼variety",
                    value="`totusi`, `say`, `slot`, `topic`, `5000`",
                    inline=False)
    embed.add_field(name="â¨ï¼ãã®ä»", value="`gcjoin`, `rank`", inline=False)
    embed1 = discord.Embed(title="ãã«ãããã«-BOT", description="ç¾å¨ä½¿ç¨ã§ããã³ãã³ãã§ãã", colour=0xb18cfe)
    embed.set_footer(text="1ãã¼ã¸ç®")
    embed1.add_field(
        name="<:S_Bot:939322657567047752>ï¼BOT",
        value=
        "`help`ï¼ç¾å¨è¡¨ç¤ºãã¦ããã¡ãã»ã¼ã¸ã§ãã\n`ping`ï¼Lilyã®pingå¤ãè¡¨ç¤ºãã¾ãã\n`invite`ï¼Lilyã®æå¾ãªã³ã¯ãéä¿¡ãã¾ãã",
    )
    embed1.set_footer(text="2ãã¼ã¸ç®")
    embed2 = discord.Embed(title="ãã«ãããã«-ä¾¿å©æ©è½",
                           description="ç¾å¨ä½¿ç¨ã§ããã³ãã³ãã§ãã",
                           colour=0xb18cfe)
    embed2.add_field(
        name="<:S_Blue_star_2:939324440943132713>ï¼ä¾¿å©æ©è½",
        value="`timer`ï¼ã¿ã¤ãã¼ãã»ãããã¾ãã\n"
        "`kick`ï¼ã¦ã¼ã¶ã¼ãã­ãã¯ãã¾ãã\n"
        "`ban`ï¼ã¦ã¼ã¶ã¼ãBANãã¾ãã\n"
        "`unban`ï¼ã¦ã¼ã¶ã¼ã®BANãè§£é¤ãã¾ãã\n"
        "`vote`ï¼æç¥¨ããã«ãä½æãã¾ãã\n"
        "`clear`ï¼æå®ããã¡ãã»ã¼ã¸ãåé¤ãã¾ãã\n"
        "`si`ï¼ãµã¼ãã¼æå ±ãè¡¨ç¤ºãã¾ãã\n"
        "`ui`ï¼ã¦ã¼ã¶ã¼æå ±ãè¡¨ç¤ºãã¾ãã\n"
        "`mute`ï¼ã¡ã³ãã¼ããã¥ã¼ããã¾ãã\n"
        "`unmute`ï¼ã¡ã³ãã¼ã®ãã¥ã¼ããè§£é¤ãã¾ãã\n"
        "`avatar`ï¼ã¡ã³ãã¼ã®ã¢ãã¿ã¼ãè¡¨ç¤ºãã¾ãã\n"
        "`banner`ï¼ã¡ã³ãã¼ã®ãã­ãã£ã¼ã«ããã¼ãè¡¨ç¤ºãã¾ãã\n"
        "`gbanner`ï¼ã¡ã³ãã¼ã®ãã­ãã£ã¼ã«ããã¼(GIF)ãè¡¨ç¤ºãã¾ãã\n"
        "`slowmode`ï¼ä½éã¢ã¼ããå¤æ´ã§ãã¾ãã\n"
        "`embed`ï¼åãè¾¼ã¿ã¡ãã»ã¼ã¸ãä½æã§ãã¾ãã\n",
    )
    embed2.set_footer(text="3ãã¼ã¸ç®")
    embed3 = discord.Embed(title="ãã«ãããã«-ãéã³",
                           description="ç¾å¨ä½¿ç¨ã§ããã³ãã³ãã§ãã",
                           colour=0xb18cfe)
    embed3.add_field(
        name="<a:S_GIF_LeSpin:939326498630942730>ï¼ãéã³",
        value="`say`ï¼Botã«åãããã¨ãã§ãã¾ããæªç¨å³ç¦ã\n"
        "`totusi`ï¼çªç¶ã®æ­»AAãä½æãã¾ãã\n"
        "`slot`ï¼ã¹ã­ãããéå§ãã¾ãã\n"
      "`topic`ï¼è©±é¡ãæä¾ãã¾ãã\n"
      "`5000`ï¼5000ååæ¬²ããï¼ã®ã¸ã§ãã¬ã¼ã¿ã¼ã§ãã",
    )
    embed3.set_footer(text="4ãã¼ã¸ç®")
    embed4 = discord.Embed(title="ãã«ãããã«-ãã®ä»",
                           description="ç¾å¨ä½¿ç¨ã§ããã³ãã³ãã§ãã",
                           colour=0xb18cfe)
    embed4.add_field(
        name="â¨ï¼ãã®ä»",
        value="`gcjoin`ï¼éä¿¡ãããã£ã³ãã«ãã°ã­ã¼ãã«ãã£ããã«ãã¾ãã\n `rank`ï¼Lilyã©ã³ã¯ãè¡¨ç¤ºãã¾ãã"
    )
    embed4.set_footer(text="5ãã¼ã¸ç®")
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
        embed=discord.Embed(title="åé¤å®äºï¼", description=f"**{len(deleted)}** ä»¶ã®ã¡ãã»ã¼ã¸ãåé¤ãã¾ããï¼", color=0xb18cfe)
        await ctx.send(embed=embed)

@bot.command()
async def say(ctx, message):
    await ctx.send(message)
    await message.delete()

@bot.command()
async def vote(ctx, title, *select):
    if len(select) > 10:
        return

    emoji_list = ["1â£", "2â£", "3â£", "4â£", "5â£", "6â£", "7â£", "8â£", "9â£", "ð"]

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
    pingem=discord.Embed(title="ã½ããã£ï¼ð", description=f"Pingå¤ã¯**{round(bot.latency * 1000)}ms**ã ããï¼", color=0xb18cfe)
    await ctx.send(embed=pingem)


@bot.command()
async def kick(ctx, member: discord.Member, reason=None):
    async with ctx.typing():
        await asyncio.sleep(0)
    if ctx.author.guild_permissions.administrator:
        kick = discord.Embed(
            title="ã¡ã³ãã¼ãã­ãã¯ãã¾ããã",
            description=f"{ctx.author.mention}ããã{member.mention}ãããã­ãã¯ãã¾ããã",
            color=0xb18cfe)
        kick.set_thumbnail(url=member.avatar_url)
        await ctx.reply(embed=kick)
        await member.kick(reason=reason)
    else:
        await ctx.reply("ãã®ã³ãã³ããå®è¡ã§ããã®ã¯ç®¡çèã®ã¿ã§ãï¼")


@bot.command()
async def ban(ctx, member: discord.Member, reason=None):
    async with ctx.typing():
        await asyncio.sleep(0)
    if ctx.author.guild_permissions.administrator:
        ban = discord.Embed(
            title="ã¡ã³ãã¼ãBANãã¾ããã",
            description=f"{ctx.author.mention}ããã{member.mention}ãããBANãã¾ããã",
            color=0xb18cfe)
        ban.set_thumbnail(url=member.avatar_url)
        await ctx.reply(embed=ban)
        await member.ban(reason=reason)
    else:
        await ctx.reply("ãã®ã³ãã³ããå®è¡ã§ããã®ã¯ç®¡çèã®ã¿ã§ãï¼")

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
            title="ã¡ã³ãã¼ã®BANãè§£é¤ãã¾ãã",
            description=f"{ctx.author.mention}ããã{user.mention}ããã®BANãè§£é¤ãã¾ããã",
            color=0xb18cfe)
        unban.set_thumbnail(url=user.avatar_url)
        await ctx.reply(embed=unban)
        await ctx.guild.unban(user)
    else:
        await ctx.reply("ãã®ã³ãã³ããå®è¡ã§ããã®ã¯ç®¡çèã®ã¿ã§ãï¼")


@bot.command()
async def mute(ctx, member: discord.Member):
    async with ctx.typing():
        await asyncio.sleep(0)
    if ctx.author.guild_permissions.administrator:
        mute = discord.Embed(
            title="ã¡ã³ãã¼ããã¥ã¼ããããï¼",
            description=f"{ctx.author.mention}ããã{member.mention}ããããã¥ã¼ããããï¼",
            color=0xb18cfe)
        mute.set_thumbnail(url=member.avatar_url)
        await ctx.reply(embed=mute)
        guild = ctx.guild
        for channel in guild.channels:
            await channel.set_permissions(member, send_messages=False)
    else:
        await ctx.reply("ãã®ã³ãã³ããå®è¡ã§ããã®ã¯ç®¡çèã®ã¿ã§ãï¼")


@bot.command()
async def unmute(ctx, member: discord.Member):
    async with ctx.typing():
        await asyncio.sleep(0)
    if ctx.author.guild_permissions.administrator:
        mute = discord.Embed(
            title="ã¡ã³ãã¼ã®ãã¥ã¼ããè§£é¤ãããï¼",
            description=
            f"{ctx.author.mention}ããã{member.mention}ããã®ãã¥ã¼ããè§£é¤ãããï¼",
            color=0xb18cfe,
        )
        mute.set_thumbnail(url=member.avatar_url)
        await ctx.reply(embed=mute)
        guild = ctx.guild
        for channel in guild.channels:
            await channel.set_permissions(member, overwrite=None)
    else:
        await ctx.reply("ãã®ã³ãã³ããå®è¡ã§ããã®ã¯ç®¡çèã®ã¿ã§ãï¼")

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
    embed = discord.Embed(title="ãµã¼ãã¼ã¤ã³ãã©ã¡ã¼ã·ã§ã³",
                          description="ãã®ãµã¼ãã¼ã®æå ±ã§ãï¼",
                          color=0xb18cfe)
    embed.add_field(
        name="ð",
        value=
        f"`ãµã¼ãã¼å`ï¼{name}\n`ãµã¼ãã¼ID`ï¼{sid}\n`ãªã¼ãã¼`ï¼<@{owner}>\n`å°å`ï¼{region}",
        inline=False)
    embed.add_field(
        name="ð¤",
        value=f"`ã¡ã³ãã¼æ°`ï¼{mcount}\n`ã¦ã¼ã¶ã¼æ°`ï¼{ucount}\n`BOTæ°`ï¼{bcount}",
        inline=False)
    embed.add_field(
        name="ð¬",
        value=
        f"`ãã£ã³ãã«æ°`ï¼{channels}\n`ãã­ã¹ããã£ã³ãã«æ°`ï¼{tchannels}\n`ãã¤ã¹ãã£ã³ãã«æ°`ï¼{vchannels}\n`ã«ãã´ãªã¼æ°`ï¼{categories}",
        inline=False,
    )
    await ctx.send(embed=embed)

@bot.command()
async def timer(ctx, number):
    async with ctx.typing():
        await asyncio.sleep(0)
    await ctx.reply(str(number) + "ç§å¾ã«éç¥ãã¾ãï¼")
    await asyncio.sleep(int(number))
    await ctx.reply("æéã§ãããï¼ã¿ã¤ãã¼ãçµäºãã¾ãï¼", mention_author=True)

@bot.command()
async def totusi(ctx, *, arg="çªç¶ã®æ­»"):
    async with ctx.typing():
        await asyncio.sleep(0)
    ue = "äºº" * len(arg)
    sita = "^Y" * len(arg)
    await ctx.reply("ï¼¿äºº" + ue + "äººï¼¿\nï¼ã" + arg + "ãï¼\nï¿£^Y" + sita + "^Yï¿£")

@bot.command()
async def avatar(ctx, user:discord.Member = None):
    if user == None:
        user = ctx.author
    userAvatar = user.avatar_url
    avatarEmbed = discord.Embed(title = "ç»åãªã³ã¯", url = userAvatar, color=0xb18cfe)
    avatarEmbed.set_author(name=str(user), icon_url=userAvatar)
    avatarEmbed.set_image(url = userAvatar)
    avatarEmbed.set_footer(text= "IDï¼ "+str(user.id))
    await ctx.send(embed = avatarEmbed)

@bot.command()
async def slowmode(ctx, seconds: int):
  if ctx.author.guild_permissions.administrator:
    await ctx.channel.edit(slowmode_delay=seconds)
    embed=discord.Embed(title="è¨­å®å®äºï¼", description=f"ãã®ãã£ã³ãã«ã®ä½éã¢ã¼ãã**{seconds}ç§**ã«è¨­å®ãã¾ããï¼", color=0xb18cfe)
    await ctx.send(embed=embed)
    await ctx.send("ç®¡çèãããã®ã³ãã³ãã¯ä½¿ããªããï¼")

@bot.command()
async def slot(ctx):
    async with ctx.typing():
        await asyncio.sleep(0)
    A = random.choice(("<:Aoi:941334135862079558>", "<:S_Blue_star:939324353458339890>", "<a:S_GIF_kerokeroGun:938720877166616596>"))
    B = random.choice(("<:Aoi:941334135862079558>", "<:S_Blue_star:939324353458339890>", "<a:S_GIF_kerokeroGun:938720877166616596>"))
    C = random.choice(("<:Aoi:941334135862079558>", "<:S_Blue_star:939324353458339890>", "<a:S_GIF_kerokeroGun:938720877166616596>"))
    embed = discord.Embed(title="ã¹ã­ããçµæãï¼", description="ï½" + A + "ï½" + B + "ï½" + C + "ï½", color=0xb18cfe)
    await ctx.reply(embed=embed, mention_author=False)
    if A == B == C:
        await ctx.reply("å½é¸ãããï¼ããã§ã¨ãï¼ï¼", mention_author=False)

@bot.command()
async def topic(ctx):
    async with ctx.typing():
        await asyncio.sleep(0)
    topic = random.choice(("ã¿ããªã®å¥½ããªYouTuberã¯èª°ï¼", "ã¿ããªã®å®¶ææ§æãæãã¦ï¼", "å¥½ããªé£ã¹ç©ï¼", "å¥½ããªäºº...ããï¼", "è½ã¡çãå ´æã¯ã©ãï¼", "ããè¡ãå ´ææãã¦ï¼", "å¥½ããªé£²ã¿ç©ï¼", "èªåã®ããã¨ããã¯ããï¼", "ãæ°ã«å¥ãã®DiscordBotã¯ï¼ãã¡ããããs((æ®´", "çµå©ãããªãã©ããªäººã¨çµå©ããï¼", "ãæ°ã«å¥ãã®é³æ¥½ã¯ä½ï¼", "é»æ­´å²ã¯ããï¼", "ä½¿ã£ã¦ãã¹ããã¯ä½ï¼"))
    embed = discord.Embed(title="è©±é¡ã¯ãã¡ãï¼", description="<:Aoi2:942971788416147527> ï¼ " + topic, color=0xb18cfe)
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
async def _5000(ctx, ä¸="5000åå", ä¸="æ¬²ããï¼"):
  embed = discord.Embed(title=f"__{ä¸}{ä¸}__ãä½æãã¾ããï¼", color=0xb18cfe)
  embed.set_image(url="https://gsapi.cyberrex.jp/image?"f"top={urllib.parse.quote(ä¸)}&bottom={urllib.parse.quote(ä¸)}")
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
        embed.set_footer(text=str(f"ã³ãã³ãå®è¡è: {member}"))
        await ctx.send(embed=embed)
    except:
        embed=discord.Embed(title="ã¨ã©ã¼", color=0xb18cfe)
        embed.add_field(name="ããã¼ãè¨­å®ããã¦ãã¾ããã", value="ããã¼ãè¨­å®ããã¦ããäººãæå®ãã¦ãã ããã")
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
        embed.set_footer(text=str(f"ã³ãã³ãå®è¡èï¼{rq_user}"))
        await ctx.send(embed=embed)
    except:
        embed=discord.Embed(title="ã¨ã©ã¼", color=0xb18cfe)
        embed.add_field(name="ããã¼ãè¨­å®ããã¦ãã¾ãã", value="ããã¼ãè¨­å®ããã¦ããäººãæå®ãã¦ãã ããã")
        await ctx.send(embed=embed)
      
Keep_alive.keep_alive()

bot.run(os.getenv('TOKEN'))
