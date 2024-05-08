from discord.ext import commands
from core.classes import Cog_Extension
import discord , os , shutil , openpyxl , random , requests

#用戶進出伺服器訊息

class welcome(Cog_Extension):

    class WelcomeMsgList():

        def __init__(self):
            self.msgChannel = None
            self.msgColor = []
            self.title = []
            self.msg = []
            self.thumbnail = []
            self.image = []

    def __init__(self , bot):
        super().__init__(bot)

    def loadWelcomeMsgList(self , guildID):
        if os.path.isfile(f"assets/welcomeMsg/{guildID}/welcomeMsg.xlsx"):
            welcomeMsgSheet = openpyxl.load_workbook(f"assets/welcomeMsg/{guildID}/welcomeMsg.xlsx").worksheets[0]
            welcomeMsgList = self.WelcomeMsgList()
            try:
                if welcomeMsgSheet.cell(row=2 , column=1).value:
                    welcomeMsgList.msgChannel = int(welcomeMsgSheet.cell(row=2 , column=1).value)
                else:
                    raise
            except:
                return None
            for i in range(2 , 7):
                totalRow = 0
                for j in range(2 , welcomeMsgSheet.max_row+1):
                    value = welcomeMsgSheet.cell(row=j , column=i).value
                    if value:
                        totalRow += 1
                    else:
                        break
                if totalRow != 0:       #沒有設定的項目
                    if i == 2:
                        for k in range(2 , totalRow+2):
                            try:
                                color = int(welcomeMsgSheet.cell(row=k , column=2).value , 16)
                                welcomeMsgList.msgColor.append(color)
                            except:
                                pass
                    elif i == 3:
                        for k in range(2 , totalRow+2):
                            welcomeMsgList.title.append(welcomeMsgSheet.cell(row=k , column=3).value)
                    elif i == 4:
                        for k in range(2 , totalRow+2):
                            welcomeMsgList.msg.append(welcomeMsgSheet.cell(row=k , column=4).value)
                    elif i == 5:
                        for k in range(2 , totalRow+2):
                            welcomeMsgList.image.append(welcomeMsgSheet.cell(row=k , column=5).value)
                    elif i == 6:
                        for k in range(2 , totalRow+2):
                            welcomeMsgList.thumbnail.append(welcomeMsgSheet.cell(row=k , column=6).value)
                else:
                    return None
            return welcomeMsgList
        else:
            return None

    @commands.Cog.listener()
    async def on_member_join(self , member):
        welcomeMsgList = self.loadWelcomeMsgList(member.guild.id)
        if welcomeMsgList:
            welcomeMsg = []
            if not welcomeMsgList.msgColor:
                welcomeMsg.append(0xffffff)
            else:
                welcomeMsg.append(welcomeMsgList.msgColor[random.randrange(len(welcomeMsgList.msgColor))])
            welcomeMsg.append(welcomeMsgList.title[random.randrange(len(welcomeMsgList.title))])
            welcomeMsg.append(welcomeMsgList.msg[random.randrange(len(welcomeMsgList.msg))])
            welcomeMsg.append(welcomeMsgList.image[random.randrange(len(welcomeMsgList.image))])
            welcomeMsg.append(welcomeMsgList.thumbnail[random.randrange(len(welcomeMsgList.thumbnail))])
            embed = discord.Embed(title=welcomeMsg[1] , description=welcomeMsg[2].replace("<user>" , f"<@{member.id}>") , color=welcomeMsg[0])
            embed.set_author(name=self.bot.user.name , icon_url=self.bot.user.avatar.url)
            embed.set_image(url=welcomeMsg[3])
            embed.set_thumbnail(url=welcomeMsg[4])
            channel = self.bot.get_channel(welcomeMsgList.msgChannel)
            await channel.send(embed=embed)

    @commands.command()
    async def sendwelcomemsglist(self , ctx):
        if not os.path.isfile(f"assets/welcomeMsg/{ctx.guild.id}/welcomeMsg.xlsx"):
            os.makedirs(f"assets/welcomeMsg/{ctx.guild.id}")
            book = openpyxl.Workbook()
            sheet = book.active
            sheet.append(("訊息傳送頻道ID" , "訊息邊條顏色" , "標題" , "內容" , "主圖網址" , "縮圖網址"))
            sheet.cell(row=2 , column=2 , value="FFFFFF")
            book.save(f"assets/welcomeMsg/{ctx.guild.id}/welcomeMsg.xlsx")
        await ctx.send(file=discord.File(f"assets/welcomeMsg/{ctx.guild.id}/welcomeMsg.xlsx"))

    @commands.command()
    async def editwelcomemsglist(self , ctx):
        try:
            _ = ctx.message.attachments[0]
        except:
            await ctx.reply(f"請附上修改自「{self.settings['commandPrefix']}sendwelcomemsglist」指令提供的檔案")
        else:
            if ctx.message.attachments[0].url[0:26] == "https://cdn.discordapp.com" and ctx.message.attachments[0].url[ctx.message.attachments[0].url.rfind('/')+1:ctx.message.attachments[0].url.find('?')] == "welcomeMsg.xlsx":
                try:
                    os.makedirs(f"assets/welcomeMsg/{ctx.guild.id}/temp" , exist_ok=True)       #先下載再取代，比較安全
                    r=requests.get(ctx.message.attachments[0].url , stream=True)
                    with open(f"assets/welcomeMsg/{ctx.guild.id}/temp/welcomeMsg.xlsx", "wb") as outFile:
                        shutil.copyfileobj(r.raw, outFile)
                    shutil.copyfile(f"assets/welcomeMsg/{ctx.guild.id}/temp/welcomeMsg.xlsx" , f"assets/welcomeMsg/{ctx.guild.id}/welcomeMsg.xlsx")
                    shutil.rmtree(f"assets/welcomeMsg/{ctx.guild.id}/temp" , ignore_errors=True)
                except:
                    await ctx.reply("寫入檔案時發生錯誤")
                else:
                    await ctx.send("歡迎訊息更新完成")
            else:
                await ctx.reply(f"請附上修改自「{self.settings['commandPrefix']}sendwelcomemsglist」指令提供的檔案")

async def setup(bot):
    await bot.add_cog(welcome(bot))