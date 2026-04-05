import discord
import asyncio
import os
import logging
from discord.ext import commands, tasks
from dotenv import load_dotenv

from core.services.database import DatabaseService
from core.services.cache import CacheService
from core.services.storage import StorageService

# Load environment variables from .env file
load_dotenv()

# Global Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("Main")

class DiscordBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = None
        self.redis = None
        self.s3 = None

    async def setup_hook(self):
        # 4. Load Cog Extensions
        modern_cogs = ["history", "music", "responder", "admin", "tools", "help"]
        for cog in modern_cogs:
            try:
                await self.load_extension(f"core.cogs.{cog}")
                logger.info(f"Loaded extension: {cog}")
            except Exception as e:
                logger.error(f"Failed to load extension {cog}: {e}")
        
        # Start the tunnel monitor task
        self.tunnel_monitor.start()

    @tasks.loop(minutes=1)
    async def tunnel_monitor(self):
        """Monitor and update Cloudflare Tunnel URL"""
        if self.s3:
            old_url = self.s3.public_url
            new_url = self.s3.refresh_public_url()
            if new_url and new_url != old_url:
                logger.info(f"Detected new Cloudflare Tunnel URL: {new_url}")
                channel = self.get_channel(int(os.getenv("LOG_CHANNEL_ID", 0)))
                if channel:
                    await channel.send(f"🔗 **Cloudflare 穿隧網址已更新**\n附件下載連結現已導向：\n`{new_url}`")

    @tunnel_monitor.before_loop
    async def before_tunnel_monitor(self):
        await self.wait_until_ready()

async def main():
    # 1. Configuration Setup
    token = os.getenv("DISCORD_TOKEN")
    db_url = os.getenv("DB_URL")
    
    # --- Redis Dynamic URL Construction ---
    redis_host = os.getenv("REDIS_HOST", "redis")
    redis_port = os.getenv("REDIS_PORT", "6379")
    redis_pass = os.getenv("REDIS_PASSWORD", "")
    if redis_pass:
        redis_url = f"redis://:{redis_pass}@{redis_host}:{redis_port}/0"
    else:
        redis_url = f"redis://{redis_host}:{redis_port}/0"
    
    s3_endpoint = os.getenv("S3_ENDPOINT")
    s3_access = os.getenv("S3_ACCESS_KEY")
    s3_secret = os.getenv("S3_SECRET_KEY")
    s3_bucket = os.getenv("S3_BUCKET_NAME", "discord-bot-storage")
    log_channel_id = int(os.getenv("LOG_CHANNEL_ID", 0))
    
    prefix = "!!" 

    if not token:
        logger.critical("DISCORD_TOKEN environment variable is missing.")
        return

    # 2. Initialize Infrastructure Services with Retry Logic
    db, redis, s3 = None, None, None
    retries = 5
    while retries > 0:
        try:
            db = DatabaseService(db_url)
            redis = CacheService(redis_url)
            s3 = StorageService(s3_endpoint, s3_access, s3_secret, s3_bucket)
            logger.info("All infrastructure services initialized successfully.")
            break
        except Exception as e:
            retries -= 1
            if retries == 0:
                logger.critical(f"Failed to initialize core services after multiple attempts: {e}")
                return
            logger.warning(f"Core services not ready, retrying in 3 seconds... ({retries} attempts left)")
            await asyncio.sleep(3)

    # 3. Discord Bot Client Setup
    intents = discord.Intents.all()
    bot = DiscordBot(command_prefix=prefix, intents=intents)
    bot.remove_command("help")

    # Dependency Injection
    bot.db = db
    bot.redis = redis
    bot.s3 = s3
    bot.settings = {
        "logChannelID": log_channel_id,
        "commandPrefix": prefix
    }

    # 5. Core Events
    @bot.event
    async def on_ready():
        await bot.tree.sync()
        logger.info(f"Discord Bot is online as {bot.user}")
        channel = bot.get_channel(log_channel_id)
        if channel:
            await channel.send("✅ 啟動成功！")

    # Start Bot Execution
    async with bot:
        await bot.start(token)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application shut down by user.")
    except Exception as e:
        logger.error(f"Application encountered an unhandled error: {e}")
