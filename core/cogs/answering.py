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
    
    @discord.app_commands.command(name="sendansweringmsglist" , description="傳送應答訊息列表檔案")
    async def sendansweringmsglist(self , interaction:discord.Interaction):
        await interaction.response.defer()
        if not os.path.isfile(f"assets/answeringMachine/{interaction.guild.id}/answeringMsg.xlsx"):
            os.makedirs(f"assets/answeringMachine/{interaction.guild.id}/temp" , exist_ok=True)
            book = openpyxl.Workbook()
            sheet = book.active
            sheet.append(("訊息內容" , "傳送內容" , "檔案名稱" , "訊息內容是否忽略大小寫" , "訊息是否有包含就觸發 不用完全一樣"))
            book.save(f"assets/answeringMachine/{interaction.guild.id}/temp/answeringMsg.xlsx")
            await interaction.followup.send(file=discord.File(f"assets/answeringMachine/{interaction.guild_id}/temp/answeringMsg.xlsx"))
            shutil.rmtree(f"assets/welcomeMsg/{interaction.guild.id}/temp" , ignore_errors=True)
        else:
            await interaction.followup.send(file=discord.File(f"assets/welcomeMsg/{interaction.guild.id}/welcomeMsg.xlsx"))

    #修改答錄機訊息

    @discord.app_commands.command(name="editansweringmsglist" , description="修改應答訊息列表（請附上應答訊息列表檔案）")
    @discord.app_commands.describe(file="應答訊息列表檔案")
    async def editansweringmsglist(self , interaction:discord.Interaction , file:discord.Attachment):
        await interaction.response.defer()
        if file.filename == "answeringMsg.xlsx":
            try:
                os.makedirs(f"assets/answeringMachine/{interaction.guild.id}/temp" , exist_ok=True)        #先下載再取代，比較安全
                #await file.save(f"assets/answeringMachine/{interaction.guild.id}/temp/answeringMsg.xlsx" , use_cached=True)    無法使用
                r=requests.get(file.url , stream=True)
                with open(f"assets/answeringMachine/{interaction.guild.id}/temp/answeringMsg.xlsx", "wb") as outFile:
                    shutil.copyfileobj(r.raw , outFile)
                shutil.copyfile(f"assets/answeringMachine/{interaction.guild.id}/temp/answeringMsg.xlsx" , f"assets/answeringMachine/{interaction.guild.id}/answeringMsg.xlsx")
                shutil.rmtree(f"assets/answeringMachine/{interaction.guild.id}/temp" , ignore_errors=True)
            except OSError:
                await interaction.followup.send("寫入檔案時發生錯誤")
            except:
                await interaction.followup.send(f"請附上修改自「/sendansweringmsglist」指令提供的檔案")
            else:
                self.loadAnsweringMsg(interaction.guild.id)
                await interaction.followup.send("應答機更新完成")
        else:
            await interaction.followup.send(f"請附上修改自「/sendansweringmsglist」指令提供的檔案")

    @commands.Cog.listener()
    async def on_message(self , message):

        #應答機
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