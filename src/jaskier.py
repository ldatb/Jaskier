## Imports
import json
import asyncio
from sys import executable
import youtube_dl
import discord
from discord.ext import commands, tasks
from discord.flags import Intents

## Get Secret Token
with open("secrets.json") as f:
    secrets = json.load(f)
    token = secrets["token"]

## Bot instance
description = 'Toss a coin yo your witcher'
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=commands.when_mentioned_or("j.")
                        ,description=description
                        ,Intents=intents)

## Youtube DL config
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'extractaudio': True,
    'audioformat': 'mp3',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = ""

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
        filename = data['title'] if stream else ytdl.prepare_filename(data)
        return filename

## Simple Commands
class Text(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def ping(ctx):
        """Simple ping"""

        await ctx.send(f'Pong! {round(bot.latency * 1000)}ms')

## Voice Commands
class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='join', help='Tells the bot to join the voice channel')
    async def join(self, ctx):
        if not ctx.message.author.voice:
            await ctx.send("Você não está conectado em um canal de voz.")
            return
        else:
            channel = ctx.message.author.voice.channel
            await channel.connect()

    @commands.command(name='leave', help='Tells the bot leave the voice channel')
    async def leave(self, ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client:
            await voice_client.disconnect()
        else:
            await ctx.send("Eu não estou conectado a nenhum canal de voz.")

    @commands.command(name='play', help='Play a song from youtube')
    async def play(self, ctx, url):
        try:
            channel = ctx.message.author.voice.channel

            # Check if the bot is in the channel and connect it
            voice_client = ctx.message.guild.voice_client
            if not voice_client:
                await channel.connect()
            
            await ctx.send(url)
            
        except:
            await ctx.send("Você não está conectado em um canal de voz.")

## Login
@bot.event
async def on_ready():
    print('Logged in as:')
    print(bot.user.name)
    print(bot.user.id)
    print('-------')

## Add cogs
bot.add_cog(Text(bot))
bot.add_cog(Music(bot))

## Run bot
bot.run(token)