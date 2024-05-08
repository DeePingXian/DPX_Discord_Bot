import discord
import pymysql , openpyxl , gdown , optparse        #打包用
from fake_useragent import UserAgent        #打包用
from discord.ext import commands , tasks        #打包用
from discord.ext.commands import Bot
import asyncio , os , shutil , requests , zipfile , json

async def main():

    if not os.path.isfile("assets/musicBot/ffmpeg.exe"):
        os.makedirs("assets/musicBot/temp" , exist_ok=True)
        print("初次啟動，下載必要檔案中...")
        with open("assets/musicBot/temp/ffmpeg-6.0-essentials_build.zip" , "wb") as f:
            f.write(requests.get("https://github.com/GyanD/codexffmpeg/releases/download/6.0/ffmpeg-6.0-essentials_build.zip").content)
        with zipfile.ZipFile("assets/musicBot/temp/ffmpeg-6.0-essentials_build.zip" , "r") as f:
            f.extractall("assets/musicBot/temp")
        shutil.move("assets/musicBot/temp/ffmpeg-6.0-essentials_build/bin/ffmpeg.exe" , "assets/musicBot")
    shutil.rmtree("assets/musicBot/temp" , ignore_errors=True)

    with open("settings.json" , "r" , encoding = "utf8") as jsonFile:
        settings = json.load(jsonFile)

    intents = discord.Intents.all()
    bot = Bot(command_prefix=settings["commandPrefix"] , intents=intents)
    bot.remove_command("help")

    #載入cogs

    CogFileList = []
    for CogFile in os.listdir("core/cogs"):
        if CogFile.endswith(".py"):
            await bot.load_extension(f"core.cogs.{CogFile[:-3]}")
            CogFileList.append(CogFile)

    #啟動時清除音樂機器人資料

    DB = bot.get_cog("MySQL")
    DB.init()
    if DB.test():
        print("MySQL 操作正常")
    else:
        print("MySQL 操作錯誤")

    #啟動訊息

    @bot.event
    async def on_ready():
        channel = bot.get_channel(settings["logChannelID"])
        game = discord.Game(f"輸入{settings['commandPrefix']}help查詢指令")
        await bot.change_presence(status=discord.Status.online, activity=game)
        ping = round (bot.latency * 1000)
        print(f"啟動完成｜bot身份為「{bot.user}」｜與 Discord 延遲為 {ping} ms")
        await channel.send("啟動完成")

    #錯誤訊息

    @bot.event
    async def on_command_error(ctx , error):
        try:
            await ctx.reply(f"發生錯誤\n{error}")
        except:
            pass

    @bot.event
    async def on_error(event , *args , **kwargs):
        try:
            message = args[0]
            await message.reply("發生錯誤")
        except:
            pass

    await bot.start(settings["TOKEN"])

if __name__ == "__main__":
    asyncio.run(main())