from core.classes import Cog_Extension
from discord.ext import commands
import discord , os , shutil , requests , openpyxl

class answering(Cog_Extension):

    def __init__(self , bot):
        super().__init__(bot)
        self.allAnsweringDict = {}      #guild id: {應答內容}
        self.loadAllAnsweringMsg()

    #載入答錄機訊息

    def loadAllAnsweringMsg(self):
        self.allAnsweringDict.clear()
        files = os.listdir("assets/answeringMachine")
        allansweringBook = []
        for i in files:
            try:
                allansweringBook.append(int(i))        #挑選資料夾
            except:
                pass
        for i in allansweringBook:
            answeringSheet = openpyxl.load_workbook(f"assets/answeringMachine/{i}/answeringMsg.xlsx").worksheets[0]
            self.allAnsweringDict[int(i)] = []
            for j in range(2 , answeringSheet.max_row+1):
                value = []
                for k in range(1 , 6):
                    value.append(answeringSheet.cell(row=j, column=k).value)
                self.allAnsweringDict[int(i)].append(value)

    def loadAnsweringMsg(self , guildID):
        guildID = int(guildID)
        if os.path.isfile(f"assets/answeringMachine/{guildID}/answeringMsg.xlsx"):
            answeringSheet = openpyxl.load_workbook(f"assets/answeringMachine/{guildID}/answeringMsg.xlsx").worksheets[0]
            self.allAnsweringDict[guildID] = []
            for j in range(2 , answeringSheet.max_row+1):
                value = []
                for k in range(1 , 6):
                    value.append(answeringSheet.cell(row=j, column=k).value)
                self.allAnsweringDict[guildID].append(value)

    @commands.command()
    async def sendansweringmsglist(self , ctx):
        if not os.path.isfile(f"assets/answeringMachine/{ctx.guild.id}/answeringMsg.xlsx"):
            os.makedirs(f"assets/answeringMachine/{ctx.guild.id}")
            book = openpyxl.Workbook()
            sheet = book.active
            sheet.append(("訊息內容" , "傳送內容" , "檔案名稱" , "訊息內容是否忽略大小寫" , "訊息是否有包含就觸發 不用完全一樣"))
            book.save(f"assets/answeringMachine/{ctx.guild.id}/answeringMsg.xlsx")
        await ctx.send(file=discord.File(f"assets/answeringMachine/{ctx.guild.id}/answeringMsg.xlsx"))

    #修改答錄機訊息

    @commands.command()
    async def editansweringmsglist(self , ctx):
        try:
            _ = ctx.message.attachments[0]
        except:
            await ctx.reply(f"請附上修改自「{self.settings['commandPrefix']}sendansweringmsglist」指令提供的檔案")
        else:
            if ctx.message.attachments[0].url[0:26] == "https://cdn.discordapp.com" and ctx.message.attachments[0].url[ctx.message.attachments[0].url.rfind('/')+1:ctx.message.attachments[0].url.find('?')] == "answeringMsg.xlsx":
                try:
                    os.makedirs(f"assets/answeringMachine/{ctx.guild.id}/temp" , exist_ok=True)        #先下載再取代，比較安全
                    r=requests.get(ctx.message.attachments[0].url , stream=True)
                    with open(f"assets/answeringMachine/{ctx.guild.id}/temp/answeringMsg.xlsx", "wb") as outFile:
                        shutil.copyfileobj(r.raw, outFile)
                    shutil.copyfile(f"assets/answeringMachine/{ctx.guild.id}/temp/answeringMsg.xlsx" , f"assets/answeringMachine/{ctx.guild.id}/answeringMsg.xlsx")
                    shutil.rmtree(f"assets/answeringMachine/{ctx.guild.id}/temp" , ignore_errors=True)
                except:
                    await ctx.reply("寫入檔案時發生錯誤")
                else:
                    self.loadAnsweringMsg(ctx.guild.id)
                    await ctx.send("應答機更新完成")
            else:
                await ctx.reply(f"請附上修改自「{self.settings['commandPrefix']}sendansweringmsglist」指令提供的檔案")

    @commands.Cog.listener()
    async def on_message(self , message):
        if self.allAnsweringDict.get(message.guild.id , None) and message.author != self.bot.user:
            for i in self.allAnsweringDict[message.guild.id]:
                if ( message.content.lower() == i[0].lower() and ( i[3] == 'Y' or message.content == i[0] ) ) or ( ( i[0] in message.content or (i[0].lower() in message.content.lower() and i[3] == 'Y' ) ) and i[4] == 'Y' ):
                    if i[1] != None:
                        await message.channel.send(i[1])
                    if i[2] != None:
                        try:
                            await message.channel.send(file=discord.File(f"assets/answeringMachine/{message.guild.id}/{i[2]}"))
                        except:
                            pass

async def setup(bot):
    await bot.add_cog(answering(bot))