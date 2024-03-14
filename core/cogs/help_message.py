import discord
from discord.ext import commands
from core.classes import Cog_Extension

class help_message(Cog_Extension):

    def __init__(self , bot):
        super().__init__(bot)
        self.pf = self.settings['commandPrefix']

    class helpMessageMenu(discord.ui.View):
        
        def __init__(self , bot , settings , pf , DB):
            super().__init__(timeout=60)
            self.bot = bot
            self.settings = settings
            self.pf = pf
            self.DB = DB

        @discord.ui.select(
            placeholder = "請選擇查詢類別" , min_values = 1 , max_values = 1 ,
            options = [
                discord.SelectOption(
                    label="播音樂功能列表"
                ),
                discord.SelectOption(
                    label="訊息歷史紀錄功能列表"
                ),                
                discord.SelectOption(
                    label="應答機功能列表"
                ),
                discord.SelectOption(
                    label="產生連結功能列表"
                ),
                discord.SelectOption(
                    label="本 bot 附屬網頁相關"
                ),
                discord.SelectOption(
                    label="其他功能列表"
                )
            ]
        )

        async def select_callback(self , interaction , select):
            if select.values[0] == "播音樂功能列表":
                embed = discord.Embed(title="播音樂功能列表", description='\u200b' , color=0xc0c0c0)
                embed.set_author(name=self.bot.user.name , icon_url=self.bot.user.avatar.url)
                embed.add_field(name="指令", value=f"{self.pf}play + (網址)\n{self.pf}playlocal + (音樂檔案路徑)\n\n{self.pf}add + (網址)\n{self.pf}addlocal + (音樂檔案路徑)\n\n{self.pf}pause\n{self.pf}resume\n{self.pf}skip\n{self.pf}loop\n{self.pf}stop\n{self.pf}queue\n{self.pf}nowplaying\n{self.pf}download\n{self.pf}join" , inline=True)
                embed.add_field(name="功能", value="播放該音樂\n播放該本機音樂\n（僅限開bot的管理員使用）\n增加該音樂至播放隊列\n增加該本機音樂至播放隊列\n（僅限開bot的管理員使用）\n暫停播放\n恢復播放\n跳過目前曲目\n單曲重複播放\n停止播放 並清除音樂資料\n查看播放隊列\n查看現正播放\n下載現正播放的音樂\n加入用戶所在語音頻道" , inline=True)
                embed.add_field(name='\u200b', value='\u200b' , inline=False)
                embed.add_field(name="支援類型", value="來源\n\n\n播放隊列上限\nGoogle雲端單檔大小上限\nGoogle雲端音訊檔案容器" , inline=True)
                acceptableMusicContainer = ''
                for i in self.settings["musicBotOpts"]["googleDrive"]["acceptableMusicContainer"]:
                    acceptableMusicContainer += i
                    if i != self.settings["musicBotOpts"]["googleDrive"]["acceptableMusicContainer"][-1]:
                        acceptableMusicContainer += ' '
                embed.add_field(name='\u200b', value=f"YouTube影片、直播、播放清單、合輯\nGoogle雲端檔案\nbilibili影片、影片列表(beta)\n{self.settings['musicBotOpts']['maxQueueLen']}\n{self.settings['musicBotOpts']['googleDrive']['fileSizeLimitInMB']}MB\n{acceptableMusicContainer}" , inline=True)
                embed.add_field(name='\u200b', value=f"播放B站影片時受限於機制，bot反應會較慢\n如果播音樂發生問題，請使用{self.pf}stop清除資料，並再重新操作一次，實在不行請重啟bot" , inline=False)
            elif select.values[0] == "訊息歷史紀錄功能列表":
                embed = discord.Embed(title="訊息歷史紀錄功能列表", description='\u200b' , color=0xc0c0c0)
                embed.set_author(name=self.bot.user.name , icon_url=self.bot.user.avatar.url)
                embed.add_field(name="指令", value=f"{self.pf}history\n{self.pf}historyf + (數字)\n{self.pf}historyflist\n{self.pf}historyall + (數字 數字 數字)" , inline=True)
                embed.add_field(name="功能", value="查詢最近25則修改的文字訊息\n回傳前第n個被刪除的檔案訊息\n回傳已刪除的附件檔案列表\n匯出欲查詢的的文字訊息類型總集之Excel檔，0=未編輯、刪除的訊息，1=編輯，2=刪除，只輸入欲查詢的類型數字即可" , inline=True)
            elif select.values[0] == "應答機功能列表":
                embed = discord.Embed(title="應答機功能列表", description='\u200b' , color=0xc0c0c0)
                embed.set_author(name=self.bot.user.name , icon_url=self.bot.user.avatar.url)
                embed.add_field(name="指令", value=f'{self.pf}sendansweringcontentlist\n{self.pf}editansweringcontentlist' , inline=True)
                embed.add_field(name="功能", value='傳送應答列表\n修改應答列表（請附上應答列表檔案）' , inline=True)
                embed.add_field(name='\u200b', value='若訊息符合設定條件，bot會回傳設定的訊息內容\n修改訊息附件檔案須請開bot的管理員操作' , inline=False)
            elif select.values[0] == "產生連結功能列表":
                embed = discord.Embed(title="產生連結功能列表", description='\u200b' , color=0xc0c0c0)
                embed.set_author(name=self.bot.user.name , icon_url=self.bot.user.avatar.url)
                embed.add_field(name="指令", value=f'{self.pf}nh rand\n{self.pf}nh + (車號)\n{self.pf}jm + (車號)\n{self.pf}wn + (車號)\n{self.pf}pix + (作品號)\n{self.pf}pixu + (作者號)\n{self.pf}twiu + (用戶ID)' , inline=True)
                embed.add_field(name="功能", value='隨機傳送nh本子連結\n傳送該nh本子連結\n傳送該JM本子連結\n傳送該wnacg本子連結\n傳送該pixiv作品連結\n傳送該pixiv作者連結\n傳送該twitter用戶連結' , inline=True)
            elif select.values[0] == "本 bot 附屬網頁相關":
                embed = discord.Embed(title="本 bot 附屬網頁相關", description='\u200b' , color=0xc0c0c0)
                embed.set_author(name=self.bot.user.name , icon_url=self.bot.user.avatar.url)
                if self.settings['webSettings']['url']:
                    embed.add_field(name="目前存取本 Discord 伺服器之 token", value=f'{self.DB.getToken(interaction.guild_id)}' , inline=False)
                    embed.add_field(name='\u200b', value=f'token 每天 GMT 0:00 更新\n網址：{self.settings["webSettings"]["url"]}' , inline=False)
                else:
                    embed.add_field(name="未啟用此功能", value='\u200b' , inline=False)
            else:
                embed = discord.Embed(title="其他功能列表", description='\u200b' , color=0xc0c0c0)
                embed.set_author(name=self.bot.user.name , icon_url=self.bot.user.avatar.url)
                embed.add_field(name="指令", value=f"{self.pf}status\n{self.pf}majorArcana + (隨意內容)\n{self.pf}majorArcana3 + (隨意內容)" , inline=True)
                embed.add_field(name="功能", value="回傳 bot 狀態\n根據訊息內容使用大密儀塔羅牌占卜\n根據訊息內容使用三張大密儀塔羅牌占卜" , inline=True)
            await interaction.response.send_message(embed=embed , ephemeral=True)

    @commands.command()
    async def help(self , ctx):
        await ctx.send("指令列表", view=self.helpMessageMenu(self.bot , self.settings , self.pf , self.DB) , delete_after=60)

async def setup(bot):
    await bot.add_cog(help_message(bot))