from discord.ext import commands
from core.classes import Cog_Extension
import random

class generating_links(Cog_Extension):
    
    @commands.command()
    async def nh(self , ctx , book):
        if book == 'rand':
            await ctx.send(f'https://nhentai.net/g/{random.randrange(self.settings["newestNhentaiBookNum"])+1}')
        else:
            try:
                mes=int(book)
            except:
                await ctx.reply('車號僅能為數字')
            else:
                await ctx.send(f'https://nhentai.net/g/{mes}')
    
    @commands.command()
    async def jm(self , ctx , book):
        try:
            mes=int(book)
        except:
            await ctx.reply('車號僅能為數字')
        else:
            await ctx.send(f'https://18comic.org/album/{mes}')

    @commands.command()
    async def wn(self , ctx , book):
        try:
            mes=int(book)
        except:
            await ctx.reply('車號僅能為數字')
        else:
            await ctx.send(f'https://www.wnacg.com/photos-index-aid-{mes}')

    @commands.command()
    async def pix(self , ctx , art):
        try:
            mes=int(art)
        except:
            await ctx.reply('作品號僅能為數字')
        else:
            await ctx.send(f'https://www.pixiv.net/artworks/{mes}')

    @commands.command()
    async def pixu(self , ctx , user):
        await ctx.send(f'https://www.pixiv.net/users/{user}')

    @commands.command()
    async def twiu(self , ctx , user):
        await ctx.send(f'https://twitter.com/{user}')

async def setup(bot):
    await bot.add_cog(generating_links(bot))