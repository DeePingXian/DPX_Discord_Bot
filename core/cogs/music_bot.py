import discord
from discord.ext import commands
from yt_dlp import YoutubeDL
import os , shutil , asyncio , requests , gdown , uuid
from core.classes import Cog_Extension

class music_bot(Cog_Extension):

    def __init__(self , bot):
        super().__init__(bot)
        self.allMusicPlayingStatus = {}

    class musicPlayingStatus:

        class musicDetail:
            def __init__(self , type):
                self.url = ''
                self.title = ''
                self.file_name = ''
                self.duration = 0
                self.thumbnail_url = ''
                self.audio_url = ''
                self.file_size = 0
                self.type = type

        def __init__(self , ctx , settings , DB):
            self.ctx = ctx
            self.music = None
            self.tempMusic = None
            self.tempMusicDict = {}
            self.PlayNextMusic = asyncio.Event()
            self.playing = False
            self.SingleLoop = False
            self.DB = DB
            self.CreateDatabase()
            self.CreateMusicTable()
            self.settings = settings
            self.ytdlOpts = {"format": "bestaudio/best" , "extract_flat": False , "skip_download": True , "nocheckcertificate": True , "ignoreerrors": True , "logtostderr": False , "quiet": True , "no_warnings": True , "default_search": "auto" , "source_address": "0.0.0.0"}
            self.ytdlOpts2 = {"format": "bestaudio/best" , "extract_flat": "in_playlist" , "skip_download": True , "nocheckcertificate": True , "ignoreerrors": True , "logtostderr": False , "quiet": True , "no_warnings": True , "default_search": "auto" , "source_address": "0.0.0.0"}

        def initTempMusic(self , sum , type):
            for i in range(1 , sum + 1):
                self.tempMusicDict[i] = self.musicDetail(type)

        async def getYTMusicInfo(self , num , url):
            self.tempMusicDict[num].url = url
            with YoutubeDL(self.ytdlOpts) as ytdl:
                infoDict = await asyncio.to_thread(ytdl.extract_info , url , download=False)
                self.tempMusicDict[num].audio_url = infoDict['url']
                self.tempMusicDict[num].title = infoDict.get('title' , '') if not infoDict.get('is_live' , None) else infoDict.get('title' , None)[:-16]
                self.tempMusicDict[num].file_name = 'live' if infoDict.get('is_live' , None) else ''        #用這欄儲存是否為直播
                dur = int(infoDict.get('duration' , 0))
                self.tempMusicDict[num].duration = f'{dur//3600}:{"%02d" % ((dur//60)%60)}:{"%02d" % (dur%60)}'
                self.tempMusicDict[num].thumbnail_url = infoDict.get('thumbnail' , None)

        async def getYTPlaylistEachUrl(self , url):
            with YoutubeDL(self.ytdlOpts2) as ytdl:
                infoDict = await asyncio.to_thread(ytdl.extract_info , url , download=False)
            list = []
            for i in infoDict['entries']:
                if i:       #處理如果是None的部分
                    list.append((i['url'] , True if i.get('channel_id' , None) else False))        #(url , 是否為有效連結)
                else:
                    list.append(('（無法處理的影片）' , False))
            return list

        async def renewYTMusicInfo(self):
            with YoutubeDL(self.ytdlOpts) as ytdl:
                infoDict = await asyncio.to_thread(ytdl.extract_info , self.music.url , download=False)
                self.music.audio_url = infoDict['url']
                self.music.title = infoDict.get('title' , '') if not infoDict.get('is_live' , None) else infoDict.get('title' , None)[:-16]
                self.music.file_name = 'live' if infoDict.get('is_live' , None) else ''        #用這欄儲存是否為直播
                dur = int(infoDict.get('duration' , 0))
                self.music.duration = f'{dur//3600}:{"%02d" % ((dur//60)%60)}:{"%02d" % (dur%60)}'
                self.music.thumbnail_url = infoDict.get('thumbnail' , None)

        async def getGDMusicInfo(self , num , url):
            if not os.path.isdir('assets/musicBot/musicTemp'):
                os.mkdir('assets/musicBot/musicTemp')
            self.tempMusicDict[num].url = url
            self.tempMusicDict[num].title = (((await asyncio.to_thread(requests.get , url , stream=True , headers=self.settings['musicBotOpts']['googleDrive']['HTTPHeader'])).text.partition('</title>'))[0]).partition('<title>')[2]
            self.tempMusicDict[num].title = self.tempMusicDict[num].title[:self.tempMusicDict[num].title.rfind(' -')]
            if self.tempMusicDict[num].title[self.tempMusicDict[num].title.rfind('.')+1:] in self.settings['musicBotOpts']['googleDrive']['acceptableMusicContainer']:
                self.tempMusicDict[num].audio_url = (self.tempMusicDict[num].url.lstrip('https://drive.google.com/file/d/')).partition('/')[0]
                self.tempMusicDict[num].audio_url = (await asyncio.to_thread(requests.get , 'https://drive.google.com/uc?export=open&confirm=yTib&id=' + self.tempMusicDict[num].audio_url , stream=True , headers=self.settings['musicBotOpts']['googleDrive']['HTTPHeader'])).url
                self.tempMusicDict[num].file_size = int((await asyncio.to_thread(requests.get , self.tempMusicDict[num].audio_url , stream=True , headers=self.settings['musicBotOpts']['googleDrive']['HTTPHeader'])).headers['Content-length'])
                if self.tempMusicDict[num].file_size <= self.settings['musicBotOpts']['googleDrive']['fileSizeLimitInMB'] * 1048576:
                    self.tempMusicDict[num].file_name = str(uuid.uuid4()) + self.tempMusicDict[num].title[self.tempMusicDict[num].title.rfind("."):]
                else:
                    self.tempMusicDict[num].title = f'檔案名稱「{self.tempMusicDict[num].title}」（{round(self.tempMusicDict[num].file_size/1048576 , 1)}MB）\n檔案大小大於上限{self.settings["musicBotOpts"]["googleDrive"]["fileSizeLimitInMB"]}MB，請壓縮後再播放（建議使用opus編碼）'
            else:
                self.tempMusicDict[num].title = f'檔案名稱「{self.tempMusicDict[num].title}」\n為避免程式不穩，將不播放未經驗證的檔案格式「{self.tempMusicDict[num].title[self.tempMusic.title.rfind("."):]}」'
            self.tempMusicDict[num].duration = 0
            self.tempMusicDict[num].thumbnail_url = self.settings['musicBotOpts']['googleDrive']['icon']

        async def downloadGDMusic(self):
            if (self.music.file_name != '') and (not self.music.file_name in os.listdir('assets/musicBot/musicTemp')):
                await asyncio.to_thread(gdown.download , id=(self.music.url.lstrip('https://drive.google.com/file/d/')).partition('/')[0] , output='assets/musicBot/musicTemp/' + self.music.file_name , quiet=True)

        async def getBiliMusicInfo(self , num , url):
            self.tempMusicDict[num].url = url
            with YoutubeDL(self.ytdlOpts) as ytdl:
                infoDict = await asyncio.to_thread(ytdl.extract_info , url , download=False)
                self.tempMusicDict[num].title = infoDict.get('title' , '')
                dur = int(infoDict.get('duration' , 0))
                self.tempMusicDict[num].duration = f'{dur//3600}:{"%02d" % ((dur//60)%60)}:{"%02d" % (dur%60)}'
                self.tempMusicDict[num].thumbnail_url = infoDict.get('thumbnail' , None)

        async def getBiliPlaylistEachUrl(self , url):
            with YoutubeDL(self.ytdlOpts2) as ytdl:
                infoDict = await asyncio.to_thread(ytdl.extract_info , url , download=False)
            list = []
            for i in infoDict['entries']:
                list.append((i['url'] , True if i.get('id' , None) else None))        #(url , 是否為有效連結)  偵測是否為有效連結的方法是猜的 不確定
            return list

        async def renewBiliMusicInfo(self):
            with YoutubeDL(self.ytdlOpts) as ytdl:
                infoDict = await asyncio.to_thread(ytdl.extract_info , self.music.url , download=False)
                while not infoDict['url'].startswith('https://upos-hz-mirrorakam.akamaized.net/'):     #只有這個來源的能正常播放
                    await asyncio.sleep(2)      #避免頻繁request被鎖
                    infoDict = await asyncio.to_thread(ytdl.extract_info , self.music.url , download=False)
                self.music.audio_url = infoDict['url']
                self.music.title = infoDict.get('title' , '')
                dur = int(infoDict.get('duration' , 0))
                self.music.duration = f'{dur//3600}:{"%02d" % ((dur//60)%60)}:{"%02d" % (dur%60)}'
                self.music.thumbnail_url = infoDict.get('thumbnail' , None)

        async def PutMusic(self):
            def aPutMusic(self):
                for i in range(1 , len(self.tempMusicDict) + 1):
                    if self.tempMusicDict.get(i , None):        #單純避免空號
                        self.DB.PutMusic(self.ctx.guild.id , self.tempMusicDict.pop(i))
            await asyncio.to_thread(aPutMusic , self)

        async def GetMusic(self):
            self.music = await asyncio.to_thread(self.DB.GetMusic , self.ctx.guild.id)

        async def PopMusic(self):
            await asyncio.to_thread(self.DB.PopMusic , self.ctx.guild.id)

        async def GetMusicQueueLen(self):
            return await asyncio.to_thread(self.DB.GetMusicQueueLen , self.ctx.guild.id)

        async def GetMusicQueue(self):
            return await asyncio.to_thread(self.DB.GetMusicQueue , self.ctx.guild.id)

        async def SetSingleLoop(self):
            await asyncio.to_thread(self.DB.SetSingleLoop , self.ctx.guild.id , self.SingleLoop)

        async def GetLoop(self):
            self.SingleLoop = await asyncio.to_thread(self.DB.GetLoop , self.ctx.guild.id)

        def CreateDatabase(self):
            self.DB.CreateDatabase(self.ctx.guild.id)

        def CreateMusicTable(self):
            self.DB.CreateMusicTable(self.ctx.guild.id)

        def CleanMusicTable(self):
            self.DB.CleanMusicTable(self.ctx.guild.id)

    @commands.command()
    async def play(self , ctx , url):
        if ctx.author.voice:        #確認用戶在語音頻道裡
            if url.startswith('https://youtube.com/') or url.startswith('https://www.youtube.com/') or url.startswith('https://youtu.be/') or url.startswith('https://m.youtube.com/'):         #處理 YouTube 影片
                try:
                    if url.startswith('https://youtube.com/'):
                        url = url.replace('https://youtube.com/' , 'https://www.youtube.com/')
                    elif url.startswith('https://m.youtube.com/'):
                        url = url.replace('https://m.youtube.com/' , 'https://www.youtube.com/')
                    elif url.startswith('https://youtu.be/'):
                        url = url.replace('https://youtu.be/' , 'https://www.youtube.com/watch?v=')
                    if url.startswith('https://www.youtube.com/shorts/'):
                        url = url.replace('https://www.youtube.com/shorts/' , 'https://www.youtube.com/watch?v=')
                except:
                    await ctx.reply('此連結無法播放')
                else:
                    try:
                        if self.allMusicPlayingStatus[ctx.guild.id].playing == False:        #找不到此項或=False則進except
                            0/0
                    except:
                        await self.JoinChannel(ctx)
                        self.allMusicPlayingStatus[ctx.guild.id] = self.musicPlayingStatus(ctx , self.settings , self.bot.get_cog('MySQL'))
                        self.allMusicPlayingStatus[ctx.guild.id].playing = True
                        if 'playlist?list=' in url:
                            await self.add(ctx , url)
                        elif ('watch?v=' in url) and ('&list=' in url):
                            await self.add(ctx , url)
                        else:
                            self.allMusicPlayingStatus[ctx.guild.id].initTempMusic(1 , 1)
                            try:
                                await self.allMusicPlayingStatus[ctx.guild.id].getYTMusicInfo(1 , url)
                            except:
                                await ctx.reply('此連結無法播放')
                            else:
                                await self.allMusicPlayingStatus[ctx.guild.id].PutMusic()
                        await self.allMusicPlayingStatus[ctx.guild.id].GetMusic()
                        self.bot.loop.create_task(self.AudioPlayerTask(ctx))
                    else:
                        await self.JoinChannel(ctx)
                        await self.add(ctx , url)
            elif url.startswith('https://drive.google.com/file/d/'):         #處理 Google 雲端音樂檔案
                try:
                    if self.allMusicPlayingStatus[ctx.guild.id].playing == False:        #找不到此項或=False則進except
                        0/0
                except:
                    await self.JoinChannel(ctx)
                    self.allMusicPlayingStatus[ctx.guild.id] = self.musicPlayingStatus(ctx , self.settings , self.bot.get_cog('MySQL'))
                    self.allMusicPlayingStatus[ctx.guild.id].playing = True
                    self.allMusicPlayingStatus[ctx.guild.id].initTempMusic(1 , 2)
                    await self.allMusicPlayingStatus[ctx.guild.id].getGDMusicInfo(1 , url)
                    await self.allMusicPlayingStatus[ctx.guild.id].PutMusic()
                    await self.allMusicPlayingStatus[ctx.guild.id].GetMusic()
                    self.bot.loop.create_task(self.AudioPlayerTask(ctx))
                else:
                    await self.JoinChannel(ctx)
                    await self.add(ctx , url)
            elif url.startswith('https://www.bilibili.com/video/') or url.startswith('https://b23.tv/') or url.startswith('http://b23.tv/') or url.startswith('https://space.bilibili.com/'):         #處理 bilibili 影片
                try:
                    if self.allMusicPlayingStatus[ctx.guild.id].playing == False:        #找不到此項或=False則進except
                        0/0
                except:
                    if url.startswith('https://www.bilibili.com/video/') or url.startswith('https://b23.tv/') or url.startswith('http://b23.tv/'):
                        await self.JoinChannel(ctx)
                        self.allMusicPlayingStatus[ctx.guild.id] = self.musicPlayingStatus(ctx , self.settings , self.bot.get_cog('MySQL'))
                        self.allMusicPlayingStatus[ctx.guild.id].playing = True
                        self.allMusicPlayingStatus[ctx.guild.id].initTempMusic(1 , 3)
                        try:
                            await self.allMusicPlayingStatus[ctx.guild.id].getBiliMusicInfo(1 , url)
                        except:
                            await ctx.reply('此連結無法播放')
                        else:
                            await self.allMusicPlayingStatus[ctx.guild.id].PutMusic()
                    elif url.startswith('https://space.bilibili.com/'):
                        await self.JoinChannel(ctx)
                        self.allMusicPlayingStatus[ctx.guild.id] = self.musicPlayingStatus(ctx , self.settings , self.bot.get_cog('MySQL'))
                        self.allMusicPlayingStatus[ctx.guild.id].playing = True
                        await self.add(ctx , url)
                    await self.allMusicPlayingStatus[ctx.guild.id].GetMusic()
                    self.bot.loop.create_task(self.AudioPlayerTask(ctx))
                else:
                    await self.JoinChannel(ctx)
                    await self.add(ctx , url)
            else:
                await ctx.reply('此連結無法播放')
        else:
            await ctx.reply('請先進入頻道')

    @commands.command()
    async def playlocal(self , ctx , * , path=None):
        if ctx.author.id == self.settings['adminID']:
            if ctx.author.voice:        #確認用戶在語音頻道裡
                try:
                    if self.allMusicPlayingStatus[ctx.guild.id].playing == False:        #找不到此項或=False則進except
                        0/0
                except:
                    if os.path.isfile(path):
                        await self.JoinChannel(ctx)
                        self.allMusicPlayingStatus[ctx.guild.id] = self.musicPlayingStatus(ctx , self.settings , self.bot.get_cog('MySQL'))
                        self.allMusicPlayingStatus[ctx.guild.id].playing = True
                        if await self.allMusicPlayingStatus[ctx.guild.id].GetMusicQueueLen() < self.settings['musicBotOpts']['maxQueueLen'] + 1:
                            self.allMusicPlayingStatus[ctx.guild.id].initTempMusic(1 , 0)
                            self.allMusicPlayingStatus[ctx.guild.id].tempMusicDict[1].title = os.path.basename(path)
                            self.allMusicPlayingStatus[ctx.guild.id].tempMusicDict[1].audio_url = path
                            self.allMusicPlayingStatus[ctx.guild.id].tempMusicDict[1].thumbnail_url = self.settings['musicBotOpts']['localMusicIcon']
                            await self.allMusicPlayingStatus[ctx.guild.id].PutMusic()
                        else:
                            await ctx.send(f'播放隊列數量已達{self.settings["musicBotOpts"]["maxQueueLen"]}上限')
                        await self.allMusicPlayingStatus[ctx.guild.id].GetMusic()
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
        if ctx.voice_client:        #確認在語音頻道裡
            try:
                if ctx.voice_client.channel != ctx.author.voice.channel:        #確認用戶在相同的語音頻道裡
                    0/0
            except:
                await ctx.reply('請先進入頻道')
            else:
                try:
                    if self.allMusicPlayingStatus[ctx.guild.id].playing == False:        #找不到此項或=False則進except
                        0/0
                except:
                    await ctx.reply('請先播放音樂')
                else:
                    if url.startswith('https://youtube.com/') or url.startswith('https://www.youtube.com/') or url.startswith('https://youtu.be/') or url.startswith('https://m.youtube.com/'):         #處理 YouTube 影片
                        try:
                            if url.startswith('https://youtube.com/'):
                                url = url.replace('https://youtube.com/' , 'https://www.youtube.com/')
                            elif url.startswith('https://m.youtube.com/'):
                                url = url.replace('https://m.youtube.com/' , 'https://www.youtube.com/')
                            elif url.startswith('https://youtu.be/'):
                                url = url.replace('https://youtu.be/' , 'https://www.youtube.com/watch?v=')
                            if url.startswith('https://www.youtube.com/shorts/'):
                                url = url.replace('https://www.youtube.com/shorts/' , 'https://www.youtube.com/watch?v=')
                            if 'playlist?list=' in url or ('watch?v=' in url and '&list=' in url):
                                musicPlaylist = await self.allMusicPlayingStatus[ctx.guild.id].getYTPlaylistEachUrl(url)
                        except:
                            await ctx.reply('此連結無法播放')
                        else:
                            if await self.allMusicPlayingStatus[ctx.guild.id].GetMusicQueueLen() < self.settings['musicBotOpts']['maxQueueLen'] + 1:
                                if 'playlist?list=' in url:
                                    await ctx.send('播放清單處理中 請稍候')
                                    videoNames = ''
                                    sum = self.settings['musicBotOpts']['maxQueueLen'] + 1 - await self.allMusicPlayingStatus[ctx.guild.id].GetMusicQueueLen()
                                    validVideoSum = 0
                                    for i in musicPlaylist:
                                        if i[1]:
                                            validVideoSum += 1
                                    if validVideoSum < sum:
                                        sum = validVideoSum
                                    self.allMusicPlayingStatus[ctx.guild.id].initTempMusic(sum , 1)
                                    errorUrl = []
                                    atLimit = False
                                    times = 0
                                    async with asyncio.TaskGroup() as TG:
                                        for i in musicPlaylist:         #i -> (url , 是否為有效連結)
                                            if times >= sum:
                                                atLimit = True
                                                break
                                            if i[1]:
                                                times += 1
                                                TG.create_task(self.allMusicPlayingStatus[ctx.guild.id].getYTMusicInfo(times , i[0]))
                                            else:
                                                errorUrl.append(i[0])
                                    if errorUrl:
                                        errorText = ''
                                        count = 1
                                        for i in errorUrl:
                                            errorText += f'{"%02d" % count}. {i}\n'
                                            count += 1
                                        embed = discord.Embed(title='以下播放清單中的影片無法播放' , color=0xffff00)
                                        embed.add_field(name='\u200b', value=errorText , inline=False)
                                        await ctx.send(embed=embed)
                                    for i in range(1 , times + 1):
                                        if i > 10:
                                            videoNames += f'\n...後面還有{times-10}項'
                                            break
                                        music = self.allMusicPlayingStatus[ctx.guild.id].tempMusicDict[i]
                                        if i <= 10:
                                            videoNames += f'{"%02d" % (i)}. {music.title} {music.duration if music.duration != "0:00:00" else ""}'
                                            videoNames += '(YouTube直播)\n' if music.file_name == 'live' else '\n'
                                    await self.allMusicPlayingStatus[ctx.guild.id].PutMusic()
                                    if self.settings['webSettings']['url']:
                                        videoNames += '\n\n更多資訊請至 bot 附屬網頁瀏覽'
                                    if atLimit:
                                        await ctx.send(f'播放隊列數量已達{self.settings["musicBotOpts"]["maxQueueLen"]}上限')
                                    if videoNames != '':
                                        embed = discord.Embed(title='已加入隊列' , color=0x00ffff)
                                        embed.add_field(name='\u200b', value=videoNames , inline=False)
                                        await ctx.send(embed=embed)
                                elif 'watch?v=' in url and '&list=' in url:
                                    await ctx.send('播放清單處理中 請稍候')
                                    videoId = url[url.find('watch?v=')+8:url.find('&list=')]
                                    videoPosition = -1
                                    times = 0
                                    for i in musicPlaylist:
                                        if videoId in i[0] and i[1]:
                                            videoPosition = times
                                            break
                                        times += 1
                                    if videoPosition == -1:
                                        await ctx.reply('此連結無法播放')
                                        return 0
                                    musicPlaylist = musicPlaylist[videoPosition:]       #移掉沒要播的影片
                                    videoNames = ''
                                    sum = self.settings['musicBotOpts']['maxQueueLen'] + 1 - await self.allMusicPlayingStatus[ctx.guild.id].GetMusicQueueLen()
                                    validVideoSum = 0
                                    for i in musicPlaylist:
                                        if i[1]:
                                            validVideoSum += 1
                                    if validVideoSum < sum:
                                        sum = validVideoSum
                                    errorUrl = []
                                    times = 0
                                    atLimit = False
                                    self.allMusicPlayingStatus[ctx.guild.id].initTempMusic(sum , 1)
                                    async with asyncio.TaskGroup() as TG:
                                        for i in musicPlaylist:
                                            if times >= sum:
                                                atLimit = True
                                                break
                                            if i[1]:
                                                times += 1
                                                TG.create_task(self.allMusicPlayingStatus[ctx.guild.id].getYTMusicInfo(times , i[0]))
                                            else:
                                                errorUrl.append(url)
                                    if errorUrl:
                                        errorText = ''
                                        count = 1
                                        for i in errorUrl:
                                            errorText += f'{"%02d" % count}. {i}\n'
                                            count += 1
                                        embed = discord.Embed(title='以下播放清單中的影片無法播放' , color=0xffff00)
                                        embed.add_field(name='\u200b', value=errorText , inline=False)
                                        await ctx.send(embed=embed)
                                    for i in range(1 , times + 1):
                                        if i > 10:
                                            videoNames += f'\n...後面還有{times-10}項'
                                            break
                                        music = self.allMusicPlayingStatus[ctx.guild.id].tempMusicDict[i]
                                        if i <= 10:
                                            videoNames += f'{"%02d" % (i)}. {music.title} {music.duration if music.duration != "0:00:00" else ""}'
                                            videoNames += '(YouTube直播)\n' if music.file_name == 'live' else '\n'
                                    await self.allMusicPlayingStatus[ctx.guild.id].PutMusic()
                                    if self.settings['webSettings']['url']:
                                        videoNames += '\n\n更多資訊請至 bot 附屬網頁瀏覽'
                                    if atLimit:
                                        await ctx.send(f'播放隊列數量已達{self.settings["musicBotOpts"]["maxQueueLen"]}上限')
                                    if videoNames != '':
                                        embed = discord.Embed(title='已加入隊列' , color=0x00ffff)
                                        embed.add_field(name='\u200b', value=videoNames , inline=False)
                                        await ctx.send(embed=embed)
                                else:
                                    self.allMusicPlayingStatus[ctx.guild.id].initTempMusic(1 , 1)
                                    try:
                                        await self.allMusicPlayingStatus[ctx.guild.id].getYTMusicInfo(1 , url)
                                    except:
                                        await ctx.reply('此連結無法播放')
                                    else:
                                        music = self.allMusicPlayingStatus[ctx.guild.id].tempMusicDict[1]
                                        await self.allMusicPlayingStatus[ctx.guild.id].PutMusic()
                                        if await self.allMusicPlayingStatus[ctx.guild.id].GetMusicQueueLen() >= self.settings['musicBotOpts']['maxQueueLen'] + 1:
                                            await ctx.send(f'播放隊列數量已達{self.settings["musicBotOpts"]["maxQueueLen"]}上限')
                                        if music.file_name == 'live':
                                            text = 'YouTube直播'
                                        else:
                                            text =  f'長度：{music.duration}' if music.duration != '0:00:00' else None
                                        embed = discord.Embed(title=music.title, description=text , color=0x00ffff)
                                        embed.set_author(name="已加入隊列")
                                        await ctx.send(embed=embed)
                            else:
                                await ctx.send(f'播放隊列數量已達{self.settings["musicBotOpts"]["maxQueueLen"]}上限')
                    elif url.startswith('https://drive.google.com/file/d/'):         #處理 Google 雲端音樂檔案
                        if await self.allMusicPlayingStatus[ctx.guild.id].GetMusicQueueLen() < self.settings['musicBotOpts']['maxQueueLen'] + 1:
                            self.allMusicPlayingStatus[ctx.guild.id].initTempMusic(1 , 2)
                            await self.allMusicPlayingStatus[ctx.guild.id].getGDMusicInfo(1 , url)
                            music = self.allMusicPlayingStatus[ctx.guild.id].tempMusicDict[1]
                            await self.allMusicPlayingStatus[ctx.guild.id].PutMusic()
                            embed = discord.Embed(title=music.title, description='來自 Google 雲端硬碟' , color=0x00ffff)
                            embed.set_author(name="已加入隊列")
                            await ctx.send(embed=embed)
                        else:
                            await ctx.send(f'播放隊列數量已達{self.settings["musicBotOpts"]["maxQueueLen"]}上限')
                    elif url.startswith('https://www.bilibili.com/video/') or url.startswith('https://b23.tv/') or url.startswith('http://b23.tv/') or url.startswith('https://space.bilibili.com/'):         #處理 bilibili 影片
                        try:
                            if url.startswith('https://space.bilibili.com/'):
                                musicPlaylist = await self.allMusicPlayingStatus[ctx.guild.id].getBiliPlaylistEachUrl(url)
                        except:
                            await ctx.reply('此連結無法播放')
                        else:
                            if await self.allMusicPlayingStatus[ctx.guild.id].GetMusicQueueLen() < self.settings['musicBotOpts']['maxQueueLen'] + 1:
                                if url.startswith('https://www.bilibili.com/video/') or url.startswith('https://b23.tv/') or url.startswith('http://b23.tv/'):
                                    self.allMusicPlayingStatus[ctx.guild.id].initTempMusic(1 , 3)
                                    try:
                                        await self.allMusicPlayingStatus[ctx.guild.id].getBiliMusicInfo(1 , url)
                                    except:
                                        await ctx.reply('此連結無法播放')
                                    else:
                                        music = self.allMusicPlayingStatus[ctx.guild.id].tempMusicDict[1]
                                        await self.allMusicPlayingStatus[ctx.guild.id].PutMusic()
                                        embed = discord.Embed(title=music.title, description=music.duration , color=0x00ffff)
                                        embed.set_author(name="已加入隊列")
                                        await ctx.send(embed=embed)
                                elif url.startswith('https://space.bilibili.com/'):
                                    await ctx.send('影片列表處理中 請稍候')
                                    videoNames = ''
                                    sum = self.settings['musicBotOpts']['maxQueueLen'] + 1 - await self.allMusicPlayingStatus[ctx.guild.id].GetMusicQueueLen()
                                    validVideoSum = 0
                                    for i in musicPlaylist:
                                        if i[1]:
                                            validVideoSum += 1
                                    if validVideoSum < sum:
                                        sum = validVideoSum
                                    self.allMusicPlayingStatus[ctx.guild.id].initTempMusic(sum , 1)
                                    errorUrl = []
                                    atLimit = False
                                    times = 0
                                    async with asyncio.TaskGroup() as TG:
                                        for i in musicPlaylist:         #i -> (url , 是否為有效連結)
                                            if times >= sum:
                                                atLimit = True
                                                break
                                            if i[1]:
                                                times += 1
                                                TG.create_task(self.allMusicPlayingStatus[ctx.guild.id].getBiliMusicInfo(times , i[0]))
                                            else:
                                                errorUrl.append(i[0])
                                    if errorUrl:
                                        errorText = ''
                                        count = 1
                                        for i in errorUrl:
                                            errorText += f'{"%02d" % count}. {i}\n'
                                            count += 1
                                        embed = discord.Embed(title='以下影片列表中的影片無法播放' , color=0xffff00)
                                        embed.add_field(name='\u200b', value=errorText , inline=False)
                                        await ctx.send(embed=embed)
                                    for i in range(1 , times + 1):
                                        if i > 10:
                                            videoNames += f'\n...後面還有{times-10}項'
                                            break
                                        music = self.allMusicPlayingStatus[ctx.guild.id].tempMusicDict[i]
                                        if i <= 10:
                                            videoNames += f'{"%02d" % (i)}. {music.title} {music.duration}\n'
                                    await self.allMusicPlayingStatus[ctx.guild.id].PutMusic()
                                    if self.settings['webSettings']['url']:
                                        videoNames += '\n\n更多資訊請至 bot 附屬網頁瀏覽'
                                    if atLimit:
                                        await ctx.send(f'播放隊列數量已達{self.settings["musicBotOpts"]["maxQueueLen"]}上限')
                                    if videoNames != '':
                                        embed = discord.Embed(title='已加入隊列' , color=0x00ffff)
                                        embed.add_field(name='\u200b', value=videoNames , inline=False)
                                        await ctx.send(embed=embed)
                            else:
                                await ctx.send(f'播放隊列數量已達{self.settings["musicBotOpts"]["maxQueueLen"]}上限')
                    else:
                        await ctx.reply('此連結無法播放')
        else:
            await ctx.reply('本 bot 未處於任一語音頻道內')

    @commands.command()
    async def addlocal(self , ctx , *path_):
        path = ''
        if path_:
            for i in range(len(path_)):
                path+=path_[i]
                if i != len(path_):
                    path += ' '
        del path_
        if ctx.author.id == self.settings['adminID']:
            if ctx.voice_client:        #確認在語音頻道裡
                try:
                    if ctx.voice_client.channel != ctx.author.voice.channel:        #確認用戶在相同的語音頻道裡
                        0/0
                except:
                    await ctx.reply('請先進入頻道')
                else:
                    try:
                        if self.allMusicPlayingStatus[ctx.guild.id].playing == False:        #找不到此項或=False則進except
                            0/0
                    except:
                        await ctx.reply('請先播放音樂')
                    else:
                        if os.path.isfile(path):
                            if await self.allMusicPlayingStatus[ctx.guild.id].GetMusicQueueLen() < self.settings['musicBotOpts']['maxQueueLen'] + 1:
                                self.allMusicPlayingStatus[ctx.guild.id].initTempMusic(1 , 0)
                                self.allMusicPlayingStatus[ctx.guild.id].tempMusicDict[1].title = os.path.basename(path)
                                self.allMusicPlayingStatus[ctx.guild.id].tempMusicDict[1].audio_url = path
                                self.allMusicPlayingStatus[ctx.guild.id].tempMusicDict[1].thumbnail_url = self.settings['musicBotOpts']['localMusicIcon']
                                music = self.allMusicPlayingStatus[ctx.guild.id].tempMusicDict[1]
                                await self.allMusicPlayingStatus[ctx.guild.id].PutMusic()
                                embed = discord.Embed(title='本機音樂', description=music.title , color=0x00ffff)
                                embed.set_author(name="已加入隊列")
                                await ctx.send(embed=embed)
                            else:
                                await ctx.send(f'播放隊列數量已達{self.settings["musicBotOpts"]["maxQueueLen"]}上限')
                        else:
                            await ctx.reply('找不到此檔案')
            else:
                await ctx.reply('未處於任一語音頻道內')
        else:
            await ctx.reply('此功能僅限開此bot的管理員使用')

    @commands.command()
    async def pause(self , ctx):
        if ctx.voice_client:
            try:
                if ctx.voice_client.channel != ctx.author.voice.channel:
                    0/0
                else:
                    try:
                        if not self.allMusicPlayingStatus[ctx.guild.id].playing:
                            0/0
                        else:
                            if ctx.voice_client.is_playing():
                                embed = discord.Embed(title='已暫停播放', description=self.allMusicPlayingStatus[ctx.guild.id].music.title , color=0xffff00)
                                await ctx.send(embed=embed)
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
        if ctx.voice_client:
            try:
                if ctx.voice_client.channel != ctx.author.voice.channel:
                    0/0
                else:
                    try:
                        if not self.allMusicPlayingStatus[ctx.guild.id].playing:
                            0/0
                        else:
                            if ctx.voice_client.is_paused():
                                embed = discord.Embed(title='已恢復播放', description=self.allMusicPlayingStatus[ctx.guild.id].music.title , color=0x00ff00)
                                await ctx.send(embed=embed)
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
        if ctx.voice_client:
            try:
                if ctx.voice_client.channel != ctx.author.voice.channel:
                    0/0
                else:
                    if await self.allMusicPlayingStatus[ctx.guild.id].GetMusicQueueLen() == 1:
                        embed = discord.Embed(title='已停止播放' , color=0xff0000)
                        await ctx.send(embed=embed)
                        await self.LeaveChannel(ctx)
                    else:
                        self.allMusicPlayingStatus[ctx.guild.id].SingleLoop = False
                        await self.allMusicPlayingStatus[ctx.guild.id].SetSingleLoop()
                        embed = discord.Embed(title='已跳過', description=self.allMusicPlayingStatus[ctx.guild.id].music.title , color=0x00ffff)
                        await ctx.send(embed=embed)
                        ctx.voice_client.stop()
            except:
                await ctx.reply('請先進入頻道')
        else:
            await ctx.reply('未處於任一語音頻道內')

    @commands.command()
    async def loop(self , ctx):
        if ctx.voice_client:
            try:
                if ctx.voice_client.channel != ctx.author.voice.channel:
                    0/0
            except:
                await ctx.reply('請先進入頻道')
            else:
                try:
                    if self.allMusicPlayingStatus[ctx.guild.id].playing == False:
                        0/0
                    else:
                        await self.allMusicPlayingStatus[ctx.guild.id].GetLoop()
                        if self.allMusicPlayingStatus[ctx.guild.id].SingleLoop == False:
                            self.allMusicPlayingStatus[ctx.guild.id].SingleLoop = True
                            embed = discord.Embed(title='已啟用單曲重複播放', description=self.allMusicPlayingStatus[ctx.guild.id].music.title , color=0x00ff00)
                            await ctx.send(embed=embed)
                        else:
                            self.allMusicPlayingStatus[ctx.guild.id].SingleLoop = False
                            embed = discord.Embed(title='已停用單曲重複播放', description=self.allMusicPlayingStatus[ctx.guild.id].music.title , color=0x00ff00)
                            await ctx.send(embed=embed)
                        await self.allMusicPlayingStatus[ctx.guild.id].SetSingleLoop()
                except:
                    await ctx.reply('未播放')
        else:
            await ctx.reply('未處於任一語音頻道內')

    @commands.command()
    async def stop(self , ctx):
        if ctx.voice_client:
            try:
                if ctx.voice_client.channel != ctx.author.voice.channel:
                    0/0
            except:
                await ctx.reply('請先進入頻道')
            else:
                embed = discord.Embed(title='已停止播放' , color=0xff0000)
                await ctx.send(embed=embed)
                await self.LeaveChannel(ctx)
        else:
            await ctx.reply('未處於任一語音頻道內')

    @commands.command()
    async def join(self , ctx):
        if ctx.author.voice:
            await self.JoinChannel(ctx)
        else:
            await ctx.reply('請先進入頻道')

    @commands.command()
    async def nowplaying(self , ctx):
        try:
            if self.allMusicPlayingStatus[ctx.guild.id].playing == False:
                0/0
            else:
                music = self.allMusicPlayingStatus[ctx.guild.id].music
                loop = '重複' if self.allMusicPlayingStatus[ctx.guild.id].SingleLoop else ''
                if music.type == 0:
                    embed = discord.Embed(title=music.title , color=0x00ff00)
                    embed.set_author(name=f'現正{loop}播放 本機音樂')
                elif music.type == 1:
                    if music.file_name == 'live':
                        text = '直播'
                    else:
                        text =  f'長度：{music.duration}' if music.duration != '0:00:00' else None
                    embed = discord.Embed(title=music.title , description=text , url=music.url , color=0x00ff00)
                    embed.set_author(name=f'現正{loop}播放 YouTube')
                elif music.type == 2:
                    embed = discord.Embed(title=music.title , url=music.url , color=0x00ff00)
                    embed.set_author(name=f'現正{loop}播放 Google雲端硬碟')
                elif music.type == 3:
                    embed = discord.Embed(title=music.title, description=music.duration , url=music.url , color=0x00ff00)
                    embed.set_author(name=f'現正{loop}播放 bilibili')
                embed.set_thumbnail(url=music.thumbnail_url) 
                await ctx.send(embed=embed)
        except:
            await ctx.send('未播放')

    @commands.command()
    async def queue(self , ctx):
        try:
            if await self.allMusicPlayingStatus[ctx.guild.id].GetMusicQueueLen() == 0:      #這是舊的程式碼 應該不會觸發
                0/0
        except:
            await ctx.send('無音樂待播放')
        else:
            queue = await self.allMusicPlayingStatus[ctx.guild.id].GetMusicQueue()
            loop = '重複' if self.allMusicPlayingStatus[ctx.guild.id].SingleLoop else ''
            embed = discord.Embed(title="音樂隊列" , color=0x00ffff)
            if queue[0][8] == 0:
                MusicNames = f'現正{loop}播放\n本機音樂：{queue[0][1]}\n\n'
            elif queue[0][8] == 1:
                MusicNames = f'現正{loop}播放\nYouTube：{queue[0][1]} {queue[0][3] if str(queue[0][3]) != "0:00:00" else ""}'
                MusicNames += ' (直播)\n\n' if queue[0][2] == 'live' else '\n\n'
            elif queue[0][8] == 2:
                MusicNames = f'現正{loop}播放\nGoogle Drive：{queue[0][1]}\n\n'
            elif queue[0][8] == 3:
                MusicNames = f'現正{loop}播放\nbilibili：{queue[0][1]} {queue[0][3]}\n\n'
            if len(queue) >= 2:
                MusicNames += f'音樂隊列\n'
            for i in range(1 , len(queue)):
                if queue[i][8] == 0:
                    MusicNames += f'{"%02d" % (i)}. 本機音樂：{queue[i][1]}\n'
                elif queue[i][8] == 1:
                    MusicNames += f'{"%02d" % (i)}. YouTube：{queue[i][1]} {queue[i][3] if str(queue[i][3]) != "0:00:00" else ""}'
                    MusicNames += ' (直播)\n' if queue[i][2] == 'live' else '\n'
                elif queue[i][8] == 2:
                    MusicNames += f'{"%02d" % (i)}. Google Drive：{queue[i][1]}\n'
                elif queue[i][8] == 3:
                    MusicNames += f'{"%02d" % (i)}. bilibili：{queue[i][1]} {queue[i][3]}\n'
                if i == 10:
                    if len(queue) > 11:
                        MusicNames += f'\n...後面還有{len(queue)-11}項'
                    break
            if self.settings['webSettings']['url']:
                MusicNames += '\n\n更多資訊請至 bot 附屬網頁瀏覽'
            embed.add_field(name='\u200b', value=MusicNames , inline=False)
            await ctx.send(embed=embed)

    async def AudioPlayerTask(self , ctx):
        while True:
            self.allMusicPlayingStatus[ctx.guild.id].PlayNextMusic.clear()
            if not self.allMusicPlayingStatus[ctx.guild.id].SingleLoop:
                if self.allMusicPlayingStatus[ctx.guild.id].music.type == 2:
                    if os.path.isfile('assets/musicBot/musicTemp/' + self.allMusicPlayingStatus[ctx.guild.id].music.file_name):
                        os.remove('assets/musicBot/musicTemp/' + self.allMusicPlayingStatus[ctx.guild.id].music.file_name)
                await self.allMusicPlayingStatus[ctx.guild.id].GetMusic()
                if self.allMusicPlayingStatus[ctx.guild.id].music == None:
                    await self.LeaveChannel(ctx)
                    break
            try:
                if self.allMusicPlayingStatus[ctx.guild.id].music.type == 0:
                    music = self.allMusicPlayingStatus[ctx.guild.id].music
                    if os.path.isfile(music.audio_url):
                        ctx.voice_client.play(discord.FFmpegOpusAudio(executable = 'assets/musicBot/ffmpeg.exe' , bitrate = self.settings['musicBotOpts']['bitrate'] , source = music.audio_url , before_options=self.settings['ffmpegopts']['local']['before_options'] , options=self.settings['ffmpegopts']['local']['options']) , after = lambda _: self.TogglePlayNextMusic(ctx))
                        embed = discord.Embed(title=music.title , color=0x00ff00)
                        embed.set_author(name="現正播放 本機音樂")
                    else:
                        embed = discord.Embed(title=music.title , description='未找到檔案 將跳過' , color=0x00ff00)
                elif self.allMusicPlayingStatus[ctx.guild.id].music.type == 1:
                    try:
                        await self.allMusicPlayingStatus[ctx.guild.id].renewYTMusicInfo()
                    except:
                        embed = discord.Embed(title='播放時發生問題 將跳過', description=self.allMusicPlayingStatus[ctx.guild.id].music.url , color=0x00ff00)
                    else:
                        music = self.allMusicPlayingStatus[ctx.guild.id].music
                        ctx.voice_client.play(discord.FFmpegOpusAudio(executable = 'assets/musicBot/ffmpeg.exe' , bitrate = self.settings['musicBotOpts']['bitrate'] , source = music.audio_url , before_options=self.settings['ffmpegopts']['online']['before_options'] , options=self.settings['ffmpegopts']['online']['options']) , after = lambda _: self.TogglePlayNextMusic(ctx))
                        if music.file_name == 'live':
                            embed = discord.Embed(title=music.title , description='直播' , url=music.url , color=0x00ff00)
                        else:
                            embed = discord.Embed(title=music.title , description=f'長度：{music.duration}' if music.duration != '0:00:00' else None , url=music.url , color=0x00ff00)
                        embed.set_author(name="現正播放 YouTube")
                elif self.allMusicPlayingStatus[ctx.guild.id].music.type == 2:
                    music = self.allMusicPlayingStatus[ctx.guild.id].music
                    await self.allMusicPlayingStatus[ctx.guild.id].downloadGDMusic()
                    ctx.voice_client.play(discord.FFmpegOpusAudio(executable = 'assets/musicBot/ffmpeg.exe' , bitrate = self.settings['musicBotOpts']['bitrate'] , source = 'assets/musicBot/musicTemp/' + music.file_name , before_options=self.settings['ffmpegopts']['local']['before_options'] , options=self.settings['ffmpegopts']['local']['options']) , after = lambda _: self.TogglePlayNextMusic(ctx))
                    embed = discord.Embed(title=music.title , url=music.url , color=0x00ff00)
                    embed.set_author(name="現正播放 Google雲端硬碟")
                elif self.allMusicPlayingStatus[ctx.guild.id].music.type == 3:
                    try:
                        await self.allMusicPlayingStatus[ctx.guild.id].renewBiliMusicInfo()
                        pass
                    except:
                        embed = discord.Embed(title='播放時發生問題 將跳過', description=self.allMusicPlayingStatus[ctx.guild.id].music.url , color=0x00ff00)
                    else:
                        music = self.allMusicPlayingStatus[ctx.guild.id].music
                        ctx.voice_client.play(discord.FFmpegOpusAudio(executable = 'assets/musicBot/ffmpeg.exe' , bitrate = self.settings['musicBotOpts']['bitrate'] , source = music.audio_url , before_options=self.settings['ffmpegopts']['online']['before_options'] , options=self.settings['ffmpegopts']['online']['options']) , after = lambda _: self.TogglePlayNextMusic(ctx))
                        embed = discord.Embed(title=music.title, description=music.duration , url=music.url , color=0x00ff00)
                        embed.set_author(name="現正播放 bilibili")
                embed.set_thumbnail(url=music.thumbnail_url)
                await ctx.send(embed=embed , delete_after=10)
                await self.allMusicPlayingStatus[ctx.guild.id].PlayNextMusic.wait()
                if not self.allMusicPlayingStatus[ctx.guild.id].SingleLoop:
                    await self.allMusicPlayingStatus[ctx.guild.id].PopMusic()
            except:
                self.TogglePlayNextMusic(ctx)

    def TogglePlayNextMusic(self , ctx):
        try:
            self.allMusicPlayingStatus[ctx.guild.id].PlayNextMusic.set()
        except:
            pass

    async def JoinChannel(self , ctx):
        if ctx.author.voice:
            if ctx.voice_client:
                if ctx.voice_client.channel != ctx.author.voice.channel:
                    await ctx.guild.change_voice_state(channel=ctx.author.voice.channel, self_mute=False, self_deaf=True)
            else:
                await ctx.author.voice.channel.connect()
                await ctx.guild.change_voice_state(channel=ctx.author.voice.channel, self_mute=False, self_deaf=True)
        else:
            await ctx.reply('請先進入頻道')

    async def LeaveChannel(self , ctx):
        try:
            if self.allMusicPlayingStatus[ctx.guild.id].playing == False:
                0/0
        except:                                  
            await ctx.voice_client.disconnect()
        else:
            try:
                await ctx.voice_client.disconnect()
                self.allMusicPlayingStatus[ctx.guild.id].CleanMusicTable()
                del self.allMusicPlayingStatus[ctx.guild.id]
            except:      #通常是AttributeError
                pass
        if os.path.isdir('assets/musicBot/musicTemp'):
            shutil.rmtree('assets/musicBot/musicTemp' , ignore_errors = False)

async def setup(bot):
    await bot.add_cog(music_bot(bot))