import discord
import math
import random
from discord.ext import commands
from core.classes import Cog_Extension

class MajorArcana(Cog_Extension):

    @commands.command()
    async def MajorArcana(self , ctx , *word):
        try:
            word2 = ''
            for i in range(len(word)):
                word2 += ( word[i] + ' ' )
            word2 = word2.rstrip(' ')
            word = word2
        except:
            word = ''
        finally:
            random.seed(word)
            card = math.floor(random.random()*22)
            reverse = math.floor(random.random()*2)
            if card == 0:
                if reverse == 0:
                    await ctx.send(f'愚者')
                    await ctx.send(file=discord.File('.\\assets\\MajorArcana\\0.jpg'))
                else:
                    await ctx.send(f'愚者（逆位）')
                    await ctx.send(file=discord.File('.\\assets\\MajorArcana\\0_1.jpg'))
            if card == 1:
                if reverse == 0:
                    await ctx.send(f'魔術師')
                    await ctx.send(file=discord.File('.\\assets\\MajorArcana\\1.jpg'))
                else:
                    await ctx.send(f'魔術師（逆位）')
                    await ctx.send(file=discord.File('.\\assets\\MajorArcana\\1_1.jpg'))
            if card == 2:
                if reverse == 0:
                    await ctx.send(f'女祭司')
                    await ctx.send(file=discord.File('.\\assets\\MajorArcana\\2.jpg'))
                else:
                    await ctx.send(f'女祭司（逆位）')
                    await ctx.send(file=discord.File('.\\assets\\MajorArcana\\2_1.jpg'))
            if card == 3:
                if reverse == 0:
                    await ctx.send(f'皇后')
                    await ctx.send(file=discord.File('.\\assets\\MajorArcana\\3.jpg'))
                else:
                    await ctx.send(f'皇后（逆位）')
                    await ctx.send(file=discord.File('.\\assets\\MajorArcana\\3_1.jpg'))
            if card == 4:
                if reverse == 0:
                    await ctx.send(f'皇帝')
                    await ctx.send(file=discord.File('.\\assets\\MajorArcana\\4.jpg'))
                else:
                    await ctx.send(f'皇帝（逆位）')
                    await ctx.send(file=discord.File('.\\assets\\MajorArcana\\4_1.jpg'))
            if card == 5:
                if reverse == 0:
                    await ctx.send(f'教皇')
                    await ctx.send(file=discord.File('.\\assets\\MajorArcana\\5.jpg'))
                else:
                    await ctx.send(f'教皇（逆位）')
                    await ctx.send(file=discord.File('.\\assets\\MajorArcana\\5_1.jpg'))
            if card == 6:
                if reverse == 0:
                    await ctx.send(f'戀人')
                    await ctx.send(file=discord.File('.\\assets\\MajorArcana\\6.jpg'))
                else:
                    await ctx.send(f'戀人（逆位）')
                    await ctx.send(file=discord.File('.\\assets\\MajorArcana\\6_1.jpg'))
            if card == 7:
                if reverse == 0:
                    await ctx.send(f'戰車')
                    await ctx.send(file=discord.File('.\\assets\\MajorArcana\\7.jpg'))
                else:
                    await ctx.send(f'戰車（逆位）')
                    await ctx.send(file=discord.File('.\\assets\\MajorArcana\\7_1.jpg'))
            if card == 8:
                if reverse == 0:
                    await ctx.send(f'力量')
                    await ctx.send(file=discord.File('.\\assets\\MajorArcana\\8.jpg'))
                else:
                    await ctx.send(f'力量（逆位）')
                    await ctx.send(file=discord.File('.\\assets\\MajorArcana\\8_1.jpg'))
            if card == 9:
                if reverse == 0:
                    await ctx.send(f'隱者')
                    await ctx.send(file=discord.File('.\\assets\\MajorArcana\\9.jpg'))
                else:
                    await ctx.send(f'隱者（逆位）')
                    await ctx.send(file=discord.File('.\\assets\\MajorArcana\\9_1.jpg'))
            if card == 10:
                if reverse == 0:
                    await ctx.send(f'命運之輪')
                    await ctx.send(file=discord.File('.\\assets\\MajorArcana\\10.jpg'))
                else:
                    await ctx.send(f'命運之輪（逆位）')
                    await ctx.send(file=discord.File('.\\assets\\MajorArcana\\10_1.jpg'))
            if card == 11:
                if reverse == 0:
                    await ctx.send(f'正義')
                    await ctx.send(file=discord.File('.\\assets\\MajorArcana\\11.jpg'))
                else:
                    await ctx.send(f'正義（逆位）')
                    await ctx.send(file=discord.File('.\\assets\\MajorArcana\\11_1.jpg'))
            if card == 12:
                if reverse == 0:
                    await ctx.send(f'倒吊人')
                    await ctx.send(file=discord.File('.\\assets\\MajorArcana\\12.jpg'))
                else:
                    await ctx.send(f'倒吊人（逆位）')
                    await ctx.send(file=discord.File('.\\assets\\MajorArcana\\12_1.jpg'))
            if card == 13:
                if reverse == 0:
                    await ctx.send(f'死神')
                    await ctx.send(file=discord.File('.\\assets\\MajorArcana\\13.jpg'))
                else:
                    await ctx.send(f'死神（逆位）')
                    await ctx.send(file=discord.File('.\\assets\\MajorArcana\\13_1.jpg'))
            if card == 14:
                if reverse == 0:
                    await ctx.send(f'節制')
                    await ctx.send(file=discord.File('.\\assets\\MajorArcana\\14.jpg'))
                else:
                    await ctx.send(f'節制（逆位）')
                    await ctx.send(file=discord.File('.\\assets\\MajorArcana\\14_1.jpg'))
            if card == 15:
                if reverse == 0:
                    await ctx.send(f'惡魔')
                    await ctx.send(file=discord.File('.\\assets\\MajorArcana\\15.jpg'))
                else:
                    await ctx.send(f'惡魔（逆位）')
                    await ctx.send(file=discord.File('.\\assets\\MajorArcana\\15_1.jpg'))
            if card == 16:
                if reverse == 0:
                    await ctx.send(f'塔')
                    await ctx.send(file=discord.File('.\\assets\\MajorArcana\\16.jpg'))
                else:
                    await ctx.send(f'塔（逆位）')
                    await ctx.send(file=discord.File('.\\assets\\MajorArcana\\16_1.jpg'))
            if card == 17:
                if reverse == 0:
                    await ctx.send(f'星星')
                    await ctx.send(file=discord.File('.\\assets\\MajorArcana\\17.jpg'))
                else:
                    await ctx.send(f'星星（逆位）')
                    await ctx.send(file=discord.File('.\\assets\\MajorArcana\\17_1.jpg'))
            if card == 18:
                if reverse == 0:
                    await ctx.send(f'月亮')
                    await ctx.send(file=discord.File('.\\assets\\MajorArcana\\18.jpg'))
                else:
                    await ctx.send(f'月亮（逆位）')
                    await ctx.send(file=discord.File('.\\assets\\MajorArcana\\18_1.jpg'))
            if card == 19:
                if reverse == 0:
                    await ctx.send(f'太陽')
                    await ctx.send(file=discord.File('.\\assets\\MajorArcana\\19.jpg'))
                else:
                    await ctx.send(f'太陽（逆位）')
                    await ctx.send(file=discord.File('.\\assets\\MajorArcana\\19_1.jpg'))
            if card == 20:
                if reverse == 0:
                    await ctx.send(f'審判')
                    await ctx.send(file=discord.File('.\\assets\\MajorArcana\\20.jpg'))
                else:
                    await ctx.send(f'審判（逆位）')
                    await ctx.send(file=discord.File('.\\assets\\MajorArcana\\20_1.jpg'))
            if card == 21:
                if reverse == 0:
                    await ctx.send(f'世界')
                    await ctx.send(file=discord.File('.\\assets\\MajorArcana\\21.jpg'))
                else:
                    await ctx.send(f'世界（逆位）')
                    await ctx.send(file=discord.File('.\\assets\\MajorArcana\\21_1.jpg'))

    @commands.command()
    async def MajorArcana3(self , ctx , *word):
        try:
            word2 = ''
            for i in range(len(word)):
                word2 += ( word[i] + ' ' )
            word2 = word2.rstrip(' ')
            word = word2
        except:
            word = ''
        finally:
            random.seed(word)
            card1 = -1
            card2 = -1
            
            for i in range(3):

                if i == 0:
                    await ctx.send('過去：')
                elif i == 1:
                    await ctx.send('現在：')
                else:
                    await ctx.send('未來：')
                card = math.floor(random.random()*22)
                reverse = math.floor(random.random()*2)

                if ((card == card1) or (card == card2)):
                    i-=1
                    continue

                if card == 0:
                    if i == 0:
                        card1 = 0
                    if i == 1:
                        card2 = 0

                    if reverse == 0:
                        await ctx.send(f'愚者')
                        await ctx.send(file=discord.File('.\\assets\\MajorArcana\\0.jpg'))
                    else:
                        await ctx.send(f'愚者（逆位）')
                        await ctx.send(file=discord.File('.\\assets\\MajorArcana\\0_1.jpg'))
                if card == 1:
                    if i == 0:
                        card1 = 1
                    if i == 1:
                        card2 = 0

                    if reverse == 1:
                        await ctx.send(f'魔術師')
                        await ctx.send(file=discord.File('.\\assets\\MajorArcana\\1.jpg'))
                    else:
                        await ctx.send(f'魔術師（逆位）')
                        await ctx.send(file=discord.File('.\\assets\\MajorArcana\\1_1.jpg'))
                if card == 2:
                    if i == 0:
                        card1 = 2
                    if i == 1:
                        card2 = 2

                    if reverse == 0:
                        await ctx.send(f'女祭司')
                        await ctx.send(file=discord.File('.\\assets\\MajorArcana\\2.jpg'))
                    else:
                        await ctx.send(f'女祭司（逆位）')
                        await ctx.send(file=discord.File('.\\assets\\MajorArcana\\2_1.jpg'))
                if card == 3:
                    if i == 0:
                        card1 = 3
                    if i == 1:
                        card2 = 3

                    if reverse == 0:
                        await ctx.send(f'皇后')
                        await ctx.send(file=discord.File('.\\assets\\MajorArcana\\3.jpg'))
                    else:
                        await ctx.send(f'皇后（逆位）')
                        await ctx.send(file=discord.File('.\\assets\\MajorArcana\\3_1.jpg'))
                if card == 4:
                    if i == 0:
                        card1 = 4
                    if i == 1:
                        card2 = 4

                    if reverse == 0:
                        await ctx.send(f'皇帝')
                        await ctx.send(file=discord.File('.\\assets\\MajorArcana\\4.jpg'))
                    else:
                        await ctx.send(f'皇帝（逆位）')
                        await ctx.send(file=discord.File('.\\assets\\MajorArcana\\4_1.jpg'))
                if card == 5:
                    if i == 0:
                        card1 = 5
                    if i == 1:
                        card2 = 5

                    if reverse == 0:
                        await ctx.send(f'教皇')
                        await ctx.send(file=discord.File('.\\assets\\MajorArcana\\5.jpg'))
                    else:
                        await ctx.send(f'教皇（逆位）')
                        await ctx.send(file=discord.File('.\\assets\\MajorArcana\\5_1.jpg'))
                if card == 6:
                    if i == 0:
                        card1 = 6
                    if i == 1:
                        card2 = 6

                    if reverse == 0:
                        await ctx.send(f'戀人')
                        await ctx.send(file=discord.File('.\\assets\\MajorArcana\\6.jpg'))
                    else:
                        await ctx.send(f'戀人（逆位）')
                        await ctx.send(file=discord.File('.\\assets\\MajorArcana\\6_1.jpg'))
                if card == 7:
                    if i == 0:
                        card1 = 7
                    if i == 1:
                        card2 = 7

                    if reverse == 0:
                        await ctx.send(f'戰車')
                        await ctx.send(file=discord.File('.\\assets\\MajorArcana\\7.jpg'))
                    else:
                        await ctx.send(f'戰車（逆位）')
                        await ctx.send(file=discord.File('.\\assets\\MajorArcana\\7_1.jpg'))
                if card == 8:
                    if i == 0:
                        card1 = 8
                    if i == 1:
                        card2 = 8

                    if reverse == 0:
                        await ctx.send(f'力量')
                        await ctx.send(file=discord.File('.\\assets\\MajorArcana\\8.jpg'))
                    else:
                        await ctx.send(f'力量（逆位）')
                        await ctx.send(file=discord.File('.\\assets\\MajorArcana\\8_1.jpg'))
                if card == 9:
                    if i == 0:
                        card1 = 9
                    if i == 1:
                        card2 = 9

                    if reverse == 0:
                        await ctx.send(f'隱者')
                        await ctx.send(file=discord.File('.\\assets\\MajorArcana\\9.jpg'))
                    else:
                        await ctx.send(f'隱者（逆位）')
                        await ctx.send(file=discord.File('.\\assets\\MajorArcana\\9_1.jpg'))
                if card == 10:
                    if i == 0:
                        card1 = 10
                    if i == 1:
                        card2 = 10

                    if reverse == 0:
                        await ctx.send(f'命運之輪')
                        await ctx.send(file=discord.File('.\\assets\\MajorArcana\\10.jpg'))
                    else:
                        await ctx.send(f'命運之輪（逆位）')
                        await ctx.send(file=discord.File('.\\assets\\MajorArcana\\10_1.jpg'))
                if card == 11:
                    if i == 0:
                        card1 = 11
                    if i == 1:
                        card2 = 11

                    if reverse == 0:
                        await ctx.send(f'正義')
                        await ctx.send(file=discord.File('.\\assets\\MajorArcana\\11.jpg'))
                    else:
                        await ctx.send(f'正義（逆位）')
                        await ctx.send(file=discord.File('.\\assets\\MajorArcana\\11_1.jpg'))
                if card == 12:
                    if i == 0:
                        card1 = 12
                    if i == 1:
                        card2 = 12

                    if reverse == 0:
                        await ctx.send(f'倒吊人')
                        await ctx.send(file=discord.File('.\\assets\\MajorArcana\\12.jpg'))
                    else:
                        await ctx.send(f'倒吊人（逆位）')
                        await ctx.send(file=discord.File('.\\assets\\MajorArcana\\12_1.jpg'))
                if card == 13:
                    if i == 0:
                        card1 = 13
                    if i == 1:
                        card2 = 13

                    if reverse == 0:
                        await ctx.send(f'死神')
                        await ctx.send(file=discord.File('.\\assets\\MajorArcana\\13.jpg'))
                    else:
                        await ctx.send(f'死神（逆位）')
                        await ctx.send(file=discord.File('.\\assets\\MajorArcana\\13_1.jpg'))
                if card == 14:
                    if i == 0:
                        card1 = 14
                    if i == 1:
                        card2 = 14

                    if reverse == 0:
                        await ctx.send(f'節制')
                        await ctx.send(file=discord.File('.\\assets\\MajorArcana\\14.jpg'))
                    else:
                        await ctx.send(f'節制（逆位）')
                        await ctx.send(file=discord.File('.\\assets\\MajorArcana\\14_1.jpg'))
                if card == 15:
                    if i == 0:
                        card1 = 15
                    if i == 1:
                        card2 = 15

                    if reverse == 0:
                        await ctx.send(f'惡魔')
                        await ctx.send(file=discord.File('.\\assets\\MajorArcana\\15.jpg'))
                    else:
                        await ctx.send(f'惡魔（逆位）')
                        await ctx.send(file=discord.File('.\\assets\\MajorArcana\\15_1.jpg'))
                if card == 16:
                    if i == 0:
                        card1 = 16
                    if i == 1:
                        card2 = 16

                    if reverse == 0:
                        await ctx.send(f'塔')
                        await ctx.send(file=discord.File('.\\assets\\MajorArcana\\16.jpg'))
                    else:
                        await ctx.send(f'塔（逆位）')
                        await ctx.send(file=discord.File('.\\assets\\MajorArcana\\16_1.jpg'))
                if card == 17:
                    if i == 0:
                        card1 = 17
                    if i == 1:
                        card2 = 17

                    if reverse == 0:
                        await ctx.send(f'星星')
                        await ctx.send(file=discord.File('.\\assets\\MajorArcana\\17.jpg'))
                    else:
                        await ctx.send(f'星星（逆位）')
                        await ctx.send(file=discord.File('.\\assets\\MajorArcana\\17_1.jpg'))
                if card == 18:
                    if i == 0:
                        card1 = 18
                    if i == 1:
                        card2 = 18

                    if reverse == 0:
                        await ctx.send(f'月亮')
                        await ctx.send(file=discord.File('.\\assets\\MajorArcana\\18.jpg'))
                    else:
                        await ctx.send(f'月亮（逆位）')
                        await ctx.send(file=discord.File('.\\assets\\MajorArcana\\18_1.jpg'))
                if card == 19:
                    if i == 0:
                        card1 = 19
                    if i == 1:
                        card2 = 19

                    if reverse == 0:
                        await ctx.send(f'太陽')
                        await ctx.send(file=discord.File('.\\assets\\MajorArcana\\19.jpg'))
                    else:
                        await ctx.send(f'太陽（逆位）')
                        await ctx.send(file=discord.File('.\\assets\\MajorArcana\\19_1.jpg'))
                if card == 20:
                    if i == 0:
                        card1 = 20
                    if i == 1:
                        card2 = 20

                    if reverse == 0:
                        await ctx.send(f'審判')
                        await ctx.send(file=discord.File('.\\assets\\MajorArcana\\20.jpg'))
                    else:
                        await ctx.send(f'審判（逆位）')
                        await ctx.send(file=discord.File('.\\assets\\MajorArcana\\20_1.jpg'))
                if card == 21:
                    if i == 0:
                        card1 = 21
                    if i == 1:
                        card2 = 21

                    if reverse == 0:
                        await ctx.send(f'世界')
                        await ctx.send(file=discord.File('.\\assets\\MajorArcana\\21.jpg'))
                    else:
                        await ctx.send(f'世界（逆位）')
                        await ctx.send(file=discord.File('.\\assets\\MajorArcana\\21_1.jpg'))

def setup(bot):
    bot.add_cog(MajorArcana(bot))