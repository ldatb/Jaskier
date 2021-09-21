
# Youtube-DL config
YTDL_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noPlaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto'
}

# FFMPEG config
FFMPEG_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

# YTDL Class for streaming
YTDL = youtube_dl.YoutubeDL(YTDL_options)
class YTDLsource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: YTDL.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['title'] if stream else YTDL.prepare_filename(data)
        return filename

# Commands
class MusicPlayer(commands.Cog):
    def __init__(self, bot, prefix):
        # Discord related
        self.bot = bot
        self.prefix = prefix

    async def join_or_move(self, ctx):

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

        VOICE_CLIENT = ctx.voice_client
        try:
            if not VOICE_CLIENT:
                await channel.connect(timeout=10.0, reconnect=False)

        except asyncio.TimeoutError:
            await ctx.send(f'Falha ao conectar-se a: <**{channel}**> `Erro de conexão: tempo limite esgotado`, certifique-se de que o bot tem uma *função* para ser capaz de entrar no <**{channel}**>, se ainda falhar, tente alterando a região do seu canal de voz. "')
            return

        except Exception as err:
            print(f"join_or_move on {channel}, {err}")
            await ctx.send(f'Falha ao conectar-se a: <**{channel}**>, Certifique-se de que o bot tem uma *função* para ser capaz de entrar no <**{channel}**>, se ainda falhar, tente alterando a região do seu canal de voz. "')
            return

    @commands.cooldown(rate=1, per=3, type=commands.BucketType.guild)
    @commands.guild_only()
    @commands.command('play')
    async def _play(self, ctx, *, url):

        await self.join_or_move(ctx)

        voice = ctx.message.guild.voice_client

        async with ctx.typing():
            player = await YTDLsource.from_url(url, loop=self.bot.loop, stream=True)
            voice.play(discord.FFmpegPCMAudio(player), after=lambda e: print('Player error: %s' % e) if e else None)

        await ctx.send('Tocando: `{}`'.format(player.title))