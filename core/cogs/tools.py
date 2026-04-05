import discord
from core.classes import Cog_Extension

class Tools(Cog_Extension):
    """Cog for utility commands and link generation."""

    @discord.app_commands.command(name="nh", description="產生 nhentai 本子連結")
    @discord.app_commands.describe(num="車號")
    async def nh(self, interaction: discord.Interaction, num: int):
        await interaction.response.send_message(f'https://nhentai.net/g/{num}')

    @discord.app_commands.command(name="jm", description="產生 18comic 本子連結")
    @discord.app_commands.describe(num="車號")
    async def jm(self, interaction: discord.Interaction, num: int):
        await interaction.response.send_message(f'https://18comic.org/album/{num}')

    @discord.app_commands.command(name="wn", description="產生 wnacg 本子連結")
    @discord.app_commands.describe(num="車號")
    async def wn(self, interaction: discord.Interaction, num: int):
        await interaction.response.send_message(f'https://www.wnacg.com/photos-index-aid-{num}')

    @discord.app_commands.command(name="pix", description="產生 Pixiv 作品連結")
    @discord.app_commands.describe(id="作品 ID")
    async def pix(self, interaction: discord.Interaction, id: int):
        await interaction.response.send_message(f'https://www.pixiv.net/artworks/{id}')

    @discord.app_commands.command(name="pixu", description="產生 Pixiv 作者連結")
    @discord.app_commands.describe(id="作者 ID")
    async def pixu(self, interaction: discord.Interaction, id: int):
        await interaction.response.send_message(f'https://www.pixiv.net/users/{id}')

    @discord.app_commands.command(name="twiu", description="產生 X (Twitter) 用戶連結")
    @discord.app_commands.describe(id="用戶 ID")
    async def twiu(self, interaction: discord.Interaction, id: str):
        await interaction.response.send_message(f'https://x.com/{id}')

async def setup(bot):
    await bot.add_cog(Tools(bot))
