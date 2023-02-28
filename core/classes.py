from discord.ext import commands
import json

class Cog_Extension(commands.Cog):
    def __init__(self , bot):
        self.bot = bot
        self.DB = bot.get_cog('MySQL')
        with open('settings.json' , 'r' , encoding = 'utf-8') as f:
            self.settings = json.load(f)