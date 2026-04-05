from discord.ext import commands
from fake_useragent import UserAgent

class Cog_Extension(commands.Cog):
    """
    Base class for all bot cogs.
    Provides shared access to core services (DB, Redis, S3).
    """
    def __init__(self, bot):
        self.bot = bot
        
        # Inject core services from bot instance
        self.settings = getattr(bot, 'settings', {})
        self.db = getattr(bot, 'db', None)
        self.redis = getattr(bot, 'redis', None)
        self.s3 = getattr(bot, 's3', None)
        
        # Shared UserAgent for web requests
        self.userAgent = UserAgent(browsers=['Edge', 'Chrome'])
