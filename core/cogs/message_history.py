import discord
from discord.ext import commands
from core.classes import Cog_Extension
import os , shutil , time , datetime , requests , openpyxl

class message_history(Cog_Extension):

    def __init__(self , bot):
        super().__init__(bot)
        if os.path.isdir("assets/messageHistory/temp"):     #清除暫存訊息歷史紀錄
            shutil.rmtree("assets/messageHistory/temp")

    #訊息log

    @commands.Cog.listener()
    async def on_message(self , message):        
        try:
            if message.content != '' or message.attachments != []:
                self.DB.putMessageLog(message , None , None , 0)
        except:
            if message.author != self.bot.user:
                raise ConnectionError('MySQL connection failed, can\'t create message log.')

    #儲存被刪除的訊息

    @commands.Cog.listener()
    async def on_message_delete(self , message):
        try:
            message.attachments[0].url      #檢查是否有附件
        except:         #沒有附件
            if message.content != "":
                self.DB.putMessageLog(message , None , time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) , 2)
        else:       #有附件
            self.DB.putMessageLog(message , None , time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) , 2)
            os.makedirs(f"assets/messageHistory/{message.guild.id}/{message.channel.id}/files" , exist_ok=True)
            r=requests.get(message.attachments[0].url, stream=True)     #存附件
            slashpos = message.attachments[0].url.rfind('/')
            imageName=str(f"assets/messageHistory/{message.guild.id}/{message.channel.id}/files/{message.author}➼{message.author.id}➼{(message.attachments[0].url)[slashpos+1:]}")
            with open(imageName, 'wb') as out_file:
                shutil.copyfileobj(r.raw, out_file)

    #儲存被編輯的訊息

    @commands.Cog.listener()
    async def on_message_edit(self , message_before , message_after):
        if message_before.content != message_after.content:     #單純傳連結也會被視為編輯訊息 所以要先檢查訊息是否一樣
            self.DB.putMessageLog(message_after , message_before , time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) , 1)       #只有文字能被編輯 所以只存文字 同時編輯後的文字不會為空

    #回傳訊息歷史紀錄

    class GetMessageHistory(discord.ui.View):

        def __init__(self , ctx , settings , DB):
            super().__init__(timeout=60)
            self.settings = settings
            self.messages = DB.getMessageLog(ctx.guild.id , ctx.channel.id , (1 , 2))
            self.messages = list(self.messages)
            self.messages.reverse()
            for i in range(0 , min(len(self.messages) , 25)):
                if self.messages[i][2] == "":
                    label = "(附件檔案)"
                elif len(self.messages[i][2]) > 50:
                    label = self.messages[i][2][0:46] + "..."
                else:
                    label = self.messages[i][2]
                self.children[0].options.append(discord.SelectOption(label=label , description=self.messages[i][0] , value=i))

        @discord.ui.select(placeholder="請選擇已編輯/刪除的訊息" , min_values=1 , max_values=1)

        async def select_callback(self , interaction , select):
            msg = self.messages[int(select.values[0])]
            if msg[7] == 1:
                embed = discord.Embed(title=f"前第{int(select.values[0])+1}個被刪除/編輯的文字訊息" , description=f"作者：<@{msg[1]}>\n\n原訊息：\n「{msg[2]}」\n編輯後之訊息：\n「{msg[3]}」" , color=0xff0000)
                embed.add_field(name="傳送訊息時間 (CST)" , value=str(msg[5] + datetime.timedelta(hours=8)) , inline=True)
                embed.add_field(name="編輯訊息時間 (CST)" , value=str(msg[6] + datetime.timedelta(hours=8)) , inline=True)
            elif msg[7] == 2:
                if msg[2] == "":
                    msgDescription = "(附件檔案)"
                else:
                    msgDescription = '「' + msg[2] + '」'
                embed = discord.Embed(title=f"前第{int(select.values[0])+1}個被刪除/編輯的文字訊息" , description=f"作者：<@{msg[1]}>\n\n刪除之訊息：\n{msgDescription}" , color=0xff0000)
                embed.add_field(name="傳送訊息時間 (CST)", value=str(msg[5] + datetime.timedelta(hours=8)) , inline=True)
                embed.add_field(name="刪除訊息時間 (CST)", value=str(msg[6] + datetime.timedelta(hours=8)) , inline=True)
            await interaction.response.send_message(embed=embed)

    @commands.command()
    async def history(self , ctx):
        await ctx.send("最近25則修改的訊息歷史紀錄查詢列表" , view=self.GetMessageHistory(ctx , self.settings , self.DB))
    
    @commands.command()
    async def historyall(self , ctx , *msgType):
        msgTypeValid = True if msgType != () else False
        for i in msgType:
            if i not in ('0' , '1' , '2'):
                msgTypeValid = False
                break
        if msgTypeValid:
            messages = self.DB.getMessageLog(ctx.guild.id , ctx.channel.id , msgType)
            messages = list(messages)
            messages.reverse()
            os.makedirs(f"assets/messageHistory/temp" , exist_ok=True)
            book = openpyxl.Workbook()
            sheet = book.active
            sheet.append(("作者" , "作者ID" , "原始訊息內容" , "修改後訊息內容" , "附件檔案" , "傳送時間 (CST)" , "刪除/編輯時間 (CST)" , "類型"))
            for i in range(2 , len(messages)+2):
                sheet.cell(row=i , column=1 , value=str(messages[i-2][0]))
                sheet.cell(row=i , column=2 , value=str(messages[i-2][1]))
                sheet.cell(row=i , column=3 , value=str(messages[i-2][2]))
                sheet.cell(row=i , column=4 , value=str(messages[i-2][3]))
                sheet.cell(row=i , column=5 , value=str(messages[i-2][4]))
                sheet.cell(row=i , column=6 , value=str(messages[i-2][5] + datetime.timedelta(hours=8)))
                sheet.cell(row=i , column=7 , value=str(messages[i-2][6] + datetime.timedelta(hours=8)) if str(messages[i-2][6]) != "0000-00-00 00:00:00" else "")
                if messages[i-2][7] == 0:
                    sheet.cell(row=i , column=8 , value="原訊息")
                elif messages[i-2][7] == 1:
                    sheet.cell(row=i , column=8 , value="編輯")
                elif messages[i-2][7] == 2:
                    sheet.cell(row=i , column=8 , value="刪除")
            book.save(f"assets/messageHistory/temp/{ctx.channel}_{ctx.channel.id}_message_history.xlsx")
            text = ""
            for i in msgType:
                if i == '0':
                    text += "未修改"
                elif i == '1':
                    text += "編輯"
                elif i == '2':
                    text += "刪除"
                if i != msgType[-1]:
                    text += "、"
            await ctx.send(f"本頻道之{text}訊息列表" , file=discord.File(f"assets/messageHistory/temp/{ctx.channel}_{ctx.channel.id}_message_history.xlsx"))
            shutil.rmtree("assets/messageHistory/temp")
        else:
            await ctx.reply("查詢代號僅能為 0未編輯、刪除的訊息 1編輯的訊息 2刪除的訊息")

    @commands.command()
    async def historyf(self , ctx , *num):
        try:
            num = num[0]
        except:
            num = 1
        path = f"assets/messageHistory/{ctx.guild.id}/{ctx.channel.id}/files"
        if os.path.isdir(path):
            file_list = os.listdir(path)
            if file_list != []:
                file_list.sort(key=lambda x: os.path.getmtime(f"{path}/{x}") , reverse = True)
                await ctx.send(f"前第{num}個被刪除的檔案訊息")
                await ctx.send(file=discord.File(f"{path}/{file_list[int(num)-1]}"))
                file_path = f"{path}/{file_list[int(num)-1]}"
                author = f"<@{file_list[int(num)-1].split('➼')[1]}>"
                await ctx.send(f'傳送者：{author}\n刪除訊息時間 (CST)：{time.strftime("%Y-%m-%d %H:%M:%S" , time.gmtime(os.path.getmtime(file_path)+28800))}')
            else:
                await ctx.send('無已刪除檔案訊息')
        else:
            await ctx.send('無已刪除檔案訊息')

    @commands.command()
    async def historyflist(self , ctx):
        path = f"assets/messageHistory/{ctx.guild.id}/{ctx.channel.id}/files"
        if os.path.isdir(path):
            file_list = os.listdir(path)
            if file_list != []:
                file_list.sort(key=lambda x: os.path.getmtime(f"{path}/{x}") , reverse=True)
                description = ""
                for i in range(0 , len(file_list)):
                    info = file_list[i].split('➼')
                    description += f"{'%03d' % i}. {info[0]}：{info[2]}\n"
                embed = discord.Embed(title=f"已刪除的附件檔案列表" , description=description , color=0xff0000)
                await ctx.send(embed=embed)
            else:
                await ctx.send('無已刪除檔案訊息')
        else:
            await ctx.send('無已刪除檔案訊息')

async def setup(bot):
    await bot.add_cog(message_history(bot))