import discord
from discord.ext import commands , tasks
from core.classes import Cog_Extension

class control(Cog_Extension):

    #bot狀態回報

    @discord.app_commands.command(name="status" , description="回傳 bot 狀態")
    async def status(self , interaction:discord.Interaction):
        if await self.bot.is_owner(interaction.user):
            embed = discord.Embed(title="bot狀態一覽", description='\u200b' , color=0xc0c0c0)
            embed.set_author(name="DPX discord bot" , url=None , icon_url=self.bot.user.avatar.url)
            embed.add_field(name="類別", value="與 Discord 網路延遲\nSQL資料庫作狀態" , inline=True)
            embed.add_field(name="狀態", value=f"{round(self.bot.latency * 1000)} ms\n{'正常' if self.DB.test() else '錯誤'}" , inline=True)
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("此功能僅限開此bot的管理員使用")

    #更新斜線指令(無效)
    
    """@discord.app_commands.command(name="synccommands" , description="更新 bot 指令")
    async def synccommands(self , interaction:discord.Interaction):
        if await self.bot.is_owner(interaction.user):
            successGuild = " "
            failedGuild = " "
            for guild in self.bot.guilds:
                try:
                    await self.bot.tree.sync(guild=guild)
                except discord.HTTPException:
                    failedGuild += f"{guild} "
                else:
                    successGuild += f"{guild} "
            if successGuild != " " and failedGuild == " ":
                await interaction.response.send_message(f"已成功同步{successGuild}的指令")
            elif successGuild != " " and failedGuild != " ":
                await interaction.response.send_message(f"已成功同步{successGuild}的指令\n以下則失敗{failedGuild}")
            else:
                await interaction.response.send_message("同步bot指令失敗")
        else:
            await interaction.response.send_message("此功能僅限開此bot的管理員使用")"""

    #log

    @commands.Cog.listener()
    async def on_ready(self):
        self.autoLog.start()

    @tasks.loop(hours=1)
    async def autoLog(self):
        await self.log()

    async def log(self):
        channel = self.bot.get_channel(self.settings["logChannelID"])
        word = f"與 Discord 延遲為 {round(self.bot.latency * 1000)} ms"
        word += "\nSQL資料庫操作正常" if self.DB.test() else "\nSQL資料庫操作錯誤"
        await channel.send(word)

async def setup(bot):
    await bot.add_cog(control(bot))