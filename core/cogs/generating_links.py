from core.classes import Cog_Extension
import discord , random

class generating_links(Cog_Extension):
    
    @discord.app_commands.command(name="nh" , description="傳送該nh本子連結")
    @discord.app_commands.describe(num="車號")
    async def nh(self , interaction:discord.Interaction , num:int):
        await interaction.response.send_message(f'https://nhentai.net/g/{num}')

    @discord.app_commands.command(name="nhrand" , description="隨機傳送nh本子連結")
    async def nhrand(self , interaction:discord.Interaction):
        await interaction.response.send_message(f'https://nhentai.net/g/{random.randrange(self.settings["newestnhBookNum"])+1}')

    @discord.app_commands.command(name="jm" , description="傳送該JM本子連結")
    @discord.app_commands.describe(num="車號")
    async def jm(self , interaction:discord.Interaction , num:int):
        await interaction.response.send_message(f'https://18comic.org/album/{num}')

    @discord.app_commands.command(name="wn" , description="傳送該wnacg本子連結")
    @discord.app_commands.describe(num="車號")
    async def wn(self , interaction:discord.Interaction , num:int):
        await interaction.response.send_message(f'https://www.wnacg.com/photos-index-aid-{num}')

    @discord.app_commands.command(name="pix" , description="傳送該pixiv作品連結")
    @discord.app_commands.describe(id="作品編號")
    async def pix(self , interaction:discord.Interaction , id:int):
        await interaction.response.send_message(f'https://www.pixiv.net/artworks/{id}')

    @discord.app_commands.command(name="pixu" , description="傳送該pixiv作者連結")
    @discord.app_commands.describe(id="作者編號")
    async def pixu(self , interaction:discord.Interaction , id:int):
        await interaction.response.send_message(f'https://www.pixiv.net/users/{id}')

    @discord.app_commands.command(name="twiu" , description="傳送該twitter用戶連結")
    @discord.app_commands.describe(id="用戶ID")
    async def twiu(self , interaction:discord.Interaction , id:int):
        await interaction.response.send_message(f'https://x.com/{id}')

async def setup(bot):
    await bot.add_cog(generating_links(bot))