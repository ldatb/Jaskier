import asyncio
from config import *
from app.utils import guild_to_settings


async def connect_to_channel(guild, destiny_channel, ctx, switch=False, default=True):
    """
    Connects the bot to the specified voice channel.
        Args:
            guild: The guild for witch the operation should be performed.
            switch: Determines if the bot should disconnect from his current channel to switch channels.
            default: Determines if the bot should default to the first channel, if the name was not found.
    """

    for channel in guild.voice_channels:
        if str(channel.name).strip() == str(destiny_channel).strip():
            if switch:
                try:
                    await guild.voice_client.disconnect()
                except:
                    await ctx.send(NOT_CONNECTED_MESSAGE)
            
            await channel.connect()
            return
        
        if default:
            try:
                await guild.voice_channels[0].connect()
            except:
                await ctx.send(DEFAULT_CHANNEL_JOIN_FAILED)
        else:
            await ctx.send(CHANNEL_NOT_FOUND_MESSAGE + str(destiny_channel))

async def is_connected(ctx):
    try:
        voice_channel = ctx.guild.voice_client.channel
        return voice_channel
    except:
        return None

async def play_check(ctx):
    author_voice = ctx.message.author.voice
    if author_voice == None:
        await ctx.send(USER_NOT_IN_VC_MESSAGE)
        return False
    else:
        return True

async def check_channel(ctx):
    author_voice = ctx.message.author.voice.channel
    voice_channel = ctx.guild.voice_client.channel

    if not voice_channel:
        return True
    elif author_voice != voice_channel:
        await ctx.send(DIFFERENT_VOICE_CHANNEL)
        return False
    else:
        return True

class Timer:
    def __init__(self, callback):
        self._callback = callback
        self._task = asyncio.create_task(self._job())

    async def _job(self):
        await asyncio.sleep(VC_TIMEOUT)
        await self._callback()

    def cancel(self):
        self._task.cancel()