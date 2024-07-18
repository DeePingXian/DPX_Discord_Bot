import discord
from core.classes import Cog_Extension

class help_message(Cog_Extension):

    class helpMessageMenu(discord.ui.View):
        
        def __init__(self , bot , settings , DB):
            super().__init__(timeout=60)
            self.bot = bot
            self.settings = settings
            self.DB = DB

        @discord.ui.select(
            placeholder = "請選擇查詢類別" , min_values = 1 , max_values = 1 ,
            options = [
                discord.SelectOption(
                    label="AI聊天功能列表"
                ),
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
                    label="新人加入歡迎訊息功能列表"
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

        async def select_callback(self , interaction:discord.Interaction , select):
            if select.values[0] == "AI聊天功能列表":
                embed = discord.Embed(title="AI聊天功能列表", description='\u200b' , color=0xc0c0c0)
                embed.set_author(name=self.bot.user.name , icon_url=self.bot.user.avatar.url)
                embed.add_field(name="指令", value=f"直接tag此bot + (訊息內容)\n/resetchat\n/getchattokenemaillink\n/getchattoken" , inline=True)
                embed.add_field(name="功能", value="與本bot聊天\n重設聊天狀態\n取得Character.AI的連線token (步驟1/2)\n取得Character.AI的連線token (步驟2/2)" , inline=True)
            elif select.values[0] == "播音樂功能列表":
                embed = discord.Embed(title="播音樂功能列表", description='\u200b' , color=0xc0c0c0)
                embed.set_author(name=self.bot.user.name , icon_url=self.bot.user.avatar.url)
                embed.add_field(name="指令", value=f"/play + (網址)\n\n/playlocal + (音樂檔案路徑)\n\n/add + (網址)\n\n/addlocal + (音樂檔案路徑)\n\n/pause\n/resume\n/skip\n/loop\n/stop\n/queue\n/nowplaying\n/download\n/join" , inline=True)
                embed.add_field(name="功能", value="播放該音樂\n若為播放清單將從該項的位置依序加入\n播放該本機音樂\n(僅限開bot的管理員使用)\n增加該音樂至播放隊列\n若為播放清單將從該項的位置依序加入\n增加該本機音樂至播放隊列\n(僅限開bot的管理員使用)\n暫停播放音樂\n恢復播放音樂\n跳過目前曲目\n切換單曲重複播放\n停止播放音樂 並清除音樂資料\n查看音樂播放隊列\n查看現正播放的音樂\n下載現正播放的音樂\n加入用戶所在語音頻道" , inline=True)
                embed.add_field(name='\u200b', value='\u200b' , inline=False)
                embed.add_field(name="支援類型", value="來源\n\n\n\n播放隊列上限\nGoogle雲端單檔大小上限\nGoogle雲端音訊檔案容器" , inline=True)
                acceptableMusicContainer = ''
                for i in self.settings["musicBotOpts"]["googleDrive"]["acceptableMusicContainer"]:
                    acceptableMusicContainer += i
                    if i != self.settings["musicBotOpts"]["googleDrive"]["acceptableMusicContainer"][-1]:
                        acceptableMusicContainer += ' '
                embed.add_field(name='\u200b', value=f"YouTube影片、直播、播放清單、合輯\nGoogle雲端檔案\nbilibili影片、影片列表\n電腦本地檔案\n{self.settings['musicBotOpts']['maxQueueLen']}\n{self.settings['musicBotOpts']['googleDrive']['fileSizeLimitInMB']}MB\n{acceptableMusicContainer}" , inline=True)
                embed.add_field(name='\u200b', value=f"如果播音樂發生問題，請使用/stop清除資料，並再重新操作一次，實在不行請重啟bot" , inline=False)
            elif select.values[0] == "訊息歷史紀錄功能列表":
                embed = discord.Embed(title="訊息歷史紀錄功能列表", description='\u200b' , color=0xc0c0c0)
                embed.set_author(name=self.bot.user.name , icon_url=self.bot.user.avatar.url)
                embed.add_field(name="指令", value=f"/history\n/historyf + (數字)\n/historyflist\n/historyall + (選項 選項 選項)" , inline=True)
                embed.add_field(name="功能", value="查詢最近25則修改的文字訊息\n回傳前第n個被刪除的檔案訊息\n回傳已刪除的附件檔案列表\n匯出欲查詢的的文字訊息類型總集之Excel檔，只選擇欲查詢的項目即可" , inline=True)
            elif select.values[0] == "應答機功能列表":
                embed = discord.Embed(title="應答機功能列表", description='\u200b' , color=0xc0c0c0)
                embed.set_author(name=self.bot.user.name , icon_url=self.bot.user.avatar.url)
                embed.add_field(name="指令", value=f"/sendansweringmsglist\n/editansweringmsglist" , inline=True)
                embed.add_field(name="功能", value="傳送應答訊息列表檔案\n修改應答訊息列表(請附上應答訊息列表檔案)" , inline=True)
                embed.add_field(name='\u200b', value="若訊息符合設定條件，bot會回傳設定的訊息內容，若要關閉此功能請將應答訊息列表清空\n修改訊息附件檔案須請開bot的管理員操作" , inline=False)
            elif select.values[0] == "新人加入歡迎訊息功能列表":
                embed = discord.Embed(title="新人加入歡迎訊息功能列表", description='\u200b' , color=0xc0c0c0)
                embed.set_author(name=self.bot.user.name , icon_url=self.bot.user.avatar.url)
                embed.add_field(name="指令", value=f"/sendwelcomemsglist\n/editwelcomemsglist" , inline=True)
                embed.add_field(name="功能", value="傳送新人加入歡迎訊息列表檔案\n修改新人加入歡迎訊息(請附上歡迎訊息列表檔案)" , inline=True)
            elif select.values[0] == "產生連結功能列表":
                embed = discord.Embed(title="產生連結功能列表", description='\u200b' , color=0xc0c0c0)
                embed.set_author(name=self.bot.user.name , icon_url=self.bot.user.avatar.url)
                embed.add_field(name="指令", value=f"/nh + (車號)\n/nhrand\n/jm + (車號)\n/wn + (車號)\n/pix + (作品號)\n/pixu + (作者號)\n/twiu + (用戶ID)" , inline=True)
                embed.add_field(name="功能", value="傳送該nh本子連結\n隨機傳送nh本子連結\n傳送該JM本子連結\n傳送該wnacg本子連結\n傳送該pixiv作品連結\n傳送該pixiv作者連結\n傳送該X(twitter)用戶連結" , inline=True)
            elif select.values[0] == "本 bot 附屬網頁相關":
                embed = discord.Embed(title="本 bot 附屬網頁相關", description='\u200b' , color=0xc0c0c0)
                embed.set_author(name=self.bot.user.name , icon_url=self.bot.user.avatar.url)
                if self.settings["webSettings"]["url"]:
                    embed.add_field(name="目前存取本 Discord 伺服器之 token", value=f"{self.DB.getToken(interaction.guild_id)}" , inline=False)
                    embed.add_field(name='\u200b', value=f"token 每天 GMT 0:00 更新\n網址：{self.settings['webSettings']['url']}" , inline=False)
                else:
                    embed.add_field(name="未啟用此功能", value='\u200b' , inline=False)
            else:
                embed = discord.Embed(title="其他功能列表", description='\u200b' , color=0xc0c0c0)
                embed.set_author(name=self.bot.user.name , icon_url=self.bot.user.avatar.url)
                embed.add_field(name="指令", value=f"/help\n/status\n/majorarcana + (訊息)\n/majorarcana3 + (訊息)" , inline=True)
                embed.add_field(name="功能", value="查詢指令\n回傳bot狀態\n根據訊息內容使用大密儀塔羅牌占卜\n根據訊息內容使用三張大密儀塔羅牌占卜" , inline=True)
            await interaction.response.send_message(embed=embed , ephemeral=True)

    @discord.app_commands.command(name="help" , description="指令列表")
    async def help(self , interaction:discord.Interaction):
        await interaction.response.send_message("指令列表", view=self.helpMessageMenu(self.bot , self.settings , self.DB) , delete_after=60)

async def setup(bot):
    await bot.add_cog(help_message(bot))