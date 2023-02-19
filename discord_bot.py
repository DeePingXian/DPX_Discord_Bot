import discord , os , shutil , json
from discord.ext import commands , tasks
from discord.ext.commands import Bot

with open('settings.json' , 'r' , encoding = 'utf8') as json_file:
    json_data = json.load(json_file)

intents = discord.Intents.all()
bot=Bot(command_prefix=json_data['command_prefix'] , intents=intents)
bot.remove_command("help")

#載入cogs

CogFileList = []
for CogFile in os.listdir('core\\cogs'):
    if CogFile.endswith('.py'):
        bot.load_extension(f'core.cogs.{CogFile[:-3]}')
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
    channel = bot.get_channel(json_data['log_channel_id'])
    game = discord.Game(f'輸入{json_data["command_prefix"]}help查詢指令')
    await bot.change_presence(status=discord.Status.online, activity=game)
    ping = round (bot.latency * 1000)
    print(f'啟動完成 與 Discord 延遲為 {ping} ms')
    await channel.send('啟動完成')
    DB.CleanAllMusicTable()

@bot.event
async def on_message(message):

    #訊息log
    
    if message.content != '' or message.attachments != []:
        DB.PutMessageLog(message , None , None , 0)

    await bot.process_commands(message)

#錯誤訊息

@bot.event
async def on_error(event, *args, **kwargs):
    message = args[0] #Gets the message object
    await SendErrorMessage(message)

@bot.event
async def on_command_error(ctx, error):
    await SendErrorMessage(f'{ctx.message}\n{error}')

async def SendErrorMessage(message):
    await message.reply('發生錯誤')
    await message.channel.send(file=discord.File(json_data['error_message_file']))

if __name__ == "__main__":
    bot.run(json_data['TOKEN'])