## Imports
import psutil
import distro
import platform
import discord
from app.utils import convert_size
from config import EMBED_COLOR, AUTHOR_DISCORD_NAME
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
        """Bot's latency"""

        await ctx.send(f'Pong! {round(self.bot.latency * 1000)}ms')
        return

    @commands.cooldown(rate=1, per=3, type=commands.BucketType.guild)
    @commands.guild_only()
    @commands.command('info')
    async def _info(self, ctx):
        """Bot's info"""

        python_version = platform.python_version()
        total_cpu = psutil.cpu_count(logical=False)
        cpu_usage = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory()
        total_ram = convert_size(ram.total)
        ram_usage = convert_size(ram.used)
        ram_usage_percent = ram.percent

        embed = discord.Embed(title = 'System Info', color = EMBED_COLOR)
        embed.add_field(name='OS', value=platform.system(), inline=True)
        embed.add_field(name='Distro', value=distro.linux_distribution(), inline=True)
        embed.add_field(name='CPU', value=f'{total_cpu} CPUs ({cpu_usage}%)', inline=False)
        embed.add_field(name='RAM', value=f'{ram_usage} / {total_ram} ({ram_usage_percent}%)', inline=False)
        embed.add_field(name='Python Version', value=python_version, inline=False)
        embed.set_footer(text='Criado por Lucas de Ataides')

        await ctx.send(embed=embed)
        return

    @commands.cooldown(rate=1, per=3, type=commands.BucketType.guild)
    @commands.guild_only()
    @commands.command('invite')
    async def _invite(self, ctx):
        """Info on how to invite the bot"""

        embed = discord.Embed(
            title = f'Para botar o Jaskier no seu servidor, fale com o {AUTHOR_DISCORD_NAME}',
            description = 'Como o Youtube vem limitando os bots de música, o Jaskier foi feito para contornar isso, então é preciso que o número de servidores em que ele está seja limitado.',
            color = EMBED_COLOR
        )

        await ctx.send(embed=embed)
        return