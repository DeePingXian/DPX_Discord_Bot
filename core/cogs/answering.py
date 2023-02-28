from core.classes import Cog_Extension
from discord.ext import commands
import discord , os , shutil , requests , openpyxl

class answering(Cog_Extension):

    def __init__(self , bot):
        super().__init__(bot)
        self.AnsweringDict = {}
        self.loadAnsweringContent()

    #載入答錄機訊息

    def loadAnsweringContent(self):
        self.AnsweringDict.clear()
        AnsweringSheet = openpyxl.load_workbook('assets\\answeringMachine\\answeringContent.xlsx').worksheets[0]
        for i in range(2 , AnsweringSheet.max_row+1):
            value = []
            for j in range(1 , 6):
                value.append(AnsweringSheet.cell(row=i, column=j).value)
            self.AnsweringDict[AnsweringSheet.cell(row=i, column=1).value] = value

    @commands.command()
    async def sendansweringcontentlist(self , ctx):
        await ctx.send(file=discord.File('assets\\answeringMachine\\answeringContent.xlsx'))

    #修改答錄機訊息

    @commands.command()
    async def editansweringcontentlist(self , ctx):
        try:
            _ = ctx.message.attachments[0]
        except:
            await ctx.reply('請附上修改自「!!sendansweringcontentlist」指令提供的檔案')
        else:
            if ctx.message.attachments[0].url[0:26] == "https://cdn.discordapp.com" and ctx.message.attachments[0].url[ctx.message.attachments[0].url.rfind('/')+1:] == 'answeringContent.xlsx':
                try:
                    if not os.path.isdir('assets/answeringMachine/temp'):         #先下載再取代，比較安全
                        os.mkdir('assets/answeringMachine/temp')
                    r=requests.get(ctx.message.attachments[0].url , stream=True)
                    with open('assets\\answeringMachine\\temp\\answeringContent.xlsx', 'wb') as outFile:
                        shutil.copyfileobj(r.raw, outFile)
                    shutil.copyfile('assets\\answeringMachine\\temp\\answeringContent.xlsx' , 'assets\\answeringMachine\\answeringContent.xlsx')
                    if os.path.isfile('assets\\answeringMachine\\temp\\answeringContent.xlsx'):
                        os.remove('assets\\answeringMachine\\temp\\answeringContent.xlsx')
                except:
                    await ctx.reply('寫入檔案時發生錯誤')
                else:
                    self.loadAnsweringContent()
                    await ctx.send('應答機更新完成')
            else:
                await ctx.reply('請附上修改自「!!sendansweringcontentlist」指令提供的檔案')

    @commands.Cog.listener()
    async def on_message(self , message):

        #應答機

        if message.author != self.bot.user:
            for i in self.AnsweringDict:
                if ( message.content.lower() == i.lower() and ( self.AnsweringDict[i][3] == 'Y' or message.content == i ) ) or ( ( i in message.content or (i.lower() in message.content.lower() and self.AnsweringDict[i][3] == 'Y' ) ) and self.AnsweringDict[i][4] == 'Y' ):
                    if self.AnsweringDict[i][1] != None:
                        await message.channel.send(self.AnsweringDict[i][1])
                    if self.AnsweringDict[i][2] != None:
                        try:
                            await message.channel.send(file=discord.File(f'assets\\answeringMachine\\{self.AnsweringDict[i][2]}'))
                        except:
                            pass

async def setup(bot):
    await bot.add_cog(answering(bot))