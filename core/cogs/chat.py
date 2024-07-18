from discord.ext import commands
from core.classes import Cog_Extension
from characterai import aiocai
import discord

class chat(Cog_Extension):

    def __init__(self , bot):
        super().__init__(bot)
        self.characterID = self.settings["characteraiSettings"]["characterID"]
        self.client = aiocai.Client(self.settings["characteraiSettings"]["clientToken"])
        self.enabled = False
    
    @commands.Cog.listener()
    async def on_ready(self):
        if self.characterID and self.client:
            try:
                self.me = await self.client.get_me()
            except:
                raise ConnectionError("CharacterAI連線錯誤")
            else:
                self.enabled = True

    async def chat(self , guild , channel , prompt):
        self.DB.createDatabase(guild.id)
        self.DB.createCharacterAITable(guild.id)
        chatInfoID = self.DB.getCharacterAIChatID(guild.id)
        if not chatInfoID:
            await self.resetchat(guild , channel)
            chatInfoID = self.DB.getCharacterAIChatID(guild.id)
        answer = ""
        async with channel.typing():
            async with await self.client.connect() as chat:
                processPosition = 0
                while "<@" in prompt and ">" in prompt[processPosition:]:
                    object = prompt[prompt.find("<@"):prompt.find(">" , prompt.find("<@"))+1]
                    try:
                        startPostion = prompt.find("<@")
                        userName = self.bot.get_user(int(object[2:-1])).display_name
                        prompt = prompt.replace(object , userName)
                        processPosition = prompt.find(userName , startPostion)+1
                    except:
                        processPosition = prompt.find(">" , prompt.find("<@"))+1
                response = await chat.send_message(self.characterID , chatInfoID , prompt)
                answer = response.text
        await channel.send(answer)

    @commands.Cog.listener()
    async def on_message(self , message):
        if self.enabled and message.content.startswith(f"<@{self.bot.user.id}>") and message.content != f"<@{self.bot.user.id}>":
            await self.chat(message.guild , message.channel , message.content.partition(f"<@{self.bot.user.id}>")[2])

    @discord.app_commands.command(name="resetchat", description = "重設聊天")
    async def resetchat_(self ,interaction:discord.Interaction):
        if self.enabled:
            await interaction.response.defer()      #interaction.response.send_message需在3秒內回應 這樣可以隔15分鐘再回應
            self.DB.createDatabase(interaction.guild.id)
            self.DB.createCharacterAITable(interaction.guild.id)
            answer = ""
            async with await self.client.connect() as chat:
                chatInfo , response = await chat.new_chat(self.characterID , self.me.id)
                answer = response.text
                chatInfoID = chatInfo.chat_id
                self.DB.setCharacterAIChatID(interaction.guild.id , chatInfoID)
            await interaction.followup.send(answer)
        else:
            await interaction.response.send_message("未啟用此功能")

    async def resetchat(self , guild , channel):
        self.DB.createDatabase(guild.id)
        self.DB.createCharacterAITable(guild.id)
        #answer = ""
        #async with channel.typing():
        async with await self.client.connect() as chat:
            chatInfo , response = await chat.new_chat(self.characterID , self.me.id)
            #answer = response.text
            chatInfoID = chatInfo.chat_id
            self.DB.setCharacterAIChatID(guild.id , chatInfoID)
        #await channel.send(answer)
        await channel.send("> 聊天狀態已重設")

    @discord.app_commands.command(name="getchattokenemaillink" , description="取得Character.AI的連線token (步驟1/2)")
    @discord.app_commands.describe(email="要用於連線至Character.AI的帳號E-mail")
    async def getchattokenemail(self , interaction:discord.Interaction , email:str):
        from characterai import sendCode
        await interaction.response.defer(ephemeral=True)
        try:
            sendCode(email)
            await interaction.followup.send("E-mail已發送，請使用/getchattoken輸入E-mail裡的登入連結以取得token")
        except:
            await interaction.followup.send("E-mail發送失敗")

    @discord.app_commands.command(name="getchattoken" , description="取得Character.AI的連線token (步驟2/2)")
    @discord.app_commands.describe(email="取得登入連結的E-mail" , link="E-mail裡的登入連結")
    async def getchattoken(self , interaction:discord.Interaction , email:str , link:str):
        from characterai import authUser
        await interaction.response.defer(ephemeral=True)
        try:
            token = authUser(link , email)
            await interaction.followup.send(f"Character.AI的token為「{token}」，請設定至settings.json裡並重啟bot")       #如果做自動線上更新排版會亂掉
        except:
            await interaction.followup.send("取得token失敗")

async def setup(bot):
    await bot.add_cog(chat(bot))