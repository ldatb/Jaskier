## Imports
import discord
from discord.ext import commands

## Commands
class General(commands.Cog):
    def __init__(self, bot, prefix):
        self.bot = bot
        self.prefix = prefix

    @commands.cooldown(rate=1, per=3, type=commands.BucketType.guild)
    @commands.guild_only()
    @commands.command('ping')
    async def _ping(self, ctx):
        """Latência do bot"""

        await ctx.send(f'Pong! {round(self.bot.latency * 1000)}ms')
        return
