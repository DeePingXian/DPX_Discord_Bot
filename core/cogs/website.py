from core.classes import Cog_Extension
from discord.ext import commands , tasks
import time

class website(Cog_Extension):

    #更新資料庫網頁存取token

    @commands.Cog.listener()
    async def on_ready(self):
        self.DB.updateAllToken()
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
        self.DB.updateAllToken()

async def setup(bot):
    await bot.add_cog(website(bot))