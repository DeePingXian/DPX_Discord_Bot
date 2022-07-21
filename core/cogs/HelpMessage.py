import discord
from discord.ext import commands
from core.classes import Cog_Extension
import json

with open('settings.json' , 'r' , encoding = 'utf8') as json_file:
    json_data = json.load(json_file)

pf = json_data['command_prefix']

class HelpMessage(Cog_Extension):

    @commands.command()
    async def help(self , ctx , *page):
        embed = discord.Embed(title="指令列表", description='請選擇查詢類別' , color=0xc0c0c0)
        embed.set_author(name="Discord bot" , url=discord.Embed.Empty , icon_url=json_data['BotIconUrl'])
        if len(page) !=1:
            page = 0
        try:
            page = int(page[0])
        except:
            page = 0
        finally:
            if page == 1:
                await ctx.send(f'{pf}reload→重新載入應答機內容\n內容：')
                await ctx.send(file=discord.File('assets\\AnsweringMachine\\AnsweringContent.xlsx'))
            elif page == 2:
                embed = discord.Embed(title="產生連結功能列表", description='\u200b' , color=0xc0c0c0)
                embed.set_author(name="Discord bot" , url=discord.Embed.Empty , icon_url=json_data['BotIconUrl'])
                embed.add_field(name="指令", value=f'{pf}nh rand\n{pf}nh + (車號)\n{pf}pix + (作品號)\n{pf}pixu + (作者號)\n{pf}twiu + (用戶ID)' , inline=True)
                embed.add_field(name="功能", value='隨機產生本子\n查該本子\n查該pixiv作品\n查該pixiv作者\n查該twitter用戶' , inline=True)
                await ctx.send(embed=embed)
            elif page == 3:
                embed = discord.Embed(title="播音樂功能列表", description='\u200b' , color=0xc0c0c0)
                embed.set_author(name="Discord bot" , url=discord.Embed.Empty , icon_url=json_data['BotIconUrl'])
                embed.add_field(name="指令", value=f'{pf}play + (網址)\n{pf}add + (網址)\n{pf}pause\n{pf}resume\n{pf}skip\n{pf}loop\n{pf}stop\n{pf}join\n{pf}queue\n{pf}nowplaying' , inline=True)
                embed.add_field(name="功能", value='播放該音樂\n增加該音樂至播放隊列\n暫停播放\n恢復播放\n跳過目前曲目\n單曲重複播放\n停止播放 並清除音樂資料\n加入用戶所在語音頻道\n查看播放隊列\n查看現正播放' , inline=True)
                embed.add_field(name='\u200b', value='\u200b' , inline=False)
                embed.add_field(name='支援類型', value='網站\nGoogle雲端音訊檔案容器\nGoogle雲端單檔大小上限' , inline=True)
                embed.add_field(name='\u200b', value=f'YouTube Google雲端\naac flac m4a mp3 ogg wav weba\n{json_data["googleDriveFileSizeLimitInMB"]}MB' , inline=True)
                embed.add_field(name='\u200b', value=f'如果運行發生問題，請使用{pf}stop清除資料，並再重新操作一次' , inline=False)
                await ctx.send(embed=embed)
            elif page == 4:
                embed = discord.Embed(title="其他功能列表", description='\u200b' , color=0xc0c0c0)
                embed.set_author(name="Discord bot" , url=discord.Embed.Empty , icon_url=json_data['BotIconUrl'])
                embed.add_field(name="指令", value=f'{pf}status\n{pf}history + (數字)\n{pf}history all\n{pf}historyf + (數字)\n{pf}MajorArcana + (隨意內容)\n{pf}MajorArcana3 + (隨意內容)' , inline=True)
                embed.add_field(name="功能", value='回傳 bot 狀態\n回傳前第n個被刪除/編輯的文字訊息 (上限99則)\n回傳所有被刪除/編輯的文字訊息 (上限99則)\n回傳前第n個被刪除的檔案訊息\n產生一張大密儀塔羅牌\n產生三張大密儀塔羅牌' , inline=True)
                await ctx.send(embed=embed)
            else:
                embed.add_field(name="指令", value=f'{pf}help 1\n{pf}help 2\n{pf}help 3\n{pf}help 4' , inline=True)
                embed.add_field(name="功能類別", value='應答機功能\n產生連結功能\n播音樂功能\n其他功能' , inline=True)
                await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(HelpMessage(bot))