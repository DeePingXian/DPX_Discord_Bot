from core.classes import Cog_Extension
from discord.ext import commands , tasks
import time , uuid

class website(Cog_Extension):

    def __init__(self , bot):
        self.bot = bot
        self.DB = bot.get_cog('MySQL')

    #取得存取網頁之token

    @commands.command()
    async def getwebtoken(self , ctx):
        await ctx.send(f'目前存取網頁之 token：\n{self.DB.GetToken()}\ntoken 每天 UTC 0:00／CST 8:00 更新')

    #取得本 Discord 伺服器的 ID

    @commands.command()
    async def getguildid(self , ctx):
        await ctx.send(f'本伺服器ID：{ctx.guild.id}')

    #更新資料庫網頁存取token

    @commands.Cog.listener()
    async def on_ready(self):
        self.waitForUpdateToken.start()

    @tasks.loop(seconds=60)
    async def waitForUpdateToken(self):
        nowHour = time.gmtime().tm_hour
        nowMinute = time.gmtime().tm_min
        if nowHour == 0 and nowMinute >= 0 and nowMinute <= 1:
            self.updateToken.start()
            self.waitForUpdateToken.stop()

    @tasks.loop(hours=24)
    async def updateToken(self):
        self.DB.UpdateToken(str(uuid.uuid4())[:8])

def setup(bot):
    bot.add_cog(website(bot))