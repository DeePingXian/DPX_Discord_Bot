import discord
from core.classes import Cog_Extension

class Help(Cog_Extension):
    """Cog for displaying help messages and command lists."""

    class HelpMessageMenu(discord.ui.View):
        def __init__(self, bot):
            super().__init__(timeout=60)
            self.bot = bot

        @discord.ui.select(
            placeholder="請選擇查詢類別", 
            min_values=1, 
            max_values=1,
            options=[
                discord.SelectOption(label="播音樂功能列表", emoji="🎵"),
                discord.SelectOption(label="訊息歷史紀錄功能列表", emoji="📜"),                
                discord.SelectOption(label="歡迎功能列表", emoji="🤖"),
                discord.SelectOption(label="產生連結功能列表", emoji="🔗"),
                discord.SelectOption(label="其他功能列表", emoji="⚙️")
            ]
        )
        async def select_callback(self, interaction: discord.Interaction, select):
            selection = select.values[0]
            embed = discord.Embed(title=selection, color=discord.Color.blue())
            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)

            if selection == "播音樂功能列表":
                embed.add_field(name="指令", value="/play + (網址)\n/pause\n/resume\n/skip\n/loop\n/stop\n/queue\n/nowplaying\n/join", inline=True)
                embed.add_field(name="功能", value="播放音樂 (YouTube/Bili/GD)\n暫停播放\n恢復播放\n跳過目前曲目\n切換單曲重複\n停止並清空隊列\n查看目前隊列\n查看現正播放\n加入語音頻道", inline=True)
                embed.set_footer(text="提示：若播放異常，請使用 /stop 後再試")
            
            elif selection == "訊息歷史紀錄功能列表":
                embed.add_field(name="指令", value="/history", inline=True)
                embed.add_field(name="功能", value="查詢最近 25 則紀錄", inline=True)
                embed.set_footer(text="系統會自動記錄訊息的編輯與刪除狀態，附件檔案30天後會自動清除")
            
            elif selection == "歡迎功能列表":
                embed.add_field(name="指令", value="/welcome_list\n/welcome_toggle\n/welcome_channel\n/welcome_add\n/welcome_remove", inline=True)
                embed.add_field(name="功能", value="查看目前的歡迎訊息元件清單與狀態\n切換歡迎訊息功能的開啟或關閉\n設定歡迎訊息的發送頻道\n新增歡迎訊息元件\n刪除特定的歡迎訊息元件", inline=True)
                embed.set_footer(text="歡迎訊息功能僅能由管理員統一配置")
            
            elif selection == "產生連結功能列表":
                embed.add_field(name="指令", value="/nh (車號)\n/jm (車號)\n/wn (車號)\n/pix (作品ID)\n/pixu (作者ID)\n/twiu (用戶ID)", inline=True)
                embed.add_field(name="功能", value="產生對應網站的快速連結", inline=True)
            
            else:
                embed.add_field(name="指令", value="/help\n/status", inline=True)
                embed.add_field(name="功能", value="顯示此指令選單\n查看機器人運行狀態", inline=True)

            await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.app_commands.command(name="help", description="顯示機器人指令查詢清單")
    async def help(self, interaction: discord.Interaction):
        view = self.HelpMessageMenu(self.bot)
        await interaction.response.send_message("請選擇您要查詢的功能類別：", view=view, delete_after=60)

async def setup(bot):
    await bot.add_cog(Help(bot))
