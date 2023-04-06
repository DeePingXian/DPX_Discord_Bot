import discord
import pymysql , openpyxl , gdown        #編譯用
from discord.ext import commands , tasks        #編譯用
from discord.ext.commands import Bot
import asyncio , os , shutil , json

async def main():

    with open('settings.json' , 'r' , encoding = 'utf8') as json_file:
        settings = json.load(json_file)

    intents = discord.Intents.all()
    bot = Bot(command_prefix=settings['command_prefix'] , intents=intents)
    bot.remove_command("help")

    #載入cogs

    CogFileList = []
    for CogFile in os.listdir('core\\cogs'):
        if CogFile.endswith('.py'):
            await bot.load_extension(f'core.cogs.{CogFile[:-3]}')
            CogFileList.append(CogFile)
            print(f"已載入{CogFile}")

    #啟動時清除音樂機器人資料

    DB = bot.get_cog('MySQL')
    DB.Init()
    if DB.test():
        print('MySQL 操作正常')
    else:
        print('MySQL 操作錯誤')

    #清空musicTemp

    if os.path.isdir('assets/musicBot/musicTemp'):
        shutil.rmtree('assets/musicBot/musicTemp' , ignore_errors = True)

    #啟動訊息

    @bot.event
    async def on_ready():
        channel = bot.get_channel(settings['log_channel_id'])
        game = discord.Game(f'輸入{settings["command_prefix"]}help查詢指令')
        await bot.change_presence(status=discord.Status.online, activity=game)
        ping = round (bot.latency * 1000)
        print(f'啟動完成 與 Discord 延遲為 {ping} ms')
        await channel.send('啟動完成')
        DB.CleanAllMusicTable()

    @bot.event
    async def on_message(message):

        #訊息log
        
        try:
            if message.content != '' or message.attachments != []:
                DB.PutMessageLog(message , None , None , 0)
        except:
            if message.author != bot.user:
                raise ConnectionError('MySQL connection failed, can\'t create message log.')   

        await bot.process_commands(message)

    #錯誤訊息

    @bot.event
    async def on_command_error(ctx , error):
        await ctx.reply(f'發生錯誤\n{error}')
        await ctx.send(file=discord.File(settings['error_message_file']))

    @bot.event
    async def on_error(event , *args , **kwargs):
        message = args[0]
        await message.reply('發生錯誤')
        await message.channel.send(file=discord.File(settings['error_message_file']))

    await bot.start(settings['TOKEN'])

if __name__ == "__main__":
    asyncio.run(main())