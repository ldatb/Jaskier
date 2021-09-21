import discord
from discord.ext import commands
import asyncio
import datetime

import app.utils as utils
import app.link_utils as link_utils
import app.music_utils as music_utils
from config import *


class Music(commands.Cog):
    def __init__(self, bot, prefix):
        self.bot = bot
        self.prefix = prefix

    @commands.cooldown(rate=1, per=3, type=commands.BucketType.guild)
    @commands.guild_only()
    @commands.command(name='play', aliases=['p', 'pl', 'tocar'])
    async def _play_song(self, ctx, *, track: str):
        guild = utils.get_guild(self.bot, ctx.message)
        audiocontroller = utils.guild_to_audiocontroller[guild]

        if (await music_utils.is_connected(ctx) == None):
            if await audiocontroller.uConnect(ctx) == False:
                return
        
        if track.isspace() or not track:
            return
        
        if await music_utils.play_check(ctx) == False:
            return
        
        # Reset timer
        audiocontroller.timer.cancel()
        audiocontroller.timer = music_utils.Timer(audiocontroller.timeout_handler)

        if audiocontroller.playlist.loop == True:
            await ctx.send(f'Loop ativado! Use {BOT_PREFIX}loop para desativar')
            return
        
        song = await audiocontroller.process_song(track)

        if song is None:
            await ctx.send(SONGINFO_UNKNOWN_SITE)
            return
        
        if song.origin == link_utils.Origins.Default:
            if audiocontroller.current_song != None and len(audiocontroller.playlist.queue) == 0:
                await ctx.send(embed=song.info.format_output(SONGINFO_NOW_PLAYING))
            else:
                await ctx.send(embed=song.info.format_output(SONGINFO_QUEUE_ADDED))
        
        elif song.origin == link_utils.Origins.Playlist:
            await ctx.send(SONGINFO_PLAYLIST_QUEUED)

    @commands.cooldown(rate=1, per=3, type=commands.BucketType.guild)
    @commands.guild_only()
    @commands.command(name='loop', aliases=['l'])
    async def _loop(self, ctx):
        guild = utils.get_guild(self.bot, ctx.message)
        audiocontroller = utils.guild_to_audiocontroller[guild]

        if await music_utils.play_check(ctx) == False:
            return
        
        if len(audiocontroller.playlist.queue) < 1 and guild.voice_client.is_playing() == False:
            await ctx.send('Não há nenhuma música na fila!')
            return
        
        if audiocontroller.playlist.loop == False:
            audiocontroller.playlist.loop = True
            await ctx.send('Loop ativado! :arrows_counterclockwise:')
        else:
            audiocontroller.playlist.loop = False
            await ctx.send('Loop desativado! :x:')

    @commands.cooldown(rate=1, per=3, type=commands.BucketType.guild)
    @commands.guild_only()
    @commands.command(name='shuffle', aliases=['s', 'sh', 'embaralhar'])
    async def _shuffle(self, ctx):
        guild = utils.get_guild(self.bot, ctx.message)
        audiocontroller = utils.guild_to_audiocontroller[guild]

        if await music_utils.play_check(ctx) == False:
            return

        if guild.voice_client is None or not guild.voice_client.is_playing():
            await ctx.send('A fila está vazia :x:')
            return
        
        audiocontroller.playlist.shuffle()
        await ctx.send('Playlist embaralhada! :twisted_rightwards_arrows:')

        for song in list(audiocontroller.playlist.queue)[:MAX_SONG_PRELOAD]:
            asyncio.ensure_future(audiocontroller.preload(song))

    @commands.cooldown(rate=1, per=3, type=commands.BucketType.guild)
    @commands.guild_only()
    @commands.command(name='pause', aliases=['pausar'])
    async def _pause(self, ctx):
        guild = utils.get_guild(self.bot, ctx.message)
        
        if await music_utils.play_check(ctx) == False:
            return
        
        if guild.voice_client is None or not guild.voice_client.is_playing():
            return
        
        guild.voice_client.pause()
        await ctx.send('Pausado :pause_button')

    @commands.cooldown(rate=1, per=3, type=commands.BucketType.guild)
    @commands.guild_only()
    @commands.command(name='queue', aliases=['q', 'playlist', 'fila'])
    async def _queue(self, ctx):
        guild = utils.get_guild(self.bot, ctx.message)

        if await music_utils.play_check(ctx) == False:
            return

        if guild.voice_client is None or not guild.voice_client.is_playing():
            await ctx.send("A fila está vazia :x:")
            return

        playlist = music_utils.guild_to_audiocontroller[guild].playlist

        # Embeds are limited to 25 fields
        if MAX_SONG_PRELOAD > 25:
            _MAX_SONG_PRELOAD = 25
        else:
            _MAX_SONG_PRELOAD = MAX_SONG_PRELOAD

        embed = discord.Embed(title=":scroll: Fila [{}]".format(
            len(playlist.queue)), color=EMBED_COLOR, inline=False)

        for counter, song in enumerate(list(playlist.queue)[:_MAX_SONG_PRELOAD], start=1):
            if song.info.title is None:
                embed.add_field(name="{}.".format(str(counter)), value="[{}]({})".format(
                    song.info.webpage_url, song.info.webpage_url), inline=False)
            else:
                embed.add_field(name="{}.".format(str(counter)), value="[{}]({})".format(
                    song.info.title, song.info.webpage_url), inline=False)

        await ctx.send(embed=embed)

    @commands.cooldown(rate=1, per=3, type=commands.BucketType.guild)
    @commands.guild_only()
    @commands.command(name='stop', aliases=['st', 'parar'])
    async def _stop(self, ctx):
        guild = utils.get_guild(self.bot, ctx.message)

        if await music_utils.play_check(ctx) == False:
            return

        audiocontroller = utils.guild_to_audiocontroller[guild]
        audiocontroller.playlist.loop = False

        await music_utils.guild_to_audiocontroller[guild].stop_player()
        await ctx.send('Parando todas as sessões :octagonal_sign:')

    @commands.cooldown(rate=1, per=3, type=commands.BucketType.guild)
    @commands.guild_only()
    @commands.command(name='skip', aliases=['sk', 'pular', 'proxima', 'próxima'])
    async def _skip(self, ctx):
        guild = utils.get_guild(self.bot, ctx.message)

        if await music_utils.play_check(ctx) == False:
            return

        audiocontroller = utils.guild_to_audiocontroller[guild]
        audiocontroller.playlist.loop = False

        if guild.voice_client is None or (not guild.voice_client.is_paused() and not guild.voice_client.is_playing()):
            return
        
        guild.voice_client.stop()
        await ctx.send('Pulando a música atual :fast_forward:')
    
    @commands.cooldown(rate=1, per=3, type=commands.BucketType.guild)
    @commands.guild_only()
    @commands.command(name='clear', aliases=['cl', 'limpar'])
    async def _clear(self, ctx):
        guild = utils.get_guild(self.bot, ctx.message)

        if await music_utils.play_check(ctx) == False:
            return

        audiocontroller = utils.guild_to_audiocontroller[guild]
        audiocontroller.clear_queue()
        audiocontroller.playlist.loop = False
        guild.voice_client.stop()
        
        await ctx.send('Fila esvaziada :no_entry_sign:')
    
    @commands.cooldown(rate=1, per=3, type=commands.BucketType.guild)
    @commands.guild_only()
    @commands.command(name='prev', aliases=['back', 'anterior'])
    async def _prev(self, ctx):
        guild = utils.get_guild(self.bot, ctx.message)

        if await music_utils.play_check(ctx) == False:
            return

        audiocontroller = utils.guild_to_audiocontroller[guild]
        audiocontroller.playlist.loop = False
        audiocontroller.timer.cancel()
        audiocontroller.timer = music_utils.Timer(audiocontroller.timeout_handler)

        await music_utils.guild_to_audiocontroller[guild].prev_song()
        await ctx.send("Tocando a música anterior :track_previous:")
    
    @commands.cooldown(rate=1, per=3, type=commands.BucketType.guild)
    @commands.guild_only()
    @commands.command(name='resume', aliases=['retomar'])
    async def _resume(self, ctx):
        guild = utils.get_guild(self.bot, ctx.message)

        if await music_utils.play_check(ctx) == False:
            return

        guild.voice_client.resume()
        await ctx.send("Voltando a tocar :arrow_forward:")

    @commands.cooldown(rate=1, per=3, type=commands.BucketType.guild)
    @commands.guild_only()
    @commands.command(name='songinfo', aliases=['si', 'np', 'musica'])
    async def _songinfo(self, ctx):
        guild = utils.get_guild(self.bot, ctx.message)

        if await music_utils.play_check(ctx) == False:
            return
        
        song = music_utils.guild_to_audiocontroller[guild].current_song

        if song is None:
            return

        await ctx.send(embed=song.info.format_output(SONGINFO_SONGINFO))

    @commands.cooldown(rate=1, per=3, type=commands.BucketType.guild)
    @commands.guild_only()
    @commands.command(name='history', aliases=['historico'])
    async def _history(self, ctx):
        guild = utils.get_guild(self.bot, ctx.message)

        if await music_utils.play_check(ctx) == False:
            return
        
        await ctx.send(music_utils.guild_to_audiocontroller[guild].track_history())

    @commands.cooldown(rate=1, per=3, type=commands.BucketType.guild)
    @commands.guild_only()
    @commands.command(name='volume', aliases=['vol'])
    async def _volume(self, ctx, *args):
        guild = utils.get_guild(self.bot, ctx.message)
        
        if len(args) == 0:
            await ctx.send('Volume atual: {} :speaker:'.format(music_utils.guild_to_audiocontroller[guild]._volume))
            return
        
        try:
            volume = args[0]
            volume = int(volume)

            if volume > 100:
                raise Exception('')
            
            if music_utils.guild_to_audiocontroller[guild]._volume >= volume:
                await ctx.send('Volume diminuido para {}% :sound:'.format(str(volume)))
            else:
                await ctx.send('Volume aumentado para {}% :loud_sound:'.format(str(volume)))
            
            music_utils.guild_to_audiocontroller[guild].volume = volume
        except:
            await ctx.send('O volume deve ser um valor entre 1 e 100')
        