# Imports
import asyncio
import discord
from discord.ext import commands
from .utils import is_valid_url

# Commands
class MusicPlayer(commands.Cog):
    def __init__(self, bot, prefix):
        self.bot = bot
        self.prefix = prefix

    async def join_or_move(self, ctx, channel):
        VOICE_CLIENT = ctx.voice_client
        try:
            if not VOICE_CLIENT:
                await ctx.guild.change_voice_state(channel=channel, self_deaf=True)
                #await channel.connect(timeout=10.0, reconnect=False)
        except asyncio.TimeoutError:
            await ctx.send(f'Falha ao conectar-se a: <**{channel}**> `Erro de conexão: tempo limite esgotado`, certifique-se de que o bot tem uma *função* para ser capaz de entrar no <**{channel}**>, se ainda falhar, tente alterando a região do seu canal de voz. "')
            return
        except Exception as err:
            print(f"join_or_move on {channel}, {err}")
            await ctx.send(f'Falha ao conectar-se a: <**{channel}**>, Certifique-se de que o bot tem uma *função* para ser capaz de entrar no <**{channel}**>, se ainda falhar, tente alterando a região do seu canal de voz. "')
            return

    @commands.cooldown(rate=1, per=3, type=commands.BucketType.guild)
    @commands.guild_only()
    @commands.command(name="join")
    async def _join(self, ctx):
        """
        Joins a voice channel
        Params:
        - channel: discord.VoiceChannel [Optional]
            The channel to connect to. If a channel is not specified, an attempt to join the voice channel you are in
            will be made.
        """

        try:
            channel = ctx.author.voice.channel
        except AttributeError:
            await ctx.send('Você precisa estar em um canal de voz primeiro.')
            return

        perms = channel.permissions_for(ctx.guild.me)
        if perms.connect is False:
            await ctx.send(f'Falha ao conectar no <**{channel}**>, certifique-se de que o bot tem a *função* certa para poder entrar no <**{channel}**>.')
            return

        if perms.speak is False:
            await ctx.send(f'O bot não tem uma *função* para falar no <**{channel}**>, certifique-se de que o bot tem a **função** certa para poder falar no <**{channel}**>.')
            return

        await self.join_or_move(ctx, channel)
        return