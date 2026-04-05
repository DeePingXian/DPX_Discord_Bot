import discord
from discord.ext import commands
from core.classes import Cog_Extension
import logging
import random
import re

MAX_ITEMS = 10

class Responder(Cog_Extension):
    """Cog for modular random Welcome Messages using components."""

    def __init__(self, bot):
        super().__init__(bot)
        self.logger = logging.getLogger("Responder")
        self.welcome_cache = {} # guild_id: config_dict

    async def cog_load(self):
        """Initial load of configurations into memory cache."""
        query = "SELECT guild_id, welcome_config FROM guild_configs"
        results = self.db.fetch_all(query)
        for guild_id, wel_cfg in results:
            self.welcome_cache[guild_id] = wel_cfg if wel_cfg else self._default_config()
        self.logger.info("Responder modular cache initialized.")

    def _default_config(self):
        """Standard fallback configuration."""
        return {
            "enabled": False,
            "channel_id": None, # Will fallback to system_channel if None
            "titles": ["歡迎加入！"],
            "messages": ["歡迎 <user> 加入伺服器！"],
            "images": [],
            "thumbnails": [],
            "colors": ["3498DB"]
        }

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Assemble a random welcome message from component pools."""
        config = self.welcome_cache.get(member.guild.id, self._default_config())
        
        if not config.get("enabled"):
            return

        # Determine target channel
        target_channel_id = config.get("channel_id")
        if target_channel_id:
            channel = self.bot.get_channel(int(target_channel_id))
        else:
            channel = member.guild.system_channel

        if not channel:
            return

        defaults = self._default_config()
        
        # Modular Random Selection
        title = random.choice(config.get("titles") or defaults["titles"])
        message_tpl = random.choice(config.get("messages") or defaults["messages"])
        message = message_tpl.replace("<user>", member.mention)
        color_hex = random.choice(config.get("colors") or defaults["colors"])
        
        image = random.choice(config.get("images")) if config.get("images") else None
        thumb = random.choice(config.get("thumbnails")) if config.get("thumbnails") else None

        embed = discord.Embed(title=title, description=message, color=int(color_hex, 16))
        if image: embed.set_image(url=image)
        if thumb: embed.set_thumbnail(url=thumb)
        
        try:
            await channel.send(embed=embed)
        except Exception as e:
            self.logger.error(f"Failed to send welcome message in {member.guild.name}: {e}")

    # --- Management Commands ---

    @discord.app_commands.command(name="welcome_list", description="查看目前的歡迎訊息元件清單與狀態")
    async def welcome_list(self, interaction: discord.Interaction):
        cfg = self.welcome_cache.get(interaction.guild.id, self._default_config())
        
        status_str = "🟢 啟用中" if cfg.get("enabled") else "🔴 已關閉"
        
        if cfg.get("channel_id"):
            channel_str = f"<#{cfg['channel_id']}>"
        elif interaction.guild.system_channel:
            channel_str = f"{interaction.guild.system_channel.mention} **(系統預設)**"
        else:
            channel_str = "*未設定且無系統頻道*"
        
        embed = discord.Embed(title="歡迎訊息系統狀態", color=discord.Color.blue())
        embed.description = f"**目前狀態：** {status_str}\n**發送頻道：** {channel_str}\n\n*提示：在訊息中使用 `<user>` 可標註該成員。*"
        
        categories = {
            "titles": "🏷️ 標題池",
            "messages": "💬 訊息池",
            "images": "🖼️ 大圖池",
            "thumbnails": "🖼️ 縮圖池",
            "colors": "🎨 顏色池"
        }
        
        for key, name in categories.items():
            items = cfg.get(key, [])
            val = ""
            if not items:
                val = "*目前為空*"
            else:
                for i, item in enumerate(items):
                    display_val = f"#{item}" if key == "colors" else item
                    line = f"`{i+1}.` {display_val}"
                    # Check field character limit (1024) - safety margin at 900
                    if len(val) + len(line) > 900:
                        val += f"... (剩餘 {len(items)-i} 個項目已隱藏)"
                        break
                    val += f"{line}\n"
            embed.add_field(name=name, value=val, inline=False)
            
        await interaction.response.send_message(embed=embed)

    @discord.app_commands.command(name="welcome_toggle", description="切換歡迎訊息功能的開啟或關閉")
    async def welcome_toggle(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ 您需要「管理伺服器」權限。", ephemeral=True)
            return

        cfg = self.welcome_cache.get(interaction.guild.id, self._default_config())
        cfg["enabled"] = not cfg.get("enabled", False)
        
        self.db.update_welcome_config(interaction.guild.id, cfg)
        self.welcome_cache[interaction.guild.id] = cfg
        status_str = "🟢 開啟" if cfg["enabled"] else "🔴 關閉"
        await interaction.response.send_message(f"✅ 歡迎訊息功能已切換為：**{status_str}**")

    @discord.app_commands.command(name="welcome_channel", description="設定歡迎訊息的發送頻道 (不輸入則使用系統預設)")
    @discord.app_commands.describe(channel="發送頻道 (留空則重置為系統預設)")
    async def welcome_channel(self, interaction: discord.Interaction, channel: discord.TextChannel = None):
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ 您需要「管理伺服器」權限。", ephemeral=True)
            return

        cfg = self.welcome_cache.get(interaction.guild.id, self._default_config())
        if channel:
            cfg["channel_id"] = str(channel.id)
            msg = f"✅ 歡迎頻道已設定為 {channel.mention}。"
        else:
            cfg["channel_id"] = None
            sys_channel = interaction.guild.system_channel
            sys_name = sys_channel.mention if sys_channel else "無"
            msg = f"✅ 歡迎頻道已重置為 {sys_name} **(系統預設)**。"
        
        self.db.update_welcome_config(interaction.guild.id, cfg)
        self.welcome_cache[interaction.guild.id] = cfg
        await interaction.response.send_message(msg)

    @discord.app_commands.command(name="welcome_add", description="新增歡迎訊息元件 (上限 10 個)")
    @discord.app_commands.describe(
        category="元件類別", 
        value="內容 (訊息類別可用 <user> 標註成員；顏色類別請輸入 6 位色碼如 00ff00)"
    )
    @discord.app_commands.choices(category=[
        discord.app_commands.Choice(name="標題 (Titles)", value="titles"),
        discord.app_commands.Choice(name="訊息 (Messages)", value="messages"),
        discord.app_commands.Choice(name="大圖網址 (Images)", value="images"),
        discord.app_commands.Choice(name="縮圖網址 (Thumbnails)", value="thumbnails"),
        discord.app_commands.Choice(name="色條顏色 (Colors)", value="colors")
    ])
    async def welcome_add(self, interaction: discord.Interaction, category: discord.app_commands.Choice[str], value: str):
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ 您需要「管理伺服器」權限。", ephemeral=True)
            return

        cfg = self.welcome_cache.get(interaction.guild.id, self._default_config())
        cat_key = category.value
        
        if len(cfg.get(cat_key, [])) >= MAX_ITEMS:
            await interaction.response.send_message(f"❌ 「{category.name}」已達 {MAX_ITEMS} 個上限，請先刪除舊項目。", ephemeral=True)
            return

        # Validation logic
        if cat_key == "colors":
            hex_val = value.lstrip("#")
            if not re.fullmatch(r"[0-9a-fA-F]{6}", hex_val):
                await interaction.response.send_message("❌ 顏色格式錯誤！請輸入 6 位 16 進位色碼 (例如: `00ff00`)。", ephemeral=True)
                return
            value = hex_val.lower()

        if cat_key not in cfg: cfg[cat_key] = []
        cfg[cat_key].append(value)
        
        self.db.update_welcome_config(interaction.guild.id, cfg)
        self.welcome_cache[interaction.guild.id] = cfg
        await interaction.response.send_message(f"✅ 已將新項目加入「{category.name}」池中。")

    @discord.app_commands.command(name="welcome_remove", description="刪除特定的歡迎訊息元件")
    @discord.app_commands.describe(category="元件類別", index="項目編號 (由 /welcome_list 查詢)")
    @discord.app_commands.choices(category=[
        discord.app_commands.Choice(name="標題 (Titles)", value="titles"),
        discord.app_commands.Choice(name="訊息 (Messages)", value="messages"),
        discord.app_commands.Choice(name="大圖網址 (Images)", value="images"),
        discord.app_commands.Choice(name="縮圖網址 (Thumbnails)", value="thumbnails"),
        discord.app_commands.Choice(name="色條顏色 (Colors)", value="colors")
    ])
    async def welcome_remove(self, interaction: discord.Interaction, category: discord.app_commands.Choice[str], index: int):
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ 您需要「管理伺服器」權限。", ephemeral=True)
            return

        cfg = self.welcome_cache.get(interaction.guild.id, self._default_config())
        cat_key = category.value
        items = cfg.get(cat_key, [])
        
        if index < 1 or index > len(items):
            await interaction.response.send_message(f"❌ 無效的編號。請參考 `/welcome_list`。", ephemeral=True)
            return

        removed_val = items.pop(index - 1)
        self.db.update_welcome_config(interaction.guild.id, cfg)
        self.welcome_cache[interaction.guild.id] = cfg
        await interaction.response.send_message(f"✅ 已從「{category.name}」刪除：`{removed_val[:30]}`")

async def setup(bot):
    await bot.add_cog(Responder(bot))
