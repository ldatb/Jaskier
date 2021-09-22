import os
import json
import discord
from config import *

dir_path = os.path.dirname(os.path.realpath(__file__))

class Settings():
    def __init__(self, guild):
        self.guild = guild
        self.json_data = None
        self.config = None
        self.path = f'{dir_path}/generated/settings.json'

        self.settings_template = {
            "id": 0,
            "default_nickname": "",
            "button_emote": "",
            "default_volume": 100,
            "vc_timeout": VC_TIMEOUT_DEFAULT
        }

        self.reload()
        self.upgrade()

    async def write(self, setting, value, ctx):
        response = await self.process_setting(setting, value, ctx)

        with open(self.path, 'w') as source:
            json.dump(self.json_data, source)
        self.reload()
        return response
    
    def reload(self):
        with open(self.path, 'r') as source:
            self.json_data = json.load(source)

        target = None

        for server in self.json_data:
            server = self.json_data[server]

            if server['id'] == self.guild.id:
                target = server

        if target == None:
            self.create()
            return

        self.config = target
    
    def upgrade(self):
        refresh = False
        for key in self.settings_template.keys():
            if not key in self.config:
                self.config[key] = self.settings_template.get(key)
                refresh = True
        if refresh:
            self.reload()

    def create(self):

        self.json_data[self.guild.id] = self.settings_template
        self.json_data[self.guild.id]['id'] = self.guild.id

        with open(self.path, 'w') as source:
            json.dump(self.json_data, source)
        self.reload()

    def get(self, setting):
        return self.config[setting]
    
    async def format(self):
        embed = discord.Embed(
            title="Settings", description=self.guild.name, color=EMBED_COLOR)

        embed.set_thumbnail(url=self.guild.icon_url)
        embed.set_footer(
            text="Usage: {}set setting_name value".format(BOT_PREFIX))

        exclusion_keys = ['id']

        for key in self.config.keys():
            if key in exclusion_keys:
                continue

            if self.config.get(key) == "" or self.config.get(key) == None:

                embed.add_field(name=key, value="Not Set", inline=False)
                continue

            embed.add_field(name=key, value=self.config.get(key), inline=False)

        return embed

    async def process_setting(self, setting, value, ctx):

        switcher = {
            'default_nickname': lambda: self.default_nickname(setting, value, ctx),
            'button_emote': lambda: self.button_emote(setting, value, ctx),
            'default_volume': lambda: self.default_volume(setting, value, ctx),
            'vc_timeout': lambda: self.vc_timeout(setting, value, ctx),
        }
        func = switcher.get(setting)

        if func is None:
            return None
        else:
            answer = await func()
            if answer == None:
                return True
            else:
                return answer

    # -----setting methods-----

    async def default_nickname(self, setting, value, ctx):

        if value.lower() == "unset":
            self.config[setting] = ""
            return

        if len(value) > 32:
            await ctx.send("`Error: Nickname exceeds character limit`\nUsage: {}set {} nickname\nOther options: unset".format(BOT_PREFIX, setting))
            return False
        else:
            self.config[setting] = value
            await self.guild.me.edit(nick=value)

    async def button_emote(self, setting, value, ctx):

        if value.lower() == "unset":
            self.config[setting] = ""
            return

        emoji = discord.utils.get(self.guild.emojis, name=value)
        if emoji is None:
            await ctx.send("`Error: Emote name not found on server`\nUsage: {}set {} emotename\nOther options: unset".format(BOT_PREFIX, setting))
            return False
        else:
            self.config[setting] = value

    async def default_volume(self, setting, value, ctx):
        try:
            value = int(value)
        except:
            await ctx.send("`Error: Value must be a number`\nUsage: {}set {} 0-100".format(BOT_PREFIX, setting))
            return False

        if value > 100 or value < 0:
            await ctx.send("`Error: Value must be a number`\nUsage: {}set {} 0-100".format(BOT_PREFIX, setting))
            return False

        self.config[setting] = value

    async def vc_timeout(self, setting, value, ctx):

        if ALLOW_VC_TIMEOUT_EDIT == False:
            await ctx.send("`Error: This value cannot be modified".format(BOT_PREFIX, setting))

        if value.lower() == "true":
            self.config[setting] = True
            self.config['start_voice_channel'] = None
        elif value.lower() == "false":
            self.config[setting] = False
        else:
            await ctx.send("`Error: Value must be True/False`\nUsage: {}set {} True/False".format(BOT_PREFIX, setting))
            return False