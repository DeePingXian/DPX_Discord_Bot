from discord.ext import commands
from core.classes import Cog_Extension
from PyCharacterAI import get_client
import discord

class chat(Cog_Extension):

    def __init__(self, bot):
        super().__init__(bot)
        self.characterID = self.settings["characteraiSettings"]["characterID"]
        self.enabled = False
    
    @commands.Cog.listener()
    async def on_ready(self):
        if self.characterID:
            try:
                self.client = await get_client(token=self.settings["characteraiSettings"]["clientToken"])
                self.me = await self.client.account.fetch_me()
            except:
                raise ConnectionError("CharacterAI連線錯誤")
            else:
                await self.client.close_session()
                self.enabled = True

    async def chat(self, guild, channel, prompt):
        self.DB.createDatabase(guild.id)
        self.DB.createCharacterAITable(guild.id)
        chatInfoID = self.DB.getCharacterAIChatID(guild.id)
        if not chatInfoID:
            await self.resetchat(guild, channel)
            chatInfoID = self.DB.getCharacterAIChatID(guild.id)
        async with channel.typing():
            processPosition = 0
            while "<@" in prompt and ">" in prompt[processPosition:]:
                object = prompt[prompt.find("<@"):prompt.find(">", prompt.find("<@"))+1]
                try:
                    startPostion = prompt.find("<@")
                    userName = self.bot.get_user(int(object[2:-1])).display_name
                    prompt = prompt.replace(object, userName)
                    processPosition = prompt.find(userName, startPostion)+1
                except:
                    processPosition = prompt.find(">", prompt.find("<@"))+1
            response = await self.client.chat.send_message(self.characterID, chatInfoID, prompt, streaming=True)
            answered = False
            answer = ""
            msg = None
            async for message in response:
                answer = message.get_primary_candidate().text
                if not answered:
                    msg = await channel.send(answer)
                    answered = True
                else:
                    await msg.edit(content=answer)
        await self.client.close_session()

    @commands.Cog.listener()
    async def on_message(self, message):
        if self.enabled and message.content.startswith(f"<@{self.bot.user.id}>") and message.content != f"<@{self.bot.user.id}>":
            await self.chat(message.guild, message.channel, message.content.partition(f"<@{self.bot.user.id}>")[2])

    @discord.app_commands.command(name="dellastmsg", description = "刪除上一則聊天訊息")
    async def dellastmsg(self, interaction: discord.Interaction):
        if self.enabled:
            await interaction.response.defer()      #interaction.response.send_message需在3秒內回應 這樣可以隔15分鐘再回應
            self.DB.createDatabase(interaction.guild.id)
            self.DB.createCharacterAITable(interaction.guild.id)
            chatInfoID = self.DB.getCharacterAIChatID(interaction.guild.id)
            if not chatInfoID:
                await interaction.followup.send("> 無聊天訊息可刪除")
            else:
                de = False
                errorMsg = ""
                nextToken = None
                messages, nextToken = await self.client.chat.fetch_messages(chatInfoID, next_token=nextToken)

                try:
                    de = await self.client.chat.delete_message(chatInfoID, messages[0].turn_id)
                    await self.client.close_session()
                except Exception as e:
                    errorMsg = e
                if de:
                    await interaction.followup.send(f"> 已刪除上一則訊息「{messages[0].get_primary_candidate().text}」")
                else:
                    await interaction.followup.send(f"> 刪除訊息失敗：\n{errorMsg}")

    @discord.app_commands.command(name="resetchat", description = "重設聊天")
    async def resetchat_(self, interaction:discord.Interaction):
        if self.enabled:
            await interaction.response.defer()      #interaction.response.send_message需在3秒內回應 這樣可以隔15分鐘再回應
            self.DB.createDatabase(interaction.guild.id)
            self.DB.createCharacterAITable(interaction.guild.id)
            answer = ""
            chatInfo, greetingMessage = await self.client.chat.create_chat(self.characterID)
            chatInfoID = chatInfo.chat_id
            answer = greetingMessage.get_primary_candidate().text
            await self.client.close_session()
            self.DB.setCharacterAIChatID(interaction.guild.id, chatInfoID)
            await interaction.followup.send(answer)
        else:
            await interaction.response.send_message("未啟用此功能")

    async def resetchat(self, guild, channel):
        self.DB.createDatabase(guild.id)
        self.DB.createCharacterAITable(guild.id)
        chatInfo, greetingMessage = await self.client.chat.create_chat(self.characterID)
        chatInfoID = chatInfo.chat_id
        await self.client.close_session()
        self.DB.setCharacterAIChatID(guild.id, chatInfoID)
        await channel.send("> 聊天狀態已重設")

    @discord.app_commands.command(name="getchattokenemaillink", description="取得Character.AI的連線token (步驟1/2)")
    @discord.app_commands.describe(email="要用於連線至Character.AI的帳號E-mail")
    async def getchattokenemail(self, interaction:discord.Interaction, email:str):
        from characterai import sendCode
        await interaction.response.defer(ephemeral=True)
        try:
            sendCode(email)
            await interaction.followup.send("E-mail已發送，請使用/getchattoken輸入E-mail裡的登入連結以取得token")
        except:
            await interaction.followup.send("E-mail發送失敗")

    @discord.app_commands.command(name="getchattoken", description="取得Character.AI的連線token (步驟2/2)")
    @discord.app_commands.describe(email="取得登入連結的E-mail", link="E-mail裡的登入連結")
    async def getchattoken(self, interaction:discord.Interaction, email:str, link:str):
        from characterai import authUser
        await interaction.response.defer(ephemeral=True)
        try:
            token = authUser(link, email)
            await interaction.followup.send(f"Character.AI的token為「{token}」，請設定至settings.json裡並重啟bot")       #如果做自動線上更新排版會亂掉
        except:
            await interaction.followup.send("取得token失敗")

async def setup(bot):
    await bot.add_cog(chat(bot))