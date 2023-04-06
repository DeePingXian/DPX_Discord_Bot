import discord
from discord.ext import commands
from core.classes import Cog_Extension
import os , shutil , time , datetime , requests , openpyxl

class message_history(Cog_Extension):

    #儲存被刪除的訊息

    @commands.Cog.listener()
    async def on_message_delete(self , message):
        DeletedTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        try:
            url=message.attachments[0].url      #檢查是否有附件
        except:         #沒有附件 以txt儲存訊息
            if message.content != '':
                DB = self.bot.get_cog('MySQL')
                DB.PutMessageLog(message , None , time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) , 2)
                self.SaveDeletedMessage(message , DeletedTime)
        else:       #有附件 
            DB = self.bot.get_cog('MySQL')
            DB.PutMessageLog(message , None , time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) , 2)
            self.SaveDeletedMessage(message , DeletedTime)
            if not os.path.isdir(f'messageHistory\\{message.guild}\\{message.channel}\\files'):
                os.makedirs(f'messageHistory\\{message.guild}\\{message.channel}\\files')
            r=requests.get(message.attachments[0].url, stream=True)     #存附件
            slashpos = message.attachments[0].url.rfind('/')
            imageName=str(f'messageHistory\\{message.guild}\\{message.channel}\\files\\{message.author}➼{(message.attachments[0].url)[slashpos+1:]}')
            with open(imageName, 'wb') as out_file:
                shutil.copyfileobj(r.raw, out_file)

    #儲存被編輯的訊息

    @commands.Cog.listener()
    async def on_message_edit(self , message_before , message_after):
        if message_before.content != message_after.content:     #單純傳連結也會被視為編輯訊息 所以要先檢查訊息是否一樣
            EdittedTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            self.SaveEdittedMessage(message_before , message_after , EdittedTime)   #只有文字能被編輯 所以只存文字 同時編輯後的文字不會為空
            DB = self.bot.get_cog('MySQL')
            DB.PutMessageLog(message_after , message_before , time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) , 1)

    #回傳訊息歷史紀錄

    @commands.command()
    async def history(self , ctx , *num):
        try:
            num = num[0]
        except:
            num = 1
        if num == 'all':
            try:
                await ctx.send(file=discord.File(f'messageHistory\\{ctx.guild}\\{ctx.channel}\\{ctx.channel}_messageHistory.xlsx'))
            except:
                await ctx.send('無已刪除/編輯的文字訊息')
        elif int(num) >= 1 and int(num) <= 99:
            try:
                AnsweringSheet = openpyxl.load_workbook(f'messageHistory\\{ctx.guild}\\{ctx.channel}\\{ctx.channel}_messageHistory.xlsx').worksheets[0]
            except:
                await ctx.send('無已刪除/編輯的文字訊息')
            else:
                for i in range(2 , AnsweringSheet.max_row):
                    if time.strptime(AnsweringSheet.cell(row=i , column=5).value , "%Y-%m-%d %H:%M:%S") > time.strptime(AnsweringSheet.cell(row=i+1 , column=5).value , "%Y-%m-%d %H:%M:%S"):
                        startfrom = i
                        break
                    if i == AnsweringSheet.max_row-1:
                        startfrom = AnsweringSheet.max_row
                num = int(num)
                target = startfrom - (num - 1)
                if target < 2:
                    target += AnsweringSheet.max_row - 1
                if AnsweringSheet.cell(row=target , column=1).value != None:
                    if AnsweringSheet.cell(row=target , column=3).value == None:
                        embed = discord.Embed(title=AnsweringSheet.cell(row=target , column=1).value, description=f'刪除之訊息：\n「{AnsweringSheet.cell(row=target , column=2).value}」' , color=0xff0000)
                        embed.set_author(name=f'前第{num}個被刪除/編輯的文字訊息' , url=None , icon_url=None)
                        embed.add_field(name="傳送訊息時間", value=AnsweringSheet.cell(row=target , column=4).value , inline=True)
                        embed.add_field(name="刪除訊息時間", value=AnsweringSheet.cell(row=target , column=5).value , inline=True)
                    else:
                        embed = discord.Embed(title=AnsweringSheet.cell(row=target , column=1).value, description=f'原訊息：\n「{AnsweringSheet.cell(row=target , column=2).value}」\n編輯後之訊息：\n「{AnsweringSheet.cell(row=target , column=3).value}」' , color=0xff0000)
                        embed.set_author(name=f'前第{num}個被刪除/編輯的文字訊息' , url=None , icon_url=None)
                        embed.add_field(name="傳送訊息時間", value=AnsweringSheet.cell(row=target , column=4).value , inline=True)
                        embed.add_field(name="編輯訊息時間", value=AnsweringSheet.cell(row=target , column=5).value , inline=True)
                    await ctx.send(embed=embed)
                else:
                    await ctx.send('查無該紀錄')
        else:
            await ctx.reply('編號需小於100 或是輸入all來獲得全部紀錄')

    @commands.command()
    async def historyf(self , ctx , *num):
        try:
            num = num[0]
        except:
            num = 1
        path = f'messageHistory\\{ctx.guild}\\{ctx.channel}\\files'
        file_list = os.listdir(f'{path}')
        if len(file_list) != 0:
            file_list.sort(key=lambda x: os.path.getmtime(f'{path}\\{x}') , reverse = True)
            await ctx.send(f'前第{num}個被刪除的檔案訊息')
            await ctx.send(file=discord.File(f'{path}\\{file_list[int(num)-1]}'))
            file_path = f'{path}\\{file_list[int(num)-1]}'
            author = file_list[int(num)-1].split('➼')[0]
            await ctx.send(f'傳送者：{author}\n刪除訊息時間：{time.strftime("%Y-%m-%d %H:%M:%S" , time.localtime(os.path.getmtime(file_path)))}')
        else:
            await ctx.send('無已刪除檔案訊息')

    def SaveDeletedMessage(self , message , DeletedTime):
        if not os.path.isdir(f'messageHistory\\{message.guild}\\{message.channel}'):
            os.makedirs(f'messageHistory\\{message.guild}\\{message.channel}')
        if not os.path.isfile(f'messageHistory\\{message.guild}\\{message.channel}\\{message.channel}_messageHistory.xlsx'):
            AnsweringBook = openpyxl.Workbook()
            AnsweringSheet = AnsweringBook.active
            AnsweringSheet.append(('傳送者' , '原始訊息內容' , '修改後訊息內容' , '傳送時間' , '刪除/編輯時間'))
            AnsweringBook.save(f'messageHistory\\{message.guild}\\{message.channel}\\{message.channel}_messageHistory.xlsx')
        AnsweringBook = openpyxl.load_workbook(f'messageHistory\\{message.guild}\\{message.channel}\\{message.channel}_messageHistory.xlsx')
        AnsweringSheet = AnsweringBook.worksheets[0]
        if AnsweringSheet.max_row >= 100:
            for i in range(2 , AnsweringSheet.max_row):
                if time.strptime(AnsweringSheet.cell(row=i , column=5).value , "%Y-%m-%d %H:%M:%S") > time.strptime(AnsweringSheet.cell(row=i+1 , column=5).value , "%Y-%m-%d %H:%M:%S"):
                    AnsweringSheet.cell(row=i+1 , column=1 , value=str(message.author))
                    AnsweringSheet.cell(row=i+1 , column=2 , value=str(message.content))
                    AnsweringSheet.cell(row=i+1 , column=3 , value="")
                    AnsweringSheet.cell(row=i+1 , column=4 , value=str((message.created_at + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")))
                    AnsweringSheet.cell(row=i+1 , column=5 , value=str(DeletedTime))
                    break
                if i == AnsweringSheet.max_row-1:
                    AnsweringSheet.cell(row=2 , column=1 , value=str(message.author))
                    AnsweringSheet.cell(row=2 , column=2 , value=str(message.content))
                    AnsweringSheet.cell(row=2 , column=3 , value="")
                    AnsweringSheet.cell(row=2 , column=4 , value=str((message.created_at + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")))
                    AnsweringSheet.cell(row=2 , column=5 , value=str(DeletedTime))
        else:
            AnsweringSheet.append((str(message.author) , str(message.content) ,'', str((message.created_at + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")) , str(DeletedTime)))
        AnsweringBook.save(f'messageHistory\\{message.guild}\\{message.channel}\\{message.channel}_messageHistory.xlsx')

    def SaveEdittedMessage(self , message_before , message_after , EdittedTime):
        if not os.path.isdir(f'messageHistory\\{message_before.guild}\\{message_before.channel}'):
            os.makedirs(f'messageHistory\\{message_before.guild}\\{message_before.channel}')
        if not os.path.isfile(f'messageHistory\\{message_before.guild}\\{message_before.channel}\\{message_before.channel}_messageHistory.xlsx'):
            AnsweringBook = openpyxl.Workbook()
            AnsweringSheet = AnsweringBook.active
            AnsweringSheet.append(('傳送者' , '原始訊息內容' , '修改後訊息內容' , '傳送時間' , '刪除/編輯時間'))
            AnsweringBook.save(f'messageHistory\\{message_before.guild}\\{message_before.channel}\\{message_before.channel}_messageHistory.xlsx')
        AnsweringBook = openpyxl.load_workbook(f'messageHistory\\{message_before.guild}\\{message_before.channel}\\{message_before.channel}_messageHistory.xlsx')
        AnsweringSheet = AnsweringBook.worksheets[0]
        if AnsweringSheet.max_row >= 100:
            for i in range(2 , AnsweringSheet.max_row):
                if time.strptime(AnsweringSheet.cell(row=i , column=5).value , "%Y-%m-%d %H:%M:%S") > time.strptime(AnsweringSheet.cell(row=i+1 , column=5).value , "%Y-%m-%d %H:%M:%S"):
                    AnsweringSheet.cell(row=i+1 , column=1 , value=str(message_before.author))
                    AnsweringSheet.cell(row=i+1 , column=2 , value=str(message_before.content))
                    AnsweringSheet.cell(row=i+1 , column=3 , value=str(message_after.content))
                    AnsweringSheet.cell(row=i+1 , column=4 , value=str((message_before.created_at + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")))
                    AnsweringSheet.cell(row=i+1 , column=5 , value=str(EdittedTime))
                    break
                if i == AnsweringSheet.max_row-1:
                    AnsweringSheet.cell(row=2 , column=1 , value=str(message_before.author))
                    AnsweringSheet.cell(row=2 , column=2 , value=str(message_before.content))
                    AnsweringSheet.cell(row=2 , column=3 , value=str(message_after.content))
                    AnsweringSheet.cell(row=2 , column=4 , value=str((message_before.created_at + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")))
                    AnsweringSheet.cell(row=2 , column=5 , value=str(EdittedTime))
        else:
            AnsweringSheet.append((str(message_before.author) , str(message_before.content) , str(message_after.content) , str((message_before.created_at + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")) , str(EdittedTime)))
        AnsweringBook.save(f'messageHistory\\{message_before.guild}\\{message_before.channel}\\{message_before.channel}_messageHistory.xlsx')

async def setup(bot):
    await bot.add_cog(message_history(bot))