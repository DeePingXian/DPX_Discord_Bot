import discord
from discord.ext import tasks
from core.classes import Cog_Extension
import time
import logging

class Admin(Cog_Extension):
    """Cog for bot administration and status reporting."""

    def __init__(self, bot):
        super().__init__(bot)
        self.logger = logging.getLogger("Admin")
        self.start_time = time.time()

    async def cog_load(self):
        self.status_report_loop.start()

    async def cog_unload(self):
        self.status_report_loop.cancel()

    @discord.app_commands.command(name="status", description="回報機器人目前的運行狀態")
    async def status(self, interaction: discord.Interaction):
        """Display system health, latency, and all service connection statuses."""
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ 您需要「管理伺服器」權限。", ephemeral=True)
            return

        uptime_seconds = int(time.time() - self.start_time)
        uptime = time.strftime("%H:%M:%S", time.gmtime(uptime_seconds))
        latency = round(self.bot.latency * 1000)
        
        embed = discord.Embed(title="系統運行狀態", color=discord.Color.blue())
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
        
        # 1. Basic Info
        embed.add_field(name="網路延遲", value=f"`{latency} ms`", inline=False)
        embed.add_field(name="運行時間", value=f"`{uptime}`", inline=False)
        
        # 2. Database (PostgreSQL) Status
        try:
            self.db.fetch_one("SELECT 1")
            db_status = "正常"
        except:
            db_status = "失敗"
        embed.add_field(name="PostgreSQL", value=db_status, inline=False)

        # 3. Cache (Redis) Status
        try:
            self.redis.client.ping()
            redis_status = "正常"
        except:
            redis_status = "失敗"
        embed.add_field(name="Redis", value=redis_status, inline=False)

        # 4. Storage (MinIO/S3) Status
        try:
            # We check the public URL directly or try to contact internal endpoint
            public_url = self.s3.public_url if self.s3 else None
            if public_url:
                s3_status = f"已穿隧\n`{public_url}`"
            else:
                s3_status = "內部連線正常 (公網未就緒)"
        except:
            s3_status = "失敗"
        embed.add_field(name="MinIO (S3)", value=s3_status, inline=False)

        await interaction.response.send_message(embed=embed)

    @tasks.loop(hours=1)
    async def status_report_loop(self):
        """Periodically log system status to the designated log channel."""
        log_channel_id = self.settings.get("logChannelID")
        if not log_channel_id:
            return

        channel = self.bot.get_channel(log_channel_id)
        if not channel:
            return

        latency = round(self.bot.latency * 1000)
        db_ok = "OK"
        try: self.db.fetch_one("SELECT 1")
        except: db_ok = "ERROR"
        
        redis_ok = "OK"
        try: self.redis.client.ping()
        except: redis_ok = "ERROR"

        msg = f"**每小時系統報告**\n- 延遲: `{latency}ms` | DB: `{db_ok}` | Redis: `{redis_ok}`"
        if self.s3 and self.s3.public_url:
            msg += f"\n- S3 網址: `{self.s3.public_url}`"

        await channel.send(msg)

async def setup(bot):
    await bot.add_cog(Admin(bot))
