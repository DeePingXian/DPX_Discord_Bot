import discord , random
from core.classes import Cog_Extension

class major_arcana(Cog_Extension):

    @discord.app_commands.command(name="majorarcana" , description="根據訊息內容使用大密儀塔羅牌占卜")
    @discord.app_commands.describe(message="訊息")
    async def majorarcana(self , interaction:discord.Interaction , message:str):
        random.seed(message)
        card = random.randrange(22)
        reverse = random.randrange(2)
        await interaction.response.send_message("占卜結果：")
        if card == 0:
            if reverse == 0:
                await interaction.channel.send(f'愚者')
                await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\0.jpg'))
            else:
                await interaction.channel.send(f'愚者（逆位）')
                await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\0_1.jpg'))
        if card == 1:
            if reverse == 0:
                await interaction.channel.send(f'魔術師')
                await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\1.jpg'))
            else:
                await interaction.channel.send(f'魔術師（逆位）')
                await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\1_1.jpg'))
        if card == 2:
            if reverse == 0:
                await interaction.channel.send(f'女祭司')
                await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\2.jpg'))
            else:
                await interaction.channel.send(f'女祭司（逆位）')
                await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\2_1.jpg'))
        if card == 3:
            if reverse == 0:
                await interaction.channel.send(f'皇后')
                await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\3.jpg'))
            else:
                await interaction.channel.send(f'皇后（逆位）')
                await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\3_1.jpg'))
        if card == 4:
            if reverse == 0:
                await interaction.channel.send(f'皇帝')
                await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\4.jpg'))
            else:
                await interaction.channel.send(f'皇帝（逆位）')
                await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\4_1.jpg'))
        if card == 5:
            if reverse == 0:
                await interaction.channel.send(f'教皇')
                await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\5.jpg'))
            else:
                await interaction.channel.send(f'教皇（逆位）')
                await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\5_1.jpg'))
        if card == 6:
            if reverse == 0:
                await interaction.channel.send(f'戀人')
                await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\6.jpg'))
            else:
                await interaction.channel.send(f'戀人（逆位）')
                await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\6_1.jpg'))
        if card == 7:
            if reverse == 0:
                await interaction.channel.send(f'戰車')
                await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\7.jpg'))
            else:
                await interaction.channel.send(f'戰車（逆位）')
                await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\7_1.jpg'))
        if card == 8:
            if reverse == 0:
                await interaction.channel.send(f'力量')
                await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\8.jpg'))
            else:
                await interaction.channel.send(f'力量（逆位）')
                await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\8_1.jpg'))
        if card == 9:
            if reverse == 0:
                await interaction.channel.send(f'隱者')
                await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\9.jpg'))
            else:
                await interaction.channel.send(f'隱者（逆位）')
                await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\9_1.jpg'))
        if card == 10:
            if reverse == 0:
                await interaction.channel.send(f'命運之輪')
                await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\10.jpg'))
            else:
                await interaction.channel.send(f'命運之輪（逆位）')
                await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\10_1.jpg'))
        if card == 11:
            if reverse == 0:
                await interaction.channel.send(f'正義')
                await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\11.jpg'))
            else:
                await interaction.channel.send(f'正義（逆位）')
                await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\11_1.jpg'))
        if card == 12:
            if reverse == 0:
                await interaction.channel.send(f'倒吊人')
                await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\12.jpg'))
            else:
                await interaction.channel.send(f'倒吊人（逆位）')
                await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\12_1.jpg'))
        if card == 13:
            if reverse == 0:
                await interaction.channel.send(f'死神')
                await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\13.jpg'))
            else:
                await interaction.channel.send(f'死神（逆位）')
                await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\13_1.jpg'))
        if card == 14:
            if reverse == 0:
                await interaction.channel.send(f'節制')
                await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\14.jpg'))
            else:
                await interaction.channel.send(f'節制（逆位）')
                await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\14_1.jpg'))
        if card == 15:
            if reverse == 0:
                await interaction.channel.send(f'惡魔')
                await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\15.jpg'))
            else:
                await interaction.channel.send(f'惡魔（逆位）')
                await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\15_1.jpg'))
        if card == 16:
            if reverse == 0:
                await interaction.channel.send(f'塔')
                await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\16.jpg'))
            else:
                await interaction.channel.send(f'塔（逆位）')
                await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\16_1.jpg'))
        if card == 17:
            if reverse == 0:
                await interaction.channel.send(f'星星')
                await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\17.jpg'))
            else:
                await interaction.channel.send(f'星星（逆位）')
                await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\17_1.jpg'))
        if card == 18:
            if reverse == 0:
                await interaction.channel.send(f'月亮')
                await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\18.jpg'))
            else:
                await interaction.channel.send(f'月亮（逆位）')
                await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\18_1.jpg'))
        if card == 19:
            if reverse == 0:
                await interaction.channel.send(f'太陽')
                await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\19.jpg'))
            else:
                await interaction.channel.send(f'太陽（逆位）')
                await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\19_1.jpg'))
        if card == 20:
            if reverse == 0:
                await interaction.channel.send(f'審判')
                await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\20.jpg'))
            else:
                await interaction.channel.send(f'審判（逆位）')
                await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\20_1.jpg'))
        if card == 21:
            if reverse == 0:
                await interaction.channel.send(f'世界')
                await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\21.jpg'))
            else:
                await interaction.channel.send(f'世界（逆位）')
                await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\21_1.jpg'))

    @discord.app_commands.command(name="majorarcana3" , description="根據訊息內容使用三張大密儀塔羅牌占卜")
    @discord.app_commands.describe(message="訊息")
    async def majorarcana3(self , interaction:discord.Interaction , message:str):
        random.seed(message)
        card1 = -1
        card2 = -1
        await interaction.response.send_message("占卜結果：")
        for i in range(3):

            if i == 0:
                await interaction.channel.send('過去：')
            elif i == 1:
                await interaction.channel.send('現在：')
            else:
                await interaction.channel.send('未來：')
            card = random.randrange(22)
            reverse = random.randrange(2)

            if ((card == card1) or (card == card2)):
                i-=1
                continue

            if card == 0:
                if i == 0:
                    card1 = 0
                if i == 1:
                    card2 = 0

                if reverse == 0:
                    await interaction.channel.send(f'愚者')
                    await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\0.jpg'))
                else:
                    await interaction.channel.send(f'愚者（逆位）')
                    await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\0_1.jpg'))
            if card == 1:
                if i == 0:
                    card1 = 1
                if i == 1:
                    card2 = 0

                if reverse == 1:
                    await interaction.channel.send(f'魔術師')
                    await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\1.jpg'))
                else:
                    await interaction.channel.send(f'魔術師（逆位）')
                    await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\1_1.jpg'))
            if card == 2:
                if i == 0:
                    card1 = 2
                if i == 1:
                    card2 = 2

                if reverse == 0:
                    await interaction.channel.send(f'女祭司')
                    await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\2.jpg'))
                else:
                    await interaction.channel.send(f'女祭司（逆位）')
                    await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\2_1.jpg'))
            if card == 3:
                if i == 0:
                    card1 = 3
                if i == 1:
                    card2 = 3

                if reverse == 0:
                    await interaction.channel.send(f'皇后')
                    await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\3.jpg'))
                else:
                    await interaction.channel.send(f'皇后（逆位）')
                    await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\3_1.jpg'))
            if card == 4:
                if i == 0:
                    card1 = 4
                if i == 1:
                    card2 = 4

                if reverse == 0:
                    await interaction.channel.send(f'皇帝')
                    await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\4.jpg'))
                else:
                    await interaction.channel.send(f'皇帝（逆位）')
                    await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\4_1.jpg'))
            if card == 5:
                if i == 0:
                    card1 = 5
                if i == 1:
                    card2 = 5

                if reverse == 0:
                    await interaction.channel.send(f'教皇')
                    await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\5.jpg'))
                else:
                    await interaction.channel.send(f'教皇（逆位）')
                    await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\5_1.jpg'))
            if card == 6:
                if i == 0:
                    card1 = 6
                if i == 1:
                    card2 = 6

                if reverse == 0:
                    await interaction.channel.send(f'戀人')
                    await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\6.jpg'))
                else:
                    await interaction.channel.send(f'戀人（逆位）')
                    await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\6_1.jpg'))
            if card == 7:
                if i == 0:
                    card1 = 7
                if i == 1:
                    card2 = 7

                if reverse == 0:
                    await interaction.channel.send(f'戰車')
                    await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\7.jpg'))
                else:
                    await interaction.channel.send(f'戰車（逆位）')
                    await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\7_1.jpg'))
            if card == 8:
                if i == 0:
                    card1 = 8
                if i == 1:
                    card2 = 8

                if reverse == 0:
                    await interaction.channel.send(f'力量')
                    await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\8.jpg'))
                else:
                    await interaction.channel.send(f'力量（逆位）')
                    await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\8_1.jpg'))
            if card == 9:
                if i == 0:
                    card1 = 9
                if i == 1:
                    card2 = 9

                if reverse == 0:
                    await interaction.channel.send(f'隱者')
                    await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\9.jpg'))
                else:
                    await interaction.channel.send(f'隱者（逆位）')
                    await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\9_1.jpg'))
            if card == 10:
                if i == 0:
                    card1 = 10
                if i == 1:
                    card2 = 10

                if reverse == 0:
                    await interaction.channel.send(f'命運之輪')
                    await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\10.jpg'))
                else:
                    await interaction.channel.send(f'命運之輪（逆位）')
                    await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\10_1.jpg'))
            if card == 11:
                if i == 0:
                    card1 = 11
                if i == 1:
                    card2 = 11

                if reverse == 0:
                    await interaction.channel.send(f'正義')
                    await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\11.jpg'))
                else:
                    await interaction.channel.send(f'正義（逆位）')
                    await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\11_1.jpg'))
            if card == 12:
                if i == 0:
                    card1 = 12
                if i == 1:
                    card2 = 12

                if reverse == 0:
                    await interaction.channel.send(f'倒吊人')
                    await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\12.jpg'))
                else:
                    await interaction.channel.send(f'倒吊人（逆位）')
                    await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\12_1.jpg'))
            if card == 13:
                if i == 0:
                    card1 = 13
                if i == 1:
                    card2 = 13

                if reverse == 0:
                    await interaction.channel.send(f'死神')
                    await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\13.jpg'))
                else:
                    await interaction.channel.send(f'死神（逆位）')
                    await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\13_1.jpg'))
            if card == 14:
                if i == 0:
                    card1 = 14
                if i == 1:
                    card2 = 14

                if reverse == 0:
                    await interaction.channel.send(f'節制')
                    await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\14.jpg'))
                else:
                    await interaction.channel.send(f'節制（逆位）')
                    await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\14_1.jpg'))
            if card == 15:
                if i == 0:
                    card1 = 15
                if i == 1:
                    card2 = 15

                if reverse == 0:
                    await interaction.channel.send(f'惡魔')
                    await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\15.jpg'))
                else:
                    await interaction.channel.send(f'惡魔（逆位）')
                    await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\15_1.jpg'))
            if card == 16:
                if i == 0:
                    card1 = 16
                if i == 1:
                    card2 = 16

                if reverse == 0:
                    await interaction.channel.send(f'塔')
                    await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\16.jpg'))
                else:
                    await interaction.channel.send(f'塔（逆位）')
                    await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\16_1.jpg'))
            if card == 17:
                if i == 0:
                    card1 = 17
                if i == 1:
                    card2 = 17

                if reverse == 0:
                    await interaction.channel.send(f'星星')
                    await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\17.jpg'))
                else:
                    await interaction.channel.send(f'星星（逆位）')
                    await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\17_1.jpg'))
            if card == 18:
                if i == 0:
                    card1 = 18
                if i == 1:
                    card2 = 18

                if reverse == 0:
                    await interaction.channel.send(f'月亮')
                    await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\18.jpg'))
                else:
                    await interaction.channel.send(f'月亮（逆位）')
                    await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\18_1.jpg'))
            if card == 19:
                if i == 0:
                    card1 = 19
                if i == 1:
                    card2 = 19

                if reverse == 0:
                    await interaction.channel.send(f'太陽')
                    await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\19.jpg'))
                else:
                    await interaction.channel.send(f'太陽（逆位）')
                    await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\19_1.jpg'))
            if card == 20:
                if i == 0:
                    card1 = 20
                if i == 1:
                    card2 = 20

                if reverse == 0:
                    await interaction.channel.send(f'審判')
                    await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\20.jpg'))
                else:
                    await interaction.channel.send(f'審判（逆位）')
                    await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\20_1.jpg'))
            if card == 21:
                if i == 0:
                    card1 = 21
                if i == 1:
                    card2 = 21

                if reverse == 0:
                    await interaction.channel.send(f'世界')
                    await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\21.jpg'))
                else:
                    await interaction.channel.send(f'世界（逆位）')
                    await interaction.channel.send(file=discord.File('.\\assets\\majorArcana\\21_1.jpg'))

async def setup(bot):
    await bot.add_cog(major_arcana(bot))