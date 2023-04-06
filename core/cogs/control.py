import discord
from discord.ext import commands , tasks
from core.classes import Cog_Extension

class control(Cog_Extension):

    #bot狀態回報

    @commands.command()
    async def status(self , ctx):
        if ctx.author.id == self.settings['adminID']:
            DBStatus = ''
            if self.DB.test():
                DBStatus = '正常'
            else:
                DBStatus = '錯誤'
            ping = round (self.bot.latency * 1000)   
            embed = discord.Embed(title="bot 狀態一覽", description='\u200b' , color=0xc0c0c0)
            embed.set_author(name="DPX discord bot" , url=None , icon_url=self.settings['BotIconUrl'])
            embed.add_field(name="類別", value='與 Discord 網路延遲\nMySQL 操作狀態' , inline=True)
            embed.add_field(name="狀態", value=f'{ping} ms\n{DBStatus}' , inline=True)
            await ctx.send(embed=embed)
        else:
            await ctx.reply('此功能僅限開此bot的管理員使用')

    #log

    @commands.Cog.listener()
    async def on_ready(self):
        self.autoLog.start()

    @tasks.loop(hours=1)
    async def autoLog(self):
        await self.log()

    async def log(self):
        channel = self.bot.get_channel(self.settings['log_channel_id'])
        word = f'與 Discord 延遲為 {round(self.bot.latency * 1000)} ms'
        if self.DB.test():
            word += '\nMySQL 操作正常'
        else:
            word += '\nMySQL 操作錯誤'
        await channel.send(word)

async def setup(bot):
    await bot.add_cog(control(bot))