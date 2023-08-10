import discord
from discord.ext import commands
from core.classes import Cog_Extension

class help_message(Cog_Extension):

    def __init__(self , bot):
        super().__init__(bot)
        self.pf = self.settings['command_prefix']

    class helpMessageMenu(discord.ui.View):
        
        def __init__(self , bot , settings , pf , DB):
            super().__init__(timeout=60)
            self.bot = bot
            self.settings = settings
            self.pf = pf
            self.DB = DB

        @discord.ui.select(
            placeholder = "請選擇查詢類別",
            min_values = 1,
            max_values = 1,
            options = [
                discord.SelectOption(
                    label="應答機功能列表"
                ),
                discord.SelectOption(
                    label="產生連結功能列表"
                ),
                discord.SelectOption(
                    label="播音樂功能列表"
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
            if select.values[0] == '應答機功能列表':
                embed = discord.Embed(title="應答機功能列表", description='\u200b' , color=0xc0c0c0)
                embed.set_author(name=self.bot.user.name , icon_url=self.settings['BotIconUrl'])
                embed.add_field(name="指令", value=f'{self.pf}sendansweringcontentlist\n{self.pf}editansweringcontentlist' , inline=True)
                embed.add_field(name="功能", value='傳送應答列表\n修改應答列表（請附上應答列表檔案）' , inline=True)
                embed.add_field(name='\u200b', value='若訊息符合設定條件，bot會回傳設定的訊息內容\n修改訊息附件檔案須請開bot的管理員操作' , inline=False)
            elif select.values[0] == '產生連結功能列表':
                embed = discord.Embed(title="產生連結功能列表", description='\u200b' , color=0xc0c0c0)
                embed.set_author(name=self.bot.user.name , icon_url=self.settings['BotIconUrl'])
                embed.add_field(name="指令", value=f'{self.pf}nh rand\n{self.pf}nh + (車號)\n{self.pf}pix + (作品號)\n{self.pf}pixu + (作者號)\n{self.pf}twiu + (用戶ID)' , inline=True)
                embed.add_field(name="功能", value='隨機傳送本子連結\n傳送該本子連結\n傳送該pixiv作品連結\n傳送該pixiv作者連結\n傳送該twitter用戶連結' , inline=True)
            elif select.values[0] == '播音樂功能列表':
                embed = discord.Embed(title="播音樂功能列表", description='\u200b' , color=0xc0c0c0)
                embed.set_author(name=self.bot.user.name , icon_url=self.settings['BotIconUrl'])
                embed.add_field(name="指令", value=f'{self.pf}play + (網址)\n{self.pf}playlocal + (音樂檔案路徑)\n{self.pf}add + (網址)\n{self.pf}addlocal + (音樂檔案路徑)\n{self.pf}pause\n{self.pf}resume\n{self.pf}skip\n{self.pf}loop\n{self.pf}stop\n{self.pf}join\n{self.pf}queue\n{self.pf}nowplaying' , inline=True)
                embed.add_field(name="功能", value='播放該音樂\n播放該本機音樂（僅限開bot的管理員使用）\n增加該音樂至播放隊列\n增加該本機音樂至播放隊列（僅限開bot的管理員使用）\n暫停播放\n恢復播放\n跳過目前曲目\n單曲重複播放\n停止播放 並清除音樂資料\n加入用戶所在語音頻道\n查看播放隊列\n查看現正播放' , inline=True)
                embed.add_field(name='\u200b', value='\u200b' , inline=False)
                embed.add_field(name='支援類型', value='來源\n\n\n播放隊列上限\nGoogle雲端音訊檔案容器\nGoogle雲端單檔大小上限' , inline=True)
                acceptableMusicContainer = ''
                for i in self.settings['musicBotOpts']['googleDrive']['acceptableMusicContainer']:
                    acceptableMusicContainer += i
                    if i != self.settings['musicBotOpts']['googleDrive']['acceptableMusicContainer'][-1]:
                        acceptableMusicContainer += ' '
                embed.add_field(name='\u200b', value=f'YouTube影片、直播、播放清單、合輯\nGoogle雲端檔案\nbilibili影片、影片列表(beta)\n{self.settings["musicBotOpts"]["maxQueueLen"]}\n{acceptableMusicContainer}\n{self.settings["musicBotOpts"]["googleDrive"]["fileSizeLimitInMB"]}MB' , inline=True)
                embed.add_field(name='\u200b', value=f'播放B站影片時受限於機制，bot反應會較慢\n如果播音樂發生問題，請使用{self.pf}stop清除資料，並再重新操作一次，實在不行請重啟bot' , inline=False)
            elif select.values[0] == '本 bot 附屬網頁相關':
                embed = discord.Embed(title="本 bot 附屬網頁相關", description='\u200b' , color=0xc0c0c0)
                embed.set_author(name=self.bot.user.name , icon_url=self.settings['BotIconUrl'])
                if self.settings['webSettings']['url']:
                    embed.add_field(name="目前存取網頁之 token", value=f'{self.DB.GetToken()}' , inline=False)
                    embed.add_field(name="本伺服器ID", value=interaction.guild_id , inline=False)
                    embed.add_field(name='\u200b', value=f'token 每天 UTC 0:00／CST 8:00 更新\n網址：{self.settings["webSettings"]["url"]}' , inline=False)
                else:
                    embed.add_field(name="未啟用此功能", value='\u200b' , inline=False)
            else:
                embed = discord.Embed(title="其他功能列表", description='\u200b' , color=0xc0c0c0)
                embed.set_author(name=self.bot.user.name , icon_url=self.settings['BotIconUrl'])
                embed.add_field(name="指令", value=f'{self.pf}status\n{self.pf}history + (數字)\n{self.pf}history all\n{self.pf}historyf + (數字)\n{self.pf}majorArcana + (隨意內容)\n{self.pf}majorArcana3 + (隨意內容)' , inline=True)
                embed.add_field(name="功能", value='回傳 bot 狀態\n回傳前第n個被刪除/編輯的文字訊息 (上限99則)\n回傳所有被刪除/編輯的文字訊息 (上限99則)\n回傳前第n個被刪除的檔案訊息\n產生一張大密儀塔羅牌\n產生三張大密儀塔羅牌' , inline=True)
            await interaction.channel.send(embed=embed)
            await interaction.response.defer()

    @commands.command()
    async def help(self , ctx):
        await ctx.send("指令列表", view=self.helpMessageMenu(self.bot , self.settings , self.pf , self.DB) , delete_after=60)

async def setup(bot):
    await bot.add_cog(help_message(bot))