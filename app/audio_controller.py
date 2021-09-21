import discord
import youtube_dl
import asyncio
from concurrent.futures import ThreadPoolExecutor

import app.utils as utils
import app.link_utils as link_utils
import app.music_utils as music_utils
from app.song_info import Song
from app.playlist import Playlist
from config import *


YTDL_Config = {
    'format': 'bestaudio/best',
    'title': True,
    'restrictfilenames': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto'
}
YTDL_Config_no_audio = {
    'title': True,
    'restrictfilenames': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto'
}


class AudioController(object):
    """ 
    Controls the playback of audio and the sequential playing of the songs.
    Attributes:
        bot: The instance of the bot that will be playing the music.
        playlist: A Playlist object that stores the history and queue of songs.
        current_song: A Song object that stores details of the current song.
        guild: The guild in which the Audiocontroller operates.
    """

    def __init__(self, bot, guild):
        self.bot = bot
        self.playlist = Playlist()
        self.current_song = None
        self.guild = guild
        self.voice_client = None

        sett = utils.guild_to_settings[guild]
        self._volume = sett.get('default_volume')

        self.timer = music_utils.Timer(self.timeout_handler)
    
    @property
    def volume(self):
        return self._volume
    
    @volume.setter
    def volume(self, value):
        self._volume = value
        try:
            self.voice_client.source.volume = float(value) / 100.0
        except:
            pass
    
    async def connect_to_voice_channel(self, channel):
        self.voice_client = await channel.connect(reconnect=True, timeout=10.0)

    def track_history(self):
        history = INFO_HISTORY_TITLE
        for trackname in self.playlist.trackname_history:
            history += '\n' + trackname
        return history
    
    def next_song(self, error):
        """
        Invoked after a song is finished. Plays the next song if there is one.
        """

        next_song = self.playlist.next(self.current_song)
        self.current_song = None
        
        if next_song is None:
            return
        
        play_next = self.play_song(next_song)
        self.bot.loop.create_task(play_next)

    async def play_song(self, song):
        if song.info.title == None:
            if song.host == link_utils.Sites.Spotify:
                conversion = self.search_youtube(await link_utils.convert_spotify(song.info.webpage_url))
                song.info.webpage_url = conversion

            downloader = youtube_dl.YoutubeDL(YTDL_Config)
            song_request = downloader.extract_info(song.info.webpage_url, download=False)

            song.base_url = song_request.get('url')
            song.info.uploader = song_request.get('uploader')
            song.info.title = song_request.get('title')
            song.info.duration = song_request.get('duration')
            song.info.webpage_url = song_request.get('webpage_url')
            song.info.thumbnail = song_request.get('thumbnails')[0]['url']

        self.playlist.add_name(song.info.title)
        self.current_song = song
        self.playlist.history.append(self.current_song)

        self.voice_client.play(discord.FFmpegPCMAudio(
            song.base_url,
            before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'),
            after=lambda e: self.next_song(e)
        )
        self.voice_client.source = discord.PCMVolumeTransformer(self.guild.voice_client.source)
        self.voice_client.source.volume = float(self.volume) / 100.0

        self.playlist.queue.popleft()

        for song in list(self.playlist.queue)[:MAX_SONG_PRELOAD]:
            asyncio.ensure_future(self.preload(song))

    async def process_song(self, track):
        """
        Adds the track to the playlist instance and plays it, if it is the first song
        """

        host = link_utils.identify_url(track)
        is_playlist = link_utils.identify_playlist(track)

        if is_playlist != link_utils.Playlist_Types.Unknown:
            await self.process_playlist(is_playlist, track)

            if self.current_song == None:
                await self.play_song(self.playlist.queue[0])
                print('Tocando: {}'.format(track))

            song = Song(link_utils.Origins.Playlist, link_utils.Sites.Unknown)
            return song
        
        if host == link_utils.Sites.Unknown:
            if link_utils.get_url(track) is not None:
                return None
            
            track =  self.search_youtube(track)
        
        if host == link_utils.Sites.Spotify:
            title = await link_utils.convert_spotify(track)
            track = self.search_youtube(track)

        if host == link_utils.Sites.YouTube:
            track = track.split('&list=')[0]

        try:
            downloader = youtube_dl.YoutubeDL(YTDL_Config)
            song_request = downloader.extract_info(track, download=False)
        except:
            downloader = youtube_dl.YoutubeDL(YTDL_Config_no_audio)
            song_request = downloader.extract_info(track, download=False)

        if song_request.get('thumbnails') is not None:
            thumbnail = song_request.get('thumbnails')[len(song_request.get('thumbnails')) - 1]['url']
        else:
            thumbnail = None

        song = Song(
            host=host,
            origin=link_utils.Origins.Default,
            base_url=song_request.get('url'),
            uploader=song_request.get('uploader'),
            title=song_request.get('title'),
            duration=song_request.get('duration'),
            webpage_url=song_request.get('webpage_url'),
            thumbnail=thumbnail
        )

        self.playlist.add(song)

        if self.current_song == None:
            await self.play_song(song)

        return song

    async def process_playlist(self, playlist_type, url):

        if playlist_type == link_utils.Playlist_Types.YouTube_Playlist:

            if ("playlist?list=" in url):
                listid = url.split('=')[1]
            else:
                video = url.split('&')[0]
                await self.process_song(video)
                return

            with youtube_dl.YoutubeDL(YTDL_Config) as ydl:
                playlist_request = ydl.extract_info(url, download=False)

                for entry in playlist_request['entries']:

                    link = "https://www.youtube.com/watch?v={}".format(
                        entry['id'])

                    song = Song(
                        link_utils.Origins.Playlist,
                        link_utils.Sites.YouTube,
                        webpage_url=link
                    )

                    self.playlist.add(song)

        if playlist_type == link_utils.Playlist_Types.Spotify_Playlist:
            links = await link_utils.get_spotify_playlist(url)
            for link in links:
                song = Song(
                    link_utils.Origins.Playlist,
                    link_utils.Sites.Spotify,
                    webpage_url=link
                )
                
                self.playlist.add(song)

        if playlist_type == link_utils.Playlist_Types.BandCamp_Playlist:
            options = {
                'format': 'bestaudio/best',
                'extract_flat': True
            }
            with youtube_dl.YoutubeDL(options) as ydl:
                playlist_request = ydl.extract_info(url, download=False)

                for entry in playlist_request['entries']:

                    link = entry.get('url')

                    song = Song(
                        link_utils.Origins.Playlist,
                        link_utils.Sites.Bandcamp,
                        webpage_url=link
                    )

                    self.playlist.add(song)

        for song in list(self.playlist.queue)[:MAX_SONG_PRELOAD]:
            asyncio.ensure_future(self.preload(song))

    async def preload(self, song):
        if song.info.title != None:
            return
        
        def download(song):
            if song.host == link_utils.Sites.Spotify:
                song.info.webpage_url = self.search_youtube(song.info.title)
            
            downloader = youtube_dl.YoutubeDL(YTDL_Config)
            song_request = downloader.extract_info(song.info.webpage_url, download=False)

            song.base_url = song_request.get('url')
            song.info.uploader = song_request.get('uploader')
            song.info.title = song_request.get('title')
            song.info.duration = song_request.get('duration')
            song.info.webpage_url = song_request.get('webpage_url')
            song.info.thumbnail = song_request.get('thumbnails')[0]['url']

        if song.host == link_utils.Sites.Spotify:
            song.info.title = await link_utils.convert_spotify(song.info.webpage_url)

        loop = asyncio.get_event_loop()
        executor = ThreadPoolExecutor(max_workers=MAX_SONG_PRELOAD)
        await asyncio.wait(
            fs={loop.run_in_executor(executor, download, song)},
            return_when=asyncio.ALL_COMPLETED
        )

    def search_youtube(self, title):
        """
        Searches youtube for the video title and returns the first results video link
        """

        # If title is already a link
        if link_utils.get_url(title) is not None:
            return title

        with youtube_dl.YoutubeDL(YTDL_Config) as ydl:
            song_request = ydl.extract_info(title, download=False)
        
        videocode = song_request['entries'][0]['id']
        return "https://www.youtube.com/watch?v={}".format(videocode)

    async def stop_player(self):
        """
        Stops the player and removes all songs from the queue
        """

        if self.guild.voice_client is None or (not self.guild.voice_client.is_paused() and not self.guild.voice_client.is_playing()):
            return
        
        self.playlist.next(self.current_song)
        self.playlist.queue.clear()
        self.guild.voice_client.stop()

    async def prev_song(self):
        """
        Loads the last song from the history into the queue and starts it
        """

        if len(self.playlist.history) == 0:
            return

        prev_song = self.playlist.prev(self.current_song)

        if not self.guild.voice_client.is_playing() and not self.guild.voice_client.is_paused():
            if prev_song == "Dummy":
                self.playlist.next(self.current_song)
                return None
            await self.play_song(prev_song)
        else:
            self.guild.voice_client.stop()

    def clear_queue(self):
        self.playlist.queue.clear()

    async def timeout_handler(self):
        if len(self.guild.voice_client.channel.voice_states) == 1:
            await self.udisconnect()
            return

        sett = music_utils.guild_to_settings[self.guild]

        if sett.get('vc_timeout') == False:
            self.timer = music_utils.Timer(self.timeout_handler)  # restart timer
            return

        if self.guild.voice_client.is_playing():
            self.timer = music_utils.Timer(self.timeout_handler)  # restart timer
            return

        self.timer = music_utils.Timer(self.timeout_handler)
        await self.udisconnect()

    async def uConnect(self, ctx):
        if not ctx.author.voice:
            await ctx.send(USER_NOT_IN_VC_MESSAGE)
            return False
        
        voice_channel = await music_utils.is_connected(ctx.author.voice.channel)

        if voice_channel is not None:
            await ctx.send(ALREADY_CONNECTED_MESSAGE)
            return
        
        await self.connect_to_voice_channel(ctx.author.voice.channel)
    
    async def uDisconnect(self):
        await self.stop_player()
        await self.guild.voice_client.disconnect(force=True)