## Libraries imports
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv()

## App imports
from app.extras import Extras
from app.music import MusicPlayer
from app.static import COMMANDS

## Get Discord API Token
DESCRIPTION = 'Toss a coin to your witcher'
INTENTS = discord.Intents.all()
PREFIX = "j!"
TOKEN = os.getenv("DISCORD_TOKEN")
bot = commands.Bot(
        command_prefix=commands.when_mentioned_or(PREFIX),
        description=DESCRIPTION,
        Intents=INTENTS,
        help_command=None
)

## Events
@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected.')
    await bot.change_presence(activity = discord.Activity(
        type=discord.ActivityType.listening,
        name=f'{PREFIX}help'
    ))

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
bot.add_cog(Extras(bot, PREFIX))
bot.add_cog(MusicPlayer(bot, PREFIX))
bot.run(TOKEN)