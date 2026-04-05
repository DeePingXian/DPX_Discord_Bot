import discord
from discord.ext import commands
from core.classes import Cog_Extension
import aiohttp
import datetime
import logging

class History(Cog_Extension):
    """Modernized Cog for managing message history using PostgreSQL and MinIO."""

    def __init__(self, bot):
        super().__init__(bot)
        self.logger = logging.getLogger("History")

    async def _download_attachment(self, url):
        """Download attachment asynchronously."""
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    return await resp.read()
        return None
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return
        
        if message.content or message.attachments:
            query = """
                INSERT INTO message_logs 
                (guild_id, channel_id, author_id, author_name, content, message_type, sent_at)
                VALUES (%s, %s, %s, %s, %s, 0, %s)
            """
            params = (
                message.guild.id, message.channel.id, message.author.id, 
                str(message.author), message.content, message.created_at
            )
            self.db.execute(query, params)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot or not message.guild:
            return

        attachment_url = None
        if message.attachments:
            attachment = message.attachments[0]
            file_data = await self._download_attachment(attachment.url)
            if file_data:
                file_hash, s3_key = await self.s3.upload_file(file_data, attachment.filename)
                attachment_url = s3_key
                self.db.execute(
                    "INSERT INTO file_registry (file_hash, s3_key, file_size, mime_type) VALUES (%s, %s, %s, %s) ON CONFLICT (file_hash) DO NOTHING",
                    (file_hash, s3_key, len(file_data), attachment.content_type)
                )

        query = """
            INSERT INTO message_logs 
            (guild_id, channel_id, author_id, author_name, content, attachment_url, message_type, sent_at)
            VALUES (%s, %s, %s, %s, %s, %s, 2, %s)
        """
        params = (
            message.guild.id, message.channel.id, message.author.id, 
            str(message.author), message.content, attachment_url, message.created_at
        )
        self.db.execute(query, params)

    @commands.Cog.listener()
    async def on_message_edit(self, message_before, message_after):
        if message_after.author.bot or not message_after.guild or message_before.content == message_after.content:
            return

        query = """
            INSERT INTO message_logs 
            (guild_id, channel_id, author_id, author_name, content, content_old, message_type, sent_at)
            VALUES (%s, %s, %s, %s, %s, %s, 1, %s)
        """
        params = (
            message_after.guild.id, message_after.channel.id, message_after.author.id, 
            str(message_after.author), message_after.content, message_before.content, message_after.created_at
        )
        self.db.execute(query, params)

    # --- Integrated UI View ---

    class GetMessageHistory(discord.ui.View):
        def __init__(self, interaction, db, s3):
            super().__init__(timeout=60)
            self.db = db
            self.s3 = s3
            query = """
                SELECT author_id, author_name, content, message_type, sent_at, recorded_at, attachment_url, content_old
                FROM message_logs 
                WHERE channel_id = %s AND message_type IN (1, 2)
                ORDER BY recorded_at DESC LIMIT 25
            """
            self.messages = db.fetch_all(query, (interaction.channel.id,))
            
            if not self.messages:
                return

            options = []
            for i, msg in enumerate(self.messages):
                content = msg[2]
                author_name = msg[1]
                m_type = msg[3]
                
                label = content[:46] + "..." if content and len(content) > 50 else (content if content else "(附件檔案)")
                type_prefix = "【刪除】" if m_type == 2 else "【編輯】"
                
                options.append(discord.SelectOption(
                    label=f"{i+1:02d}. {label}",
                    description=f"作者: {author_name} {type_prefix}",
                    value=str(i)
                ))
            
            self.select_menu = discord.ui.Select(
                placeholder="請選擇已編輯/刪除的訊息",
                options=options
            )
            self.select_menu.callback = self.select_callback
            self.add_item(self.select_menu)

        async def select_callback(self, interaction: discord.Interaction):
            idx = int(self.select_menu.values[0])
            msg = self.messages[idx]
            # 0:author_id, 1:author_name, 2:content, 3:type, 4:sent_at, 5:recorded_at, 6:attachment_url, 7:content_old
            
            m_type = msg[3]
            type_str = '刪除' if m_type == 2 else '編輯'
            embed = discord.Embed(title=f"前第 {idx+1} 個被{type_str}的訊息", color=discord.Color.red())
            
            if m_type == 1: # Edited
                embed.description = f"作者: <@{msg[0]}>\n\n**原始訊息:**\n「{msg[7]}」\n\n**修改後訊息:**\n「{msg[2]}」"
            else: # Deleted
                embed.description = f"作者: <@{msg[0]}>\n\n**刪除之訊息:**\n{msg[2] if msg[2] else '(附件檔案)'}"
            
            time_sent = (msg[4] + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
            time_recorded = (msg[5] + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
            
            embed.add_field(name="原始傳送時間 (CST)", value=time_sent, inline=True)
            embed.add_field(name=f"{type_str}時間 (CST)", value=time_recorded, inline=True)
            
            if msg[6]: # attachment_url exists
                s3_key = msg[6]
                
                # Step 1: Check if file still exists in MinIO
                if await self.s3.exists(s3_key):
                    download_url = await self.s3.get_download_url(s3_key)
                    
                    # Step 2: Check if URL is public
                    if "trycloudflare.com" in download_url:
                        embed.add_field(name="附件檔案紀錄", value=f"[📥 點此下載檔案]({download_url})", inline=False)
                        img_exts = ['jpg', 'jpeg', 'png', 'webp', 'gif']
                        if any(s3_key.lower().endswith(ext) for ext in img_exts):
                            embed.set_image(url=download_url)
                    else:
                        embed.add_field(name="附件檔案紀錄", value="⚠️ 公網下載通道尚未就緒，請稍後再試。", inline=False)
                else:
                    # File has been deleted by MinIO lifecycle or manually
                    embed.add_field(name="附件檔案紀錄", value="⚠️ 附件檔案已過期或已由系統自動清理 (超過 30 天)。", inline=False)

            await interaction.response.send_message(embed=embed)

    # --- Command ---

    @discord.app_commands.command(name="history", description="查詢最近25則修改或刪除的訊息 (包含附件)")
    async def history(self, interaction: discord.Interaction):
        view = self.GetMessageHistory(interaction, self.db, self.s3)
        if not view.messages:
            await interaction.response.send_message("此頻道尚無編輯或刪除紀錄。")
        else:
            await interaction.response.send_message("最近 25 則修改的訊息歷史紀錄查詢列表", view=view)

async def setup(bot):
    await bot.add_cog(History(bot))
