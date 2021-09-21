## Libraries imports
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from config import *

## App imports
from app.settings import Settings
from app.utils import guild_to_audiocontroller, guild_to_settings
from app.audio_controller import AudioController
from app.static import COMMANDS

## Command imports
from app.commands.general import General
from app.commands.music import Music

load_dotenv()


## Discord API config
DESCRIPTION = 'Toss a coin to your witcher'
INTENTS = discord.Intents.all()
PREFIX = BOT_PREFIX
TOKEN = os.getenv("DISCORD_TOKEN")
bot = commands.Bot(
        command_prefix=commands.when_mentioned_or(PREFIX),
        description=DESCRIPTION,
        Intents=INTENTS,
        help_command=None,
        case_insensitive=True
)


## Events
@bot.event
async def on_ready():
    print(STARTUP_MESSAGE)

    await bot.change_presence(activity = discord.Activity(
        type=discord.ActivityType.listening,
        name=f'{PREFIX}help'
    ))

    for guild in bot.guilds:
        await register(guild)
        print(f'Uniu-se a: {guild.name}')

    print(STARTUP_COMPLETE_MESSAGE)
    print(f'{bot.user.name} is online! ID: {bot.user.id}')

@bot.event
async def on_guild_join(guild):
    print(f'Uniu-se a: {guild.name}')
    await register(guild)

async def register(guild):
    guild_to_settings[guild] = Settings(guild)
    guild_to_audiocontroller[guild] = AudioController(bot, guild)

    sett = guild_to_settings[guild]

    await guild.me.edit(nick=sett.get('default_nickname'))

    if GLOBAL_DISABLE_AUTOJOIN_VC == True:
        return
    
    voice_channels = guild.voice_channels

    if sett.get('vc_timeout') == False:
        if sett.get('start_voice_channel') == None:
            try:
                await guild_to_audiocontroller[guild].connect_to_voice_channel(guild.voice_channels[0])
            except Exception as e:
                print(e)
        else:
            for vc in voice_channels:
                if vc.id == sett.get('start_voice_channel'):
                    try:
                        await guild_to_audiocontroller[guild].connect_to_voice_channel(voice_channels[voice_channels.index(vc)])
                    except Exception as e:
                        print(e)


## General commands
@bot.command('help')
async def _help(ctx):
    """List of commands"""
    
    embed = discord.Embed(
        title = 'Comandos do Jaskier:',
        color = 0xf0e130
    )

    for cmd, msg in COMMANDS.items():
        embed.add_field(name=f'{PREFIX}{cmd}', value=f'{msg}', inline=False)
    
    await ctx.send(embed=embed)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"{str(error)}, use `{PREFIX} help` para mostrar os comandos disponíveis")
        return

    if isinstance(error, commands.ChannelNotFound):
        await ctx.send(str(error))
        return
    
    if isinstance(error, commands.CommandInvokeError):
        await ctx.send(str(error))
        return

    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("MissingRequiredArgument")
        return

    if isinstance(error, commands.NoPrivateMessage):
        await ctx.send(str(error))
        return

    await ctx.send(str(error))
    raise error


## Add cogs and run bot
bot.add_cog(General(bot, PREFIX))
bot.add_cog(Music(bot, PREFIX))
bot.run(TOKEN)