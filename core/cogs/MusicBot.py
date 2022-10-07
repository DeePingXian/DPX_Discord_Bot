import discord
from discord.ext import commands
import asyncio
from youtube_dl import YoutubeDL
import pytube
import requests
import gdown
from core.classes import Cog_Extension
import json
import os
import shutil
import uuid

with open('settings.json', 'r', encoding='utf8') as json_file:
    json_data = json.load(json_file)

AllMusicPlayingStatus = {}

class MusicCommands(Cog_Extension):

    class MusicPlayingStatus:

        class MusicDetail:
            def __init__(self , url):
                self.url = url
                self.title = None
                self.file_name = ''
                self.duration = None
                self.thumbnail_url = None
                self.audio_url = None
                self.file_size = None
                self.type = None

        def __init__(self , ctx , bot):
            self.ctx = ctx
            self.text_channel_id = ctx.channel.id
            self.music = None
            self.PlayNextMusic = asyncio.Event()
            self.playing = False
            self.SingleLoop = False
            self.DB = bot.get_cog('MySQL')
            self.DB.CreateDatabase(ctx.guild.id)
            self.DB.CreateMusicTable(ctx.guild.id)

        def InitMusic(self , url , type):
            self.tempMusic = self.MusicDetail(url)
            self.tempMusic.type = type

        async def GetYTMusicInfo(self):
            with YoutubeDL(json_data['ytdlopts']) as ytdl:
                info_dict = ytdl.extract_info(self.tempMusic.url, download=False)
                self.tempMusic.audio_url = info_dict['url']
                self.tempMusic.title = info_dict.get('title', None)
                dur = int(info_dict.get('duration', None))
                self.tempMusic.duration = f'{dur//3600}:{"%02d" % ((dur//60)%60)}:{"%02d" % (dur%60)}'
            self.tempMusic.thumbnail_url = pytube.YouTube(self.tempMusic.url).thumbnail_url

        async def renewYTMusicInfo(self):
            with YoutubeDL(json_data['ytdlopts']) as ytdl:
                info_dict = ytdl.extract_info(self.music.url, download=False)
                self.music.audio_url = info_dict['url']
                self.music.title = info_dict.get('title', None)
                dur = int(info_dict.get('duration', None))
                self.music.duration = f'{dur//3600}:{"%02d" % ((dur//60)%60)}:{"%02d" % (dur%60)}'
            self.music.thumbnail_url = pytube.YouTube(self.music.url).thumbnail_url

        async def GetGDMusicInfo(self):
            if not os.path.isdir('assets/MusicBot/MusicTemp'):
                os.mkdir('assets/MusicBot/MusicTemp')
            self.tempMusic.title = (((requests.get(self.tempMusic.url , stream=True , headers=json_data['GDHTTPHeader'])).text.partition('</title>'))[0]).partition('<title>')[2]
            self.tempMusic.title = self.tempMusic.title[:self.tempMusic.title.rfind(' -')]
            if self.tempMusic.title[self.tempMusic.title.rfind('.')+1:] in json_data['acceptableMusicContainer']:
                self.tempMusic.audio_url = (self.tempMusic.url.lstrip('https://drive.google.com/file/d/')).partition('/')[0]
                self.tempMusic.audio_url = (requests.get('https://drive.google.com/uc?export=open&confirm=yTib&id=' + self.tempMusic.audio_url , stream=True , headers=json_data['GDHTTPHeader'])).url
                self.tempMusic.file_size = int(requests.get(self.tempMusic.audio_url , stream=True , headers=json_data['GDHTTPHeader']).headers['Content-length'])
                if self.tempMusic.file_size <= json_data['googleDriveFileSizeLimitInMB'] * 1048576:
                    self.tempMusic.file_name = str(uuid.uuid4()) + self.tempMusic.title[self.tempMusic.title.rfind("."):]
                else:
                    self.tempMusic.title = f'檔案名稱「{self.tempMusic.title}」（{round(self.tempMusic.file_size/1048576 , 1)}MB）\n檔案大小大於上限{json_data["googleDriveFileSizeLimitInMB"]}MB，請壓縮後再播放（建議使用opus編碼）'
            else:
                self.tempMusic.title = f'檔案名稱「{self.tempMusic.title}」\n為避免程式不穩，將不播放未經驗證的檔案格式「{self.tempMusic.title[self.tempMusic.title.rfind("."):]}」'
            self.tempMusic.duration = 0
            self.tempMusic.thumbnail_url = json_data['googleDriveIcon']

        async def downloadGDMusic(self):
            if (self.music.file_name != '') and (not self.music.file_name in os.listdir('assets/MusicBot/MusicTemp')):
                gdown.download(id=(self.music.url.lstrip('https://drive.google.com/file/d/')).partition('/')[0], output='assets/MusicBot/MusicTemp/' + self.music.file_name, quiet=True)

        async def PutMusic(self):
            self.DB.PutMusic(self.ctx.guild.id , self.tempMusic)

        async def GetMusic(self):
            self.music = self.DB.GetMusic(self.ctx.guild.id)

        async def PopMusic(self):
            self.DB.PopMusic(self.ctx.guild.id)

        def GetMusicQueueLen(self):
            return self.DB.GetMusicQueueLen(self.ctx.guild.id)

        def GetMusicQueue(self):
            return self.DB.GetMusicQueue(self.ctx.guild.id)

        async def SetSingleLoop(self):
            self.DB.SetSingleLoop(self.ctx.guild.id , self.SingleLoop)

        async def GetLoop(self):
            self.SingleLoop = self.DB.GetLoop(self.ctx.guild.id)

        def CreateDatabase(self , GuildID):
            self.DB.CreateDatabase(self.ctx.guild.id)

        def CreateMusicTable(self , GuildID):
            self.DB.CreateMusicTable(self.ctx.guild.id)

        def CleanMusicTable(self):
            self.DB.CleanMusicTable(self.ctx.guild.id)

    @commands.command()
    async def play(self , ctx , url):
        if ctx.author.voice: # If the person is in a channel
            if url.startswith('https://youtube.com/') or url.startswith('https://www.youtube.com/') or url.startswith('https://youtu.be/') or url.startswith('https://m.youtube.com/'):         #處理 YouTube 影片
                try:
                    if '&playnext=' in url:
                        0/0
                    if url.startswith('https://youtube.com/'):
                        url = url.replace('https://youtube.com/' , 'https://www.youtube.com/')
                    elif url.startswith('https://m.youtube.com/'):
                        url = url.replace('https://m.youtube.com/' , 'https://www.youtube.com/')
                    elif url.startswith('https://youtu.be/'):
                        url = url.replace('https://youtu.be/' , 'https://www.youtube.com/watch?v=')
                    if url.startswith('https://www.youtube.com/shorts/'):
                        url = url.replace('https://www.youtube.com/shorts/' , 'https://www.youtube.com/watch?v=')
                    elif 'playlist?list=' in url:
                        pytube.Playlist(url)
                    else:
                        pytube.YouTube(url).check_availability()
                except:
                    await ctx.reply('此連結無法使用')
                else:
                    try:
                        if AllMusicPlayingStatus[ctx.guild.id].playing == False:        #找不到此項或=False則進except
                            0/0
                    except:
                        await self.JoinChannel(ctx)
                        AllMusicPlayingStatus[ctx.guild.id] = self.MusicPlayingStatus(ctx , self.bot)
                        AllMusicPlayingStatus[ctx.guild.id].playing = True
                        if 'playlist?list=' in url:
                            await self.add(ctx , url)
                        elif ('watch?v=' in url) and ('&list=' in url):
                            await self.add(ctx , url)
                        else:
                            if AllMusicPlayingStatus[ctx.guild.id].GetMusicQueueLen() < 51:
                                AllMusicPlayingStatus[ctx.guild.id].InitMusic(url , 1)
                                await AllMusicPlayingStatus[ctx.guild.id].GetYTMusicInfo()
                                await AllMusicPlayingStatus[ctx.guild.id].PutMusic()
                            else:
                                await ctx.send('播放隊列數量已達50上限')
                        await AllMusicPlayingStatus[ctx.guild.id].GetMusic()
                        self.bot.loop.create_task(self.AudioPlayerTask(ctx))
                    else:
                        await self.JoinChannel(ctx)
                        await self.add(ctx , url)
            elif url.startswith('https://drive.google.com/file/d/'):         #處理 Google 雲端音樂檔案
                try:
                    if AllMusicPlayingStatus[ctx.guild.id].playing == False:        #找不到此項或=False則進except
                        0/0
                except:
                    await self.JoinChannel(ctx)
                    AllMusicPlayingStatus[ctx.guild.id] = self.MusicPlayingStatus(ctx , self.bot)
                    AllMusicPlayingStatus[ctx.guild.id].playing = True
                    if AllMusicPlayingStatus[ctx.guild.id].GetMusicQueueLen() < 51:
                        AllMusicPlayingStatus[ctx.guild.id].InitMusic(url , 2)
                        await AllMusicPlayingStatus[ctx.guild.id].GetGDMusicInfo()
                        await AllMusicPlayingStatus[ctx.guild.id].PutMusic()
                    else:
                        await ctx.send('播放隊列數量已達50上限')
                    await AllMusicPlayingStatus[ctx.guild.id].GetMusic()
                    self.bot.loop.create_task(self.AudioPlayerTask(ctx))
                else:
                    await self.JoinChannel(ctx)
                    await self.add(ctx , url)
        else:
            await ctx.reply('請先進入頻道')

    @commands.command()
    async def playlocal(self , ctx , * , path=None):
        if ctx.author.id == json_data['adminID']:
            if ctx.author.voice: # If the person is in a channel
                try:
                    if AllMusicPlayingStatus[ctx.guild.id].playing == False:        #找不到此項或=False則進except
                        0/0
                except:
                    if os.path.isfile(path):
                        await self.JoinChannel(ctx)
                        AllMusicPlayingStatus[ctx.guild.id] = self.MusicPlayingStatus(ctx , self.bot)
                        AllMusicPlayingStatus[ctx.guild.id].playing = True
                        if AllMusicPlayingStatus[ctx.guild.id].GetMusicQueueLen() < 51:
                            AllMusicPlayingStatus[ctx.guild.id].InitMusic('' , 0)
                            AllMusicPlayingStatus[ctx.guild.id].tempMusic.title = os.path.basename(path)
                            AllMusicPlayingStatus[ctx.guild.id].tempMusic.audio_url = path
                            AllMusicPlayingStatus[ctx.guild.id].tempMusic.thumbnail_url = json_data['localMusicIcon']
                            await AllMusicPlayingStatus[ctx.guild.id].PutMusic()
                        else:
                            await ctx.send('播放隊列數量已達50上限')
                        await AllMusicPlayingStatus[ctx.guild.id].GetMusic()
                        self.bot.loop.create_task(self.AudioPlayerTask(ctx))
                    else:
                        await ctx.reply('找不到此檔案')
                else:
                    await self.JoinChannel(ctx)
                    await self.addlocal(ctx , path)
            else:
                await ctx.reply('請先進入頻道')
        else:
            await ctx.reply('此功能僅限開此bot的管理員使用')

    @commands.command()
    async def add(self , ctx , url):
        if ctx.voice_client: # If the commands is in a voice channel:
            try:
                if ctx.voice_client.channel != ctx.message.author.voice.channel:        #確認用戶在頻道在頻道裡
                    0/0
            except:
                await ctx.reply('請先進入頻道')
            else:
                try:
                    if AllMusicPlayingStatus[ctx.guild.id].playing == False:        #找不到此項或=False則進except
                        0/0
                except:
                    await ctx.reply('請先播放音樂')
                else:
                    if url.startswith('https://youtube.com/') or url.startswith('https://www.youtube.com/') or url.startswith('https://youtu.be/') or url.startswith('https://m.youtube.com/'):         #處理 YouTube 影片
                        try:
                            if '&playnext=' in url:
                                0/0
                            if url.startswith('https://youtube.com/'):
                                url = url.replace('https://youtube.com/' , 'https://www.youtube.com/')
                            elif url.startswith('https://m.youtube.com/'):
                                url = url.replace('https://m.youtube.com/' , 'https://www.youtube.com/')
                            elif url.startswith('https://youtu.be/'):
                                url = url.replace('https://youtu.be/' , 'https://www.youtube.com/watch?v=')
                            if url.startswith('https://www.youtube.com/shorts/'):
                                url = url.replace('https://www.youtube.com/shorts/' , 'https://www.youtube.com/watch?v=')
                            if 'playlist?list=' in url:
                                pytube.Playlist(url)
                            else:
                                pytube.YouTube(url).check_availability()
                        except:
                            await ctx.reply('此連結無法使用')
                        else:
                            if 'playlist?list=' in url:
                                MusicPlaylist = pytube.Playlist(url)
                                VideoNames = str()
                                times = 0
                                for i in MusicPlaylist.video_urls:
                                    if AllMusicPlayingStatus[ctx.guild.id].GetMusicQueueLen() >= 51:
                                        await ctx.send('播放隊列數量已達50上限')
                                        break
                                    times += 1
                                    AllMusicPlayingStatus[ctx.guild.id].InitMusic(i , 1)
                                    await AllMusicPlayingStatus[ctx.guild.id].GetYTMusicInfo()
                                    await AllMusicPlayingStatus[ctx.guild.id].PutMusic()
                                    music = AllMusicPlayingStatus[ctx.guild.id].tempMusic
                                    if times <= 10:
                                        VideoNames += f'{"%02d" % (times)}. {music.title} {music.duration}\n'
                                if times > 10:
                                    VideoNames += f'\n...後面還有{times-10}首'
                                if VideoNames != '':
                                    embed = discord.Embed(title='已加入隊列', description=discord.Embed.Empty , color=0x00ffff)
                                    embed.add_field(name='\u200b', value=VideoNames , inline=False)
                                    await ctx.channel.send(embed=embed)
                            elif ('watch?v=' in url) and ('&list=' in url):
                                VideoId = pytube.extract.video_id(url)
                                MusicPlaylist = pytube.Playlist(url)
                                VideoNames = str()
                                GetVideo = False
                                times = 0
                                for i in MusicPlaylist.video_urls:
                                    if AllMusicPlayingStatus[ctx.guild.id].GetMusicQueueLen() >= 51:
                                        await ctx.send('播放隊列數量已達50上限')
                                        break
                                    if VideoId in i:
                                        GetVideo = True
                                    if GetVideo:
                                        times += 1
                                        AllMusicPlayingStatus[ctx.guild.id].InitMusic(i , 1)
                                        await AllMusicPlayingStatus[ctx.guild.id].GetYTMusicInfo()
                                        await AllMusicPlayingStatus[ctx.guild.id].PutMusic()
                                        music = AllMusicPlayingStatus[ctx.guild.id].tempMusic
                                        if times <= 10:
                                            VideoNames += f'{"%02d" % (times)}. {music.title} {music.duration}\n'
                                if times > 10:
                                    VideoNames += f'\n...後面還有{times-10}首\n\n更多資訊請至 bot 附屬網頁瀏覽'
                                if VideoNames != '':
                                    embed = discord.Embed(title='已加入隊列', description=discord.Embed.Empty , color=0x00ffff)
                                    embed.add_field(name='\u200b', value=VideoNames , inline=False)
                                    await ctx.channel.send(embed=embed)
                            else:
                                if AllMusicPlayingStatus[ctx.guild.id].GetMusicQueueLen() < 51:
                                    AllMusicPlayingStatus[ctx.guild.id].InitMusic(url , 1)
                                    await AllMusicPlayingStatus[ctx.guild.id].GetYTMusicInfo()
                                    await AllMusicPlayingStatus[ctx.guild.id].PutMusic()
                                    music = AllMusicPlayingStatus[ctx.guild.id].tempMusic
                                    embed = discord.Embed(title=music.title, description=f'長度：{music.duration}' , color=0x00ffff)
                                    embed.set_author(name="已加入隊列" , url=discord.Embed.Empty , icon_url=discord.Embed.Empty)
                                    await ctx.channel.send(embed=embed)
                                else:
                                    await ctx.send('播放隊列數量已達50上限')
                    elif url.startswith('https://drive.google.com/file/d/'):         #處理 Google 雲端音樂檔案
                        if AllMusicPlayingStatus[ctx.guild.id].GetMusicQueueLen() < 51:
                            AllMusicPlayingStatus[ctx.guild.id].InitMusic(url , 2)
                            await AllMusicPlayingStatus[ctx.guild.id].GetGDMusicInfo()
                            await AllMusicPlayingStatus[ctx.guild.id].PutMusic()
                            music = AllMusicPlayingStatus[ctx.guild.id].tempMusic
                            embed = discord.Embed(title=music.title, description='來自 Google 雲端硬碟' , color=0x00ffff)
                            embed.set_author(name="已加入隊列" , url=discord.Embed.Empty , icon_url=discord.Embed.Empty)
                            await ctx.channel.send(embed=embed)
                        else:
                            await ctx.send('播放隊列數量已達50上限')
        else:
            await ctx.reply('未處於任一語音頻道內')

    @commands.command()
    async def addlocal(self , ctx , *path_):
        path = ''
        if path_:
            for i in range(len(path_)):
                path+=path_[i]
                if i != len(path_):
                    path += ' '
        del path_
        if ctx.author.id == json_data['adminID']:
            if ctx.voice_client: # If the commands is in a voice channel:
                try:
                    if ctx.voice_client.channel != ctx.message.author.voice.channel:        #確認用戶在頻道在頻道裡
                        0/0
                except:
                    await ctx.reply('請先進入頻道')
                else:
                    try:
                        if AllMusicPlayingStatus[ctx.guild.id].playing == False:        #找不到此項或=False則進except
                            0/0
                    except:
                        await ctx.reply('請先播放音樂')
                    else:
                        if os.path.isfile(path):
                            if AllMusicPlayingStatus[ctx.guild.id].GetMusicQueueLen() < 51:
                                AllMusicPlayingStatus[ctx.guild.id].InitMusic('' , 0)
                                AllMusicPlayingStatus[ctx.guild.id].tempMusic.title = os.path.basename(path)
                                AllMusicPlayingStatus[ctx.guild.id].tempMusic.audio_url = path
                                AllMusicPlayingStatus[ctx.guild.id].tempMusic.thumbnail_url = json_data['localMusicIcon']
                                await AllMusicPlayingStatus[ctx.guild.id].PutMusic()
                                music = AllMusicPlayingStatus[ctx.guild.id].tempMusic
                                embed = discord.Embed(title='本機音樂', description=music.title , color=0x00ffff)
                                embed.set_author(name="已加入隊列" , url=discord.Embed.Empty , icon_url=discord.Embed.Empty)
                                await ctx.channel.send(embed=embed)
                            else:
                                await ctx.send('播放隊列數量已達50上限')
                        else:
                            await ctx.reply('找不到此檔案')
            else:
                await ctx.reply('未處於任一語音頻道內')
        else:
            await ctx.reply('此功能僅限開此bot的管理員使用')

    @commands.command()
    async def pause(self , ctx):
        if ctx.voice_client: # If the commands is in a voice channel
            try:
                if ctx.voice_client.channel != ctx.message.author.voice.channel:        #確認用戶在頻道在頻道裡
                    0/0
                else:
                    try:
                        if not AllMusicPlayingStatus[ctx.guild.id].playing:
                            0/0
                        else:
                            if ctx.voice_client.is_playing():
                                embed = discord.Embed(title='已暫停播放', description=AllMusicPlayingStatus[ctx.guild.id].music.title , color=0xffff00)
                                await ctx.channel.send(embed=embed)
                                ctx.voice_client.pause()
                            else:
                                await ctx.reply('未播放音樂')
                    except:
                        await ctx.reply('未播放音樂')
            except:
                await ctx.reply('請先進入頻道')
        else:
            await ctx.reply('未處於任一語音頻道內')

    @commands.command()
    async def resume(self , ctx):
        if ctx.voice_client: # If the commands is in a voice channel
            try:
                if ctx.voice_client.channel != ctx.message.author.voice.channel:        #確認用戶在頻道在頻道裡
                    0/0
                else:
                    try:
                        if not AllMusicPlayingStatus[ctx.guild.id].playing:
                            0/0
                        else:
                            if ctx.voice_client.is_paused():
                                embed = discord.Embed(title='已恢復播放', description=AllMusicPlayingStatus[ctx.guild.id].music.title , color=0x00ff00)
                                await ctx.channel.send(embed=embed)
                                ctx.voice_client.resume()
                            else:
                                await ctx.reply('未暫停播放')
                    except:
                        await ctx.reply('未播放音樂')
            except:
                await ctx.reply('請先進入頻道')
        else:
            await ctx.reply('未處於任一語音頻道內')

    @commands.command()
    async def skip(self , ctx):
        if ctx.voice_client: # If the commands is in a voice channel
            try:
                if ctx.voice_client.channel != ctx.message.author.voice.channel:        #確認用戶在頻道在頻道裡
                    0/0
                else:
                    if AllMusicPlayingStatus[ctx.guild.id].GetMusicQueueLen() == 1:
                        embed = discord.Embed(title='已停止播放', description=discord.Embed.Empty , color=0xff0000)
                        await ctx.send(embed=embed)
                        await self.LeaveChannel(ctx)
                    else:
                        AllMusicPlayingStatus[ctx.guild.id].SingleLoop = False
                        await AllMusicPlayingStatus[ctx.guild.id].SetSingleLoop()
                        embed = discord.Embed(title='已跳過', description=AllMusicPlayingStatus[ctx.guild.id].music.title , color=0x00ffff)
                        await ctx.channel.send(embed=embed , delete_after=10)
                        ctx.voice_client.stop()
            except:
                await ctx.reply('請先進入頻道')
        else:
            await ctx.reply('未處於任一語音頻道內')

    @commands.command()
    async def loop(self , ctx):
        if ctx.voice_client: # If the commands is in a voice channel
            try:
                if ctx.voice_client.channel != ctx.message.author.voice.channel:        #確認用戶在頻道在頻道裡
                    0/0
            except:
                await ctx.reply('請先進入頻道')
            else:
                try:
                    if AllMusicPlayingStatus[ctx.guild.id].playing == False:
                        0/0
                    else:
                        await AllMusicPlayingStatus[ctx.guild.id].GetLoop()
                        if AllMusicPlayingStatus[ctx.guild.id].SingleLoop == False:
                            AllMusicPlayingStatus[ctx.guild.id].SingleLoop = True
                            embed = discord.Embed(title='已啟用單曲重複播放', description=AllMusicPlayingStatus[ctx.guild.id].music.title , color=0x00ff00)
                            await ctx.send(embed=embed)
                        else:
                            AllMusicPlayingStatus[ctx.guild.id].SingleLoop = False
                            embed = discord.Embed(title='已停用單曲重複播放', description=AllMusicPlayingStatus[ctx.guild.id].music.title , color=0x00ff00)
                            await ctx.send(embed=embed)
                        await AllMusicPlayingStatus[ctx.guild.id].SetSingleLoop()
                except:
                    await ctx.reply('未播放')
        else:
            await ctx.reply('未處於任一語音頻道內')

    @commands.command()
    async def stop(self , ctx):
        if ctx.voice_client: # If the commands is in a voice channel
            try:
                if ctx.voice_client.channel != ctx.message.author.voice.channel:        #確認用戶在頻道在頻道裡
                    0/0
                else:
                    embed = discord.Embed(title='已停止播放', description=discord.Embed.Empty , color=0xff0000)
                    await ctx.send(embed=embed , delete_after=10)
                    await self.LeaveChannel(ctx)
            except:
                await ctx.reply('請先進入頻道')
        else:
            await ctx.reply('未處於任一語音頻道內')

    @commands.command()
    async def join(self , ctx):
        if ctx.author.voice: # If the person is in a channel
            await self.JoinChannel(ctx)
        else:
            await ctx.reply('請先進入頻道')

    @commands.command()
    async def nowplaying(self , ctx):
        try:
            if AllMusicPlayingStatus[ctx.guild.id].playing == False:
                0/0
            else:
                music = AllMusicPlayingStatus[ctx.guild.id].music
                if music.type == 0:
                    embed = discord.Embed(title=music.title, description='本機音樂' , color=0x00ff00)
                elif music.type == 1:
                    embed = discord.Embed(title=music.title, description=f'長度：{music.duration}' , color=0x00ff00)
                elif music.type == 2:
                    embed = discord.Embed(title=music.title, description='來自 Google 雲端硬碟' , color=0x00ff00)
                embed.set_author(name="現正播放" , url=discord.Embed.Empty , icon_url=discord.Embed.Empty)
                embed.set_thumbnail(url=music.thumbnail_url) 
                await ctx.channel.send(embed=embed , delete_after=10)
        except:
            await ctx.send('未播放')

    @commands.command()
    async def queue(self , ctx):
        try:
            if AllMusicPlayingStatus[ctx.guild.id].GetMusicQueueLen() == 0:      #這是舊的程式碼 應該不會觸發
                0/0
        except:
            await ctx.send('無音樂待播放')
        else:
            queue = AllMusicPlayingStatus[ctx.guild.id].GetMusicQueue()
            embed = discord.Embed(title="音樂隊列", description=discord.Embed.Empty , color=0x00ffff)
            if queue[0][8] == 0:
                MusicNames = f'現正播放：\n（本機音樂）{queue[0][1]}\n\n'
            elif queue[0][8] == 1:
                MusicNames = f'現正播放：\n（YouTube）{queue[0][1]} {queue[0][3]}\n\n'
            elif queue[0][8] == 2:
                MusicNames = f'現正播放：\n（Google Drive）{queue[0][1]}\n\n'
            if len(queue) >= 2:
                MusicNames += f'音樂隊列：\n'
            for i in range(1 , len(queue)):
                if queue[i][8] == 0:
                    MusicNames += f'{"%02d" % (i)}.（本機音樂）{queue[i][1]}\n'
                elif queue[i][8] == 1:
                    MusicNames += f'{"%02d" % (i)}.（YouTube）{queue[i][1]} {queue[i][3]}\n'
                elif queue[i][8] == 2:
                    MusicNames += f'{"%02d" % (i)}.（Google Drive）{queue[i][1]}\n'
                if i == 10:
                    if len(queue) > 11:
                        MusicNames += f'\n...後面還有{len(queue)-11}首'
                    break
            embed.add_field(name='\u200b', value=MusicNames , inline=False)
            await ctx.channel.send(embed=embed)

    async def AudioPlayerTask(self , ctx):
        while True:
            AllMusicPlayingStatus[ctx.guild.id].PlayNextMusic.clear()
            if not AllMusicPlayingStatus[ctx.guild.id].SingleLoop:
                if AllMusicPlayingStatus[ctx.guild.id].music.type == 2:
                    if os.path.isfile('assets/MusicBot/MusicTemp/' + AllMusicPlayingStatus[ctx.guild.id].music.file_name):
                        os.remove('assets/MusicBot/MusicTemp/' + AllMusicPlayingStatus[ctx.guild.id].music.file_name)
                await AllMusicPlayingStatus[ctx.guild.id].GetMusic()
                if AllMusicPlayingStatus[ctx.guild.id].music == None:
                    await self.LeaveChannel(ctx)
                    break
            try:
                if AllMusicPlayingStatus[ctx.guild.id].music.type == 0:
                    music = AllMusicPlayingStatus[ctx.guild.id].music
                    if os.path.isfile(music.audio_url):
                        ctx.voice_client.play(discord.FFmpegOpusAudio(executable = 'assets/MusicBot/ffmpeg.exe' , bitrate = json_data['MusicBotOpts']['bitrate'] , source = music.audio_url , before_options=json_data['ffmpegopts']['before_options'] , options=json_data['ffmpegopts']['options']) , after = lambda _: self.TogglePlayNextMusic(ctx))
                        embed = discord.Embed(title=music.title, description='本機音樂' , color=0x00ff00)
                    else:
                        embed = discord.Embed(title=music.title, description='未找到檔案 將跳過' , color=0x00ff00)
                elif AllMusicPlayingStatus[ctx.guild.id].music.type == 1:
                    await AllMusicPlayingStatus[ctx.guild.id].renewYTMusicInfo()
                    music = AllMusicPlayingStatus[ctx.guild.id].music
                    ctx.voice_client.play(discord.FFmpegOpusAudio(executable = 'assets/MusicBot/ffmpeg.exe' , bitrate = json_data['MusicBotOpts']['bitrate'] , source = music.audio_url , before_options=json_data['ffmpegopts']['before_options'] , options=json_data['ffmpegopts']['options']) , after = lambda _: self.TogglePlayNextMusic(ctx))
                    embed = discord.Embed(title=music.title, description=f'長度：{music.duration}' , color=0x00ff00)
                elif AllMusicPlayingStatus[ctx.guild.id].music.type == 2:
                    music = AllMusicPlayingStatus[ctx.guild.id].music
                    await AllMusicPlayingStatus[ctx.guild.id].downloadGDMusic()
                    ctx.voice_client.play(discord.FFmpegOpusAudio(executable = 'assets/MusicBot/ffmpeg.exe' , bitrate = json_data['MusicBotOpts']['bitrate'] , source = 'assets/MusicBot/MusicTemp/' + music.file_name , before_options=json_data['ffmpegopts']['before_options'] , options=json_data['ffmpegopts']['options']) , after = lambda _: self.TogglePlayNextMusic(ctx))
                    embed = discord.Embed(title=music.title, description='來自 Google 雲端硬碟' , color=0x00ff00)
                embed.set_author(name="現正播放" , url=discord.Embed.Empty , icon_url=discord.Embed.Empty)
                embed.set_thumbnail(url=music.thumbnail_url)
                await ctx.channel.send(embed=embed , delete_after=10)
                await AllMusicPlayingStatus[ctx.guild.id].PlayNextMusic.wait()
                if not AllMusicPlayingStatus[ctx.guild.id].SingleLoop:
                    await AllMusicPlayingStatus[ctx.guild.id].PopMusic()
            except:
                self.TogglePlayNextMusic(ctx)

    def TogglePlayNextMusic(self , ctx):
        try:
            AllMusicPlayingStatus[ctx.guild.id].PlayNextMusic.set()
        except:
            pass

    async def JoinChannel(self , ctx):
        if ctx.author.voice: # If the person is in a channel
            if ctx.voice_client:
                if ctx.voice_client.channel != ctx.author.voice.channel:
                    await ctx.voice_client.move_to(ctx.author.voice.channel)
            else:
                await ctx.author.voice.channel.connect()
                await ctx.guild.change_voice_state(channel=ctx.author.voice.channel, self_mute=False, self_deaf=True)
        else:
            await ctx.reply('請先進入頻道')

    async def LeaveChannel(self , ctx):
        try:
            if AllMusicPlayingStatus[ctx.guild.id].playing == False:
                0/0
        except:                                  
            await ctx.voice_client.disconnect()
        else:
            try:
                await ctx.voice_client.disconnect()
                AllMusicPlayingStatus[ctx.guild.id].CleanMusicTable()
                del AllMusicPlayingStatus[ctx.guild.id]
            except:      #通常是AttributeError
                pass
        if os.path.isdir('assets/MusicBot/MusicTemp'):
            shutil.rmtree('assets/MusicBot/MusicTemp' , ignore_errors = False)

def setup(bot):
    bot.add_cog(MusicCommands(bot))