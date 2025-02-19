import discord
from yt_dlp import YoutubeDL
import os , shutil , asyncio , requests , gdown , uuid
from core.classes import Cog_Extension

class music_bot(Cog_Extension):

    def __init__(self , bot):
        super().__init__(bot)
        self.allMusicPlayingStatus = {}
        self.DB.cleanAllMusicTable()
        shutil.rmtree("assets/musicBot/musicTemp" , ignore_errors = True)       #清空musicTemp

    class MusicPlayingStatus:

        class MusicDetail:
            def __init__(self , type):
                self.url = ""
                self.title = ""
                self.file_name = ""
                self.duration = 0
                self.thumbnail_url = ""
                self.audio_url = ""
                self.file_size = 0
                self.type = type

        def __init__(self , interaction:discord.Interaction , settings , userAgent , DB):
            self.interaction = interaction
            self.music = None
            self.tempMusic = None
            self.tempMusicDict = {}
            self.playNextMusic = asyncio.Event()
            self.playing = False
            self.singleLoop = False
            self.audioPlayerTask = None
            self.userAgent = userAgent
            self.DB = DB
            self.createDatabase()
            self.createMusicTable()
            self.settings = settings
            self.ytdlOpts = {"format": "bestaudio/best" , "extract_flat": False , "skip_download": True , "nocheckcertificate": True , "ignoreerrors": True , "logtostderr": False , "quiet": True , "no_warnings": True , "default_search": "auto" , "source_address": "0.0.0.0"}
            self.ytdlOpts2 = {"format": "bestaudio/best" , "extract_flat": "in_playlist" , "skip_download": True , "nocheckcertificate": True , "ignoreerrors": True , "logtostderr": False , "quiet": True , "no_warnings": True , "default_search": "auto" , "source_address": "0.0.0.0"}
            self.biliOpts = {"format": "bestaudio[abr<=180]" , "extract_flat": False , "skip_download": True , "nocheckcertificate": True , "ignoreerrors": True , "logtostderr": False , "quiet": True , "no_warnings": True , "default_search": "auto" , "source_address": "0.0.0.0"}      #比較穩定

        def initTempMusic(self , sum , type):
            for i in range(1 , sum+1):
                self.tempMusicDict[i] = self.MusicDetail(type)

        async def getYTMusicInfo(self , num , url):
            self.tempMusicDict[num].url = url
            with YoutubeDL(self.ytdlOpts) as ytdl:
                infoDict = await asyncio.to_thread(ytdl.extract_info , url , download=False)
                self.tempMusicDict[num].audio_url = infoDict["url"]
                self.tempMusicDict[num].title = infoDict.get("title" , "") if not infoDict.get("is_live" , None) else infoDict.get("title" , None)[:-16]
                self.tempMusicDict[num].file_name = "live" if infoDict.get("is_live" , None) else ""        #用這欄儲存是否為直播
                dur = int(infoDict.get("duration" , 0))
                self.tempMusicDict[num].duration = f'{dur//3600}:{"%02d" % ((dur//60)%60)}:{"%02d" % (dur%60)}'
                self.tempMusicDict[num].thumbnail_url = infoDict.get("thumbnail" , None)

        async def getYTPlaylistEachUrl(self , url):
            with YoutubeDL(self.ytdlOpts2) as ytdl:
                infoDict = await asyncio.to_thread(ytdl.extract_info , url , download=False)
            list = []
            for i in infoDict["entries"]:
                if i:       #處理如果是None的部分
                    list.append((i["url"] , True if i.get("channel_id" , None) else False))        #(url , 是否為有效連結)
                else:
                    list.append(("（無法處理的影片）" , False))
            return list

        async def renewYTMusicInfo(self):
            with YoutubeDL(self.ytdlOpts) as ytdl:
                infoDict = await asyncio.to_thread(ytdl.extract_info , self.music.url , download=False)
                self.music.audio_url = infoDict["url"]
                self.music.title = infoDict.get("title" , "") if not infoDict.get("is_live" , None) else infoDict.get("title" , None)[:-16]
                self.music.file_name = "live" if infoDict.get("is_live" , None) else ""        #用這欄儲存是否為直播
                dur = int(infoDict.get("duration" , 0))
                self.music.duration = f'{dur//3600}:{"%02d" % ((dur//60)%60)}:{"%02d" % (dur%60)}'
                self.music.thumbnail_url = infoDict.get("thumbnail" , None)

        async def getGDMusicInfo(self , num , url):
            self.tempMusicDict[num].url = url
            self.tempMusicDict[num].title = (((await asyncio.to_thread(requests.get , url , stream=True , headers={"user-agent": self.userAgent.random})).text.partition("</title>"))[0]).partition("<title>")[2]
            self.tempMusicDict[num].title = self.tempMusicDict[num].title[:self.tempMusicDict[num].title.rfind(" -")]
            if self.tempMusicDict[num].title[self.tempMusicDict[num].title.rfind(".")+1:] in self.settings["musicBotOpts"]["acceptableMusicContainer"]:
                self.tempMusicDict[num].audio_url = (self.tempMusicDict[num].url.lstrip("https://drive.google.com/file/d/")).partition("/")[0]
                self.tempMusicDict[num].audio_url = (await asyncio.to_thread(requests.get , "https://drive.google.com/uc?export=open&confirm=yTib&id=" + self.tempMusicDict[num].audio_url , stream=True , headers={"user-agent": self.userAgent.random})).url
                self.tempMusicDict[num].file_size = int((await asyncio.to_thread(requests.get , self.tempMusicDict[num].audio_url , stream=True , headers={"user-agent": self.userAgent.random})).headers["Content-length"])
                if self.tempMusicDict[num].file_size <= self.settings["musicBotOpts"]["googleDrive"]["fileSizeLimitInMB"] * 1048576:
                    self.tempMusicDict[num].file_name = str(uuid.uuid4()) + self.tempMusicDict[num].title[self.tempMusicDict[num].title.rfind("."):]
                else:
                    self.tempMusicDict[num].title = f'檔案名稱「{self.tempMusicDict[num].title}」（{round(self.tempMusicDict[num].file_size/1048576 , 1)}MB）\n檔案大小大於上限{self.settings["musicBotOpts"]["googleDrive"]["fileSizeLimitInMB"]}MB，請壓縮後再播放（建議使用opus編碼）'
            else:
                self.tempMusicDict[num].title = f'檔案名稱「{self.tempMusicDict[num].title}」\n為避免程式不穩，將不播放未經驗證的檔案格式「{self.tempMusicDict[num].title[self.tempMusic.title.rfind("."):]}」'
            self.tempMusicDict[num].duration = 0
            self.tempMusicDict[num].thumbnail_url = self.settings["musicBotOpts"]["googleDrive"]["icon"]

        async def downloadGDMusic(self):
            if not os.path.isdir("assets/musicBot/musicTemp/"+str(self.interaction.guild.id)):
                os.makedirs("assets/musicBot/musicTemp/"+str(self.interaction.guild.id) , exist_ok=True)
            if (self.music.file_name != "") and (not self.music.file_name in os.listdir("assets/musicBot/musicTemp/"+str(self.interaction.guild.id))):
                await asyncio.to_thread(gdown.download , id=(self.music.url.lstrip("https://drive.google.com/file/d/")).partition("/")[0] , output="assets/musicBot/musicTemp/"+str(self.interaction.guild.id)+"/"+self.music.file_name , quiet=True)

        async def isBiliVideoPlaylist(self , url):      #包含影片選集和列表
            with YoutubeDL(self.biliOpts) as ytdl:
                infoDict = await asyncio.to_thread(ytdl.extract_info , url , download=False)
                return True if infoDict.get("entries" , None) else False
        
        async def getBiliMusicInfo(self , num , url):
            self.tempMusicDict[num].url = url
            with YoutubeDL(self.biliOpts) as ytdl:
                infoDict = await asyncio.to_thread(ytdl.extract_info , url , download=False)
                self.tempMusicDict[num].title = infoDict.get("title" , "")
                dur = int(infoDict.get("duration" , 0))
                self.tempMusicDict[num].duration = f'{dur//3600}:{"%02d" % ((dur//60)%60)}:{"%02d" % (dur%60)}'
                self.tempMusicDict[num].thumbnail_url = infoDict.get("thumbnail" , "")

        async def getBiliVideoSelectionInfo(self , url):
            with YoutubeDL(self.biliOpts) as ytdl:
                infoDict = await asyncio.to_thread(ytdl.extract_info , url , download=False)
                sum = self.settings["musicBotOpts"]["maxQueueLen"]+1 - await self.getMusicQueueLen()
                if len(infoDict["entries"])+1 < sum:
                    sum = len(infoDict["entries"])+1
                for i in range(1 , sum):
                    self.tempMusicDict[i] = self.MusicDetail(3)
                    self.tempMusicDict[i].url = infoDict["entries"][i-1].get("webpage_url" , "")
                    self.tempMusicDict[i].title = infoDict["entries"][i-1].get("title" , "")
                    dur = int(infoDict["entries"][i-1].get("duration" , 0))
                    self.tempMusicDict[i].duration = f'{dur//3600}:{"%02d" % ((dur//60)%60)}:{"%02d" % (dur%60)}'
                    self.tempMusicDict[i].thumbnail_url = infoDict["entries"][i-1].get("thumbnail" , "")

        async def getBiliVideolistEachUrl(self , url):
            with YoutubeDL(self.ytdlOpts2) as ytdl:
                infoDict = await asyncio.to_thread(ytdl.extract_info , url , download=False)
            list = []
            for i in infoDict["entries"]:
                list.append((i["url"] , True if i.get("id" , None) else False))        #(url , 是否為有效連結)  偵測是否為有效連結的方法是猜的 不確定
            return list

        async def renewBiliMusicInfo(self):
            with YoutubeDL(self.biliOpts) as ytdl:
                infoDict = await asyncio.to_thread(ytdl.extract_info , self.music.url , download=False)
                while not infoDict["url"].startswith("https://upos-hz-mirrorakam.akamaized.net/"):     #只有這個來源的能正常播放
                    infoDict = await asyncio.to_thread(ytdl.extract_info , self.music.url , download=False)
                self.music.audio_url = infoDict["url"]
                self.music.title = infoDict.get("title" , "")
                dur = int(infoDict.get("duration" , 0))
                self.music.duration = f'{dur//3600}:{"%02d" % ((dur//60)%60)}:{"%02d" % (dur%60)}'
                self.music.thumbnail_url = infoDict.get("thumbnail" , "")

        async def putMusic(self):
            def putMusic_(self):
                for i in range(1 , len(self.tempMusicDict)+1):
                    if self.tempMusicDict.get(i , None):        #單純避免空號
                        self.DB.putMusic(self.interaction.guild.id , self.tempMusicDict.pop(i))
            await asyncio.to_thread(putMusic_ , self)

        async def getMusic(self):
            self.music = await asyncio.to_thread(self.DB.getMusic , self.interaction.guild.id)

        async def popMusic(self):
            await asyncio.to_thread(self.DB.popMusic , self.interaction.guild.id)

        async def getMusicQueueLen(self):
            return await asyncio.to_thread(self.DB.getMusicQueueLen , self.interaction.guild.id)

        async def getMusicQueue(self):
            return await asyncio.to_thread(self.DB.getMusicQueue , self.interaction.guild.id)

        async def setSingleLoop(self):
            await asyncio.to_thread(self.DB.setSingleLoop , self.interaction.guild.id , self.singleLoop)

        async def getLoop(self):
            self.singleLoop = await asyncio.to_thread(self.DB.getLoop , self.interaction.guild.id)

        def createDatabase(self):
            self.DB.createDatabase(self.interaction.guild.id)

        def createMusicTable(self):
            self.DB.createMusicTable(self.interaction.guild.id)

        def cleanMusicTable(self):
            self.DB.cleanMusicTable(self.interaction.guild.id)

    @discord.app_commands.command(name="play" , description="播放該音樂，若為播放清單將從該項的位置依序加入")
    @discord.app_commands.describe(url="連結")
    async def play(self , interaction:discord.Interaction , url:str):
        await interaction.response.defer()      #interaction.response.send_message需在3秒內回應 這樣可以隔15分鐘再回應
        if interaction.user.voice:        #確認用戶在語音頻道裡
            if url.startswith("https://www.youtube.com/") or url.startswith("https://youtube.com/") or url.startswith("https://music.youtube.com/") or url.startswith("https://youtu.be/") or url.startswith("https://m.youtube.com/"):     #處理 YouTube 影片
                try:
                    if url.startswith("https://youtube.com/"):
                        url = url.replace("https://youtube.com/" , "https://www.youtube.com/")
                    elif url.startswith("https://music.youtube.com/"):
                        url = url.replace("https://music.youtube.com/" , "https://www.youtube.com/")
                    elif url.startswith("https://m.youtube.com/"):
                        url = url.replace("https://m.youtube.com/" , "https://www.youtube.com/")
                    elif url.startswith("https://youtu.be/"):
                        url = url.replace("https://youtu.be/" , "https://www.youtube.com/watch?v=")
                    if url.startswith("https://www.youtube.com/shorts/"):
                        url = url.replace("https://www.youtube.com/shorts/" , "https://www.youtube.com/watch?v=")
                except:
                    await interaction.followup.send("此YouTube連結無法播放")
                else:
                    try:
                        if self.allMusicPlayingStatus[interaction.guild.id].playing == False:        #找不到此項或=False則進except
                            raise
                    except:
                        self.allMusicPlayingStatus[interaction.guild.id] = self.MusicPlayingStatus(interaction , self.settings , self.userAgent , self.bot.get_cog("MySQL"))
                        self.allMusicPlayingStatus[interaction.guild.id].playing = True
                        oldVoiceChannelId = interaction.user.voice.channel.id       #避免user離開頻道造成錯誤
                        if "playlist?list=" in url:
                            await self.add(interaction , url)
                        elif ("watch?v=" in url) and ("&list=" in url):
                            await self.add(interaction , url)
                        else:
                            self.allMusicPlayingStatus[interaction.guild.id].initTempMusic(1 , 1)
                            try:
                                await self.allMusicPlayingStatus[interaction.guild.id].getYTMusicInfo(1 , url)
                            except:
                                await interaction.followup.send("此YouTube連結無法播放")
                                return 0
                            else:
                                await self.allMusicPlayingStatus[interaction.guild.id].putMusic()
                        await self.allMusicPlayingStatus[interaction.guild.id].getMusic()
                        try:        #避免user離開頻道造成錯誤
                            interaction.user.voice.channel
                        except:
                            voiceChannel = interaction.guild.get_channel(oldVoiceChannelId)
                            await voiceChannel.connect()
                            await interaction.guild.change_voice_state(channel=voiceChannel, self_mute=False, self_deaf=True)
                        else:
                            await self.joinChannel(interaction)
                        self.allMusicPlayingStatus[interaction.guild.id].audioPlayerTask = asyncio.create_task(self.audioPlayerTask(interaction , sendInteractionFollowupForOnce=True))
                    else:
                        await self.joinChannel(interaction)
                        await self.add(interaction , url)
            elif url.startswith("https://drive.google.com/file/d/"):         #處理 Google 雲端音樂檔案
                try:
                    if self.allMusicPlayingStatus[interaction.guild.id].playing == False:        #找不到此項或=False則進except
                        raise
                except:
                    await self.joinChannel(interaction)
                    self.allMusicPlayingStatus[interaction.guild.id] = self.MusicPlayingStatus(interaction , self.settings , self.userAgent , self.bot.get_cog("MySQL"))
                    self.allMusicPlayingStatus[interaction.guild.id].playing = True
                    self.allMusicPlayingStatus[interaction.guild.id].initTempMusic(1 , 2)
                    await self.allMusicPlayingStatus[interaction.guild.id].getGDMusicInfo(1 , url)
                    await self.allMusicPlayingStatus[interaction.guild.id].putMusic()
                    await self.allMusicPlayingStatus[interaction.guild.id].getMusic()
                    self.allMusicPlayingStatus[interaction.guild.id].audioPlayerTask = asyncio.create_task(self.audioPlayerTask(interaction , sendInteractionFollowupForOnce=True))
                else:
                    await self.joinChannel(interaction)
                    await self.add(interaction , url)
            elif url.startswith("https://www.bilibili.com/video/") or url.startswith("https://b23.tv/") or url.startswith("http://b23.tv/") or url.startswith("https://space.bilibili.com/"):         #處理 bilibili 影片
                try:
                    if self.allMusicPlayingStatus[interaction.guild.id].playing == False:        #找不到此項或=False則進except
                        raise
                except:
                    self.allMusicPlayingStatus[interaction.guild.id] = self.MusicPlayingStatus(interaction , self.settings , self.userAgent , self.bot.get_cog("MySQL"))
                    self.allMusicPlayingStatus[interaction.guild.id].playing = True
                    oldVoiceChannelId = interaction.user.voice.channel.id
                    try:
                        isBiliVideoPlaylist = await self.allMusicPlayingStatus[interaction.guild.id].isBiliVideoPlaylist(url)
                    except:
                        await interaction.followup.send("此bilibili連結無法播放")
                    else:
                        if isBiliVideoPlaylist:
                            await self.add(interaction , url)
                        else:
                            self.allMusicPlayingStatus[interaction.guild.id].initTempMusic(1 , 3)
                            try:
                                await self.allMusicPlayingStatus[interaction.guild.id].getBiliMusicInfo(1 , url)
                            except:
                                await interaction.followup.send("此bilibili連結無法播放")
                                return 0
                            else:
                                await self.allMusicPlayingStatus[interaction.guild.id].putMusic()
                        await self.allMusicPlayingStatus[interaction.guild.id].getMusic()
                        try:
                            interaction.user.voice.channel
                        except:
                            voiceChannel = interaction.guild.get_channel(oldVoiceChannelId)
                            await voiceChannel.connect()
                            await interaction.guild.change_voice_state(channel=voiceChannel, self_mute=False, self_deaf=True)
                        else:
                            await self.joinChannel(interaction)
                        self.allMusicPlayingStatus[interaction.guild.id].audioPlayerTask = asyncio.create_task(self.audioPlayerTask(interaction , sendInteractionFollowupForOnce=True))
                else:
                    await self.joinChannel(interaction)
                    await self.add(interaction , url)
            else:
                await interaction.followup.send("此連結無法播放")
        else:
            await interaction.followup.send("請先進入頻道")

    @discord.app_commands.command(name="playlocal" , description="播放該本機音樂")
    @discord.app_commands.describe(path="音樂檔案路徑" , mode="加入播放模式")
    @discord.app_commands.choices(mode=[discord.app_commands.Choice(name="單一音訊檔案" , value=0) , discord.app_commands.Choice(name="該資料夾內所有音訊檔案" , value=1)])
    async def playlocal(self , interaction:discord.Interaction , path:str , mode:discord.app_commands.Choice[int]=0):
        await interaction.response.defer()
        if mode:
            mode = mode.value
        if await self.bot.is_owner(interaction.user):
            if interaction.user.voice:        #確認用戶在語音頻道裡
                try:
                    if self.allMusicPlayingStatus[interaction.guild.id].playing == False:        #找不到此項或=False則進except
                        raise
                except:
                    if mode == 0:
                        if os.path.isfile(path):
                            await self.joinChannel(interaction)
                            self.allMusicPlayingStatus[interaction.guild.id] = self.MusicPlayingStatus(interaction , self.settings , self.userAgent , self.bot.get_cog("MySQL"))
                            self.allMusicPlayingStatus[interaction.guild.id].playing = True
                            if await self.allMusicPlayingStatus[interaction.guild.id].getMusicQueueLen() < self.settings["musicBotOpts"]["maxQueueLen"] + 1:
                                self.allMusicPlayingStatus[interaction.guild.id].initTempMusic(1 , 0)
                                self.allMusicPlayingStatus[interaction.guild.id].tempMusicDict[1].title = os.path.basename(path)
                                self.allMusicPlayingStatus[interaction.guild.id].tempMusicDict[1].audio_url = path
                                self.allMusicPlayingStatus[interaction.guild.id].tempMusicDict[1].thumbnail_url = self.settings["musicBotOpts"]["localMusicIcon"]
                                await self.allMusicPlayingStatus[interaction.guild.id].putMusic()
                            else:
                                await interaction.followup.send(f'播放隊列數量已達{self.settings["musicBotOpts"]["maxQueueLen"]}上限')
                            await self.allMusicPlayingStatus[interaction.guild.id].getMusic()
                            self.allMusicPlayingStatus[interaction.guild.id].audioPlayerTask = asyncio.create_task(self.audioPlayerTask(interaction , sendInteractionFollowupForOnce=True))
                        else:
                            await interaction.followup.send("找不到此檔案")
                    elif mode == 1:
                        if os.path.isdir(path):
                            musicFiles = []
                            for files in os.listdir(path):
                                if files[files.rfind(".")+1:] in self.settings["musicBotOpts"]["acceptableMusicContainer"]:
                                    musicFiles.append(files)
                            if musicFiles == []:
                                await interaction.followup.send("找不到可播放之音訊檔案")
                            else:                                
                                await self.joinChannel(interaction)
                                self.allMusicPlayingStatus[interaction.guild.id] = self.MusicPlayingStatus(interaction , self.settings , self.userAgent , self.bot.get_cog("MySQL"))
                                self.allMusicPlayingStatus[interaction.guild.id].playing = True
                                await self.addlocal(interaction , path , mode)
                                await self.allMusicPlayingStatus[interaction.guild.id].getMusic()
                                self.allMusicPlayingStatus[interaction.guild.id].audioPlayerTask = asyncio.create_task(self.audioPlayerTask(interaction , sendInteractionFollowupForOnce=True))
                        else:
                            await interaction.followup.send("找不到此資料夾")
                else:
                    await self.joinChannel(interaction)
                    await self.addlocal(interaction , path , mode)
            else:
                await interaction.followup.send("請先進入頻道")
        else:
            await interaction.followup.send("此功能僅限開此bot的管理員使用")

    @discord.app_commands.command(name="add" , description="增加該音樂至播放隊列，若為播放清單將從該項的位置依序加入")
    @discord.app_commands.describe(url="連結")
    async def add_(self , interaction:discord.Interaction , url:str):
        await interaction.response.defer()
        if interaction.guild.voice_client:        #確認在語音頻道裡
            try:
                if interaction.guild.voice_client.channel != interaction.user.voice.channel:        #確認用戶在相同的語音頻道裡
                    raise
            except:
                await interaction.followup.send("請先進入頻道")
            else:
                try:
                    if self.allMusicPlayingStatus[interaction.guild.id].playing == False:        #找不到此項或=False則進except
                        raise
                except:
                    await interaction.followup.send("請先播放音樂")
                else:
                    await self.add(interaction , url)                    
        else:
            await interaction.followup.send("本 bot 目前bot未處於任一語音頻道內")

    async def add(self , interaction:discord.Interaction , url:str):        #使用slash command時無法從其他地方call這個function 需要拆出來另外放
        if url.startswith("https://www.youtube.com/") or url.startswith("https://youtube.com/") or url.startswith("https://music.youtube.com/") or url.startswith("https://youtu.be/") or url.startswith("https://m.youtube.com/"):
            try:
                if url.startswith("https://youtube.com/"):
                    url = url.replace("https://youtube.com/" , "https://www.youtube.com/")
                elif url.startswith("https://music.youtube.com/"):
                    url = url.replace("https://music.youtube.com/" , "https://www.youtube.com/")
                elif url.startswith("https://m.youtube.com/"):
                    url = url.replace("https://m.youtube.com/" , "https://www.youtube.com/")
                elif url.startswith("https://youtu.be/"):
                    url = url.replace("https://youtu.be/" , "https://www.youtube.com/watch?v=")
                if url.startswith("https://www.youtube.com/shorts/"):
                    url = url.replace("https://www.youtube.com/shorts/" , "https://www.youtube.com/watch?v=")
                if "playlist?list=" in url or ("watch?v=" in url and "&list=" in url):
                    musicPlaylist = await self.allMusicPlayingStatus[interaction.guild.id].getYTPlaylistEachUrl(url)
            except:
                await interaction.followup.send("此YouTube連結無法播放")
            else:
                if await self.allMusicPlayingStatus[interaction.guild.id].getMusicQueueLen() < self.settings["musicBotOpts"]["maxQueueLen"] + 1:
                    if "playlist?list=" in url:
                        await interaction.followup.send("播放清單處理中 請稍候")
                        videoNames = ""
                        max = self.settings["musicBotOpts"]["maxQueueLen"] + 1 - await self.allMusicPlayingStatus[interaction.guild.id].getMusicQueueLen()
                        validVideoSum = 0
                        for i in musicPlaylist:
                            if i[1]:
                                validVideoSum += 1
                        if validVideoSum < max:
                            max = validVideoSum
                        self.allMusicPlayingStatus[interaction.guild.id].initTempMusic(max , 1)
                        errorUrl = []
                        atLimit = False
                        times = 0
                        async with asyncio.TaskGroup() as TG:
                            for i in musicPlaylist:         #i -> (url , 是否為有效連結)
                                if times >= max:
                                    atLimit = True
                                    break
                                if i[1]:
                                    times += 1
                                    TG.create_task(self.allMusicPlayingStatus[interaction.guild.id].getYTMusicInfo(times , i[0]))
                                else:
                                    errorUrl.append(i[0])
                        if errorUrl:
                            errorText = ""
                            count = 1
                            for i in errorUrl:
                                errorText += f'{"%02d" % count}. {i}\n'
                                count += 1
                            embed = discord.Embed(title="以下播放清單中的影片無法播放" , color=0xffff00)
                            embed.add_field(name='\u200b', value=errorText , inline=False)
                            await interaction.followup.send(embed=embed)
                        for i in range(1 , times + 1):
                            if i > 10:
                                videoNames += f'\n...後面還有{times-10}項'
                                break
                            music = self.allMusicPlayingStatus[interaction.guild.id].tempMusicDict[i]
                            if i <= 10:
                                videoNames += f'{"%02d" % (i)}. {music.title} {music.duration if music.duration != "0:00:00" else ""}'
                                videoNames += "(YouTube直播)\n" if music.file_name == "live" else "\n"
                        await self.allMusicPlayingStatus[interaction.guild.id].putMusic()
                        if self.settings["webSettings"]["url"]:
                            videoNames += "\n\n更多資訊請至 bot 附屬網頁瀏覽"
                        if atLimit:
                            await interaction.followup.send(f'播放隊列數量已達{self.settings["musicBotOpts"]["maxQueueLen"]}上限')
                        if videoNames != "":
                            embed = discord.Embed(title="已加入隊列" , color=0x00ffff)
                            embed.add_field(name="\u200b", value=videoNames , inline=False)
                            await interaction.followup.send(embed=embed)
                    elif "watch?v=" in url and "&list=" in url:
                        await interaction.followup.send("播放清單處理中 請稍候")
                        videoId = url[url.find("watch?v=")+8:url.find("&list=")]
                        videoPosition = -1
                        times = 0
                        for i in musicPlaylist:
                            if videoId in i[0] and i[1]:
                                videoPosition = times
                                break
                            times += 1
                        if videoPosition == -1:
                            await interaction.followup.send("此YouTube連結無法播放")
                            return 0
                        musicPlaylist = musicPlaylist[videoPosition:]       #移掉沒要播的影片
                        videoNames = ""
                        max = self.settings["musicBotOpts"]["maxQueueLen"] + 1 - await self.allMusicPlayingStatus[interaction.guild.id].getMusicQueueLen()
                        validVideoSum = 0
                        for i in musicPlaylist:
                            if i[1]:
                                validVideoSum += 1
                        if validVideoSum < max:
                            max = validVideoSum
                        errorUrl = []
                        times = 0
                        atLimit = False
                        self.allMusicPlayingStatus[interaction.guild.id].initTempMusic(max , 1)
                        async with asyncio.TaskGroup() as TG:
                            for i in musicPlaylist:
                                if times >= max:
                                    atLimit = True
                                    break
                                if i[1]:
                                    times += 1
                                    TG.create_task(self.allMusicPlayingStatus[interaction.guild.id].getYTMusicInfo(times , i[0]))
                                else:
                                    errorUrl.append(url)
                        if errorUrl:
                            errorText = ""
                            count = 1
                            for i in errorUrl:
                                errorText += f'{"%02d" % count}. {i}\n'
                                count += 1
                            embed = discord.Embed(title="以下播放清單中的影片無法播放" , color=0xffff00)
                            embed.add_field(name='\u200b', value=errorText , inline=False)
                            await interaction.followup.send(embed=embed)
                        for i in range(1 , times + 1):
                            if i > 10:
                                videoNames += f'\n...後面還有{times-10}項'
                                break
                            music = self.allMusicPlayingStatus[interaction.guild.id].tempMusicDict[i]
                            if i <= 10:
                                videoNames += f'{"%02d" % (i)}. {music.title} {music.duration if music.duration != "0:00:00" else ""}'
                                videoNames += "(YouTube直播)\n" if music.file_name == "live" else "\n"
                        await self.allMusicPlayingStatus[interaction.guild.id].putMusic()
                        if self.settings["webSettings"]["url"]:
                            videoNames += "\n\n更多資訊請至 bot 附屬網頁瀏覽"
                        if atLimit:
                            await interaction.followup.send(f'播放隊列數量已達{self.settings["musicBotOpts"]["maxQueueLen"]}上限')
                        if videoNames != "":
                            embed = discord.Embed(title="已加入隊列" , color=0x00ffff)
                            embed.add_field(name='\u200b', value=videoNames , inline=False)
                            await interaction.followup.send(embed=embed)
                    else:
                        self.allMusicPlayingStatus[interaction.guild.id].initTempMusic(1 , 1)
                        try:
                            await self.allMusicPlayingStatus[interaction.guild.id].getYTMusicInfo(1 , url)
                        except:
                            await interaction.followup.send("此YouTube連結無法播放")
                        else:
                            music = self.allMusicPlayingStatus[interaction.guild.id].tempMusicDict[1]
                            await self.allMusicPlayingStatus[interaction.guild.id].putMusic()
                            if await self.allMusicPlayingStatus[interaction.guild.id].getMusicQueueLen() >= self.settings["musicBotOpts"]["maxQueueLen"] + 1:
                                await interaction.followup.send(f'播放隊列數量已達{self.settings["musicBotOpts"]["maxQueueLen"]}上限')
                            if music.file_name == "live":
                                text = "YouTube直播"
                            else:
                                text =  f'長度：{music.duration}' if music.duration != "0:00:00" else None
                            embed = discord.Embed(title=music.title, description=text , color=0x00ffff)
                            embed.set_author(name="已加入隊列")
                            await interaction.followup.send(embed=embed)
                else:
                    await interaction.followup.send(f'播放隊列數量已達{self.settings["musicBotOpts"]["maxQueueLen"]}上限')
        elif url.startswith("https://drive.google.com/file/d/"):         #處理 Google 雲端音樂檔案
            if await self.allMusicPlayingStatus[interaction.guild.id].getMusicQueueLen() < self.settings["musicBotOpts"]["maxQueueLen"] + 1:
                self.allMusicPlayingStatus[interaction.guild.id].initTempMusic(1 , 2)
                await self.allMusicPlayingStatus[interaction.guild.id].getGDMusicInfo(1 , url)
                music = self.allMusicPlayingStatus[interaction.guild.id].tempMusicDict[1]
                await self.allMusicPlayingStatus[interaction.guild.id].putMusic()
                embed = discord.Embed(title=music.title, description="來自 Google 雲端硬碟" , color=0x00ffff)
                embed.set_author(name="已加入隊列")
                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send(f'播放隊列數量已達{self.settings["musicBotOpts"]["maxQueueLen"]}上限')
        elif url.startswith("https://www.bilibili.com/video/") or url.startswith("https://b23.tv/") or url.startswith("http://b23.tv/") or url.startswith("https://space.bilibili.com/"):         #處理 bilibili 影片
            if await self.allMusicPlayingStatus[interaction.guild.id].getMusicQueueLen() < self.settings["musicBotOpts"]["maxQueueLen"] + 1:
                if url.startswith("https://www.bilibili.com/video/") or url.startswith("https://b23.tv/") or url.startswith("http://b23.tv/"):
                    try:
                        isBiliVideoPlaylist = await self.allMusicPlayingStatus[interaction.guild.id].isBiliVideoPlaylist(url)
                    except:
                        await interaction.followup.send("此bilibili連結無法播放")
                    else:
                        if isBiliVideoPlaylist:
                            try:
                                await self.allMusicPlayingStatus[interaction.guild.id].getBiliVideoSelectionInfo(url)
                            except Exception as e:
                                await interaction.followup.send("此bilibili連結無法播放")
                            else:
                                await interaction.followup.send("影片選集處理中 請稍候")
                                videoNames = ""
                                times = len(self.allMusicPlayingStatus[interaction.guild.id].tempMusicDict)
                                for i in range(1 , times+1):
                                    if i > 10:
                                        videoNames += f'\n...後面還有{times-10}項'
                                        break
                                    music = self.allMusicPlayingStatus[interaction.guild.id].tempMusicDict[i]
                                    if i <= 10:
                                        videoNames += f'{"%02d" % (i)}. {music.title} {music.duration}\n'
                                await self.allMusicPlayingStatus[interaction.guild.id].putMusic()
                                if self.settings["webSettings"]["url"]:
                                    videoNames += "\n\n更多資訊請至 bot 附屬網頁瀏覽"
                                if len(self.allMusicPlayingStatus[interaction.guild.id].tempMusicDict) == self.settings["musicBotOpts"]["maxQueueLen"]+1:
                                    await interaction.followup.send(f'播放隊列數量已達{self.settings["musicBotOpts"]["maxQueueLen"]}上限')
                                if videoNames != "":
                                    embed = discord.Embed(title="已加入隊列" , color=0x00ffff)
                                    embed.add_field(name='\u200b', value=videoNames , inline=False)
                                    await interaction.followup.send(embed=embed)
                        else:
                            self.allMusicPlayingStatus[interaction.guild.id].initTempMusic(1 , 3)
                            try:
                                await self.allMusicPlayingStatus[interaction.guild.id].getBiliMusicInfo(1 , url)
                            except:
                                await interaction.followup.send("此bilibili連結無法播放")
                            else:
                                music = self.allMusicPlayingStatus[interaction.guild.id].tempMusicDict[1]
                                await self.allMusicPlayingStatus[interaction.guild.id].putMusic()
                                embed = discord.Embed(title=music.title, description=music.duration , color=0x00ffff)
                                embed.set_author(name="已加入隊列")
                                await interaction.followup.send(embed=embed)
                elif url.startswith("https://space.bilibili.com/"):
                    try:
                        musicPlaylist = await self.allMusicPlayingStatus[interaction.guild.id].getBiliVideolistEachUrl(url)
                    except:
                        await interaction.followup.send("此bilibili連結無法播放")
                    else:
                        await interaction.followup.send("影片列表處理中 請稍候")
                        videoNames = ""
                        sum = self.settings["musicBotOpts"]["maxQueueLen"] + 1 - await self.allMusicPlayingStatus[interaction.guild.id].getMusicQueueLen()
                        validVideoSum = 0
                        for i in musicPlaylist:
                            if i[1]:
                                validVideoSum += 1
                        if validVideoSum < sum:
                            sum = validVideoSum
                        self.allMusicPlayingStatus[interaction.guild.id].initTempMusic(sum , 3)
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
                                    TG.create_task(self.allMusicPlayingStatus[interaction.guild.id].getBiliMusicInfo(times , i[0]))
                                else:
                                    errorUrl.append(i[0])
                        if errorUrl:
                            errorText = ""
                            count = 1
                            for i in errorUrl:
                                errorText += f'{"%02d" % count}. {i}\n'
                                count += 1
                            embed = discord.Embed(title="以下影片列表中的影片無法播放" , color=0xffff00)
                            embed.add_field(name='\u200b', value=errorText , inline=False)
                            await interaction.followup.send(embed=embed)
                        for i in range(1 , times + 1):
                            if i > 10:
                                videoNames += f'\n...後面還有{times-10}項'
                                break
                            music = self.allMusicPlayingStatus[interaction.guild.id].tempMusicDict[i]
                            if i <= 10:
                                videoNames += f'{"%02d" % (i)}. {music.title} {music.duration}\n'
                        await self.allMusicPlayingStatus[interaction.guild.id].putMusic()
                        if self.settings["webSettings"]["url"]:
                            videoNames += "\n\n更多資訊請至 bot 附屬網頁瀏覽"
                        if atLimit:
                            await interaction.followup.send(f'播放隊列數量已達{self.settings["musicBotOpts"]["maxQueueLen"]}上限')
                        if videoNames != "":
                            embed = discord.Embed(title="已加入隊列" , color=0x00ffff)
                            embed.add_field(name='\u200b', value=videoNames , inline=False)
                            await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send(f'播放隊列數量已達{self.settings["musicBotOpts"]["maxQueueLen"]}上限')
        else:
            await interaction.followup.send("此連結無法播放")

    @discord.app_commands.command(name="addlocal" , description="增加該本機音樂至播放隊列")
    @discord.app_commands.describe(path="音樂檔案路徑" , mode="加入播放模式")
    @discord.app_commands.choices(mode=[discord.app_commands.Choice(name="單一音訊檔案" , value=0) , discord.app_commands.Choice(name="該資料夾內所有音訊檔案" , value=1)])
    async def addlocal_(self , interaction:discord.Interaction , path:str , mode:discord.app_commands.Choice[int]=0):
        await interaction.response.defer()
        if await self.bot.is_owner(interaction.user):
            if interaction.guild.voice_client:        #確認在語音頻道裡
                try:
                    if interaction.guild.voice_client.channel != interaction.user.voice.channel:        #確認用戶在相同的語音頻道裡
                        raise
                except:
                    await interaction.followup.send("請先進入頻道")
                else:
                    try:
                        if self.allMusicPlayingStatus[interaction.guild.id].playing == False:        #找不到此項或=False則進except
                            raise
                    except:
                        await interaction.followup.send("請先播放音樂")
                    else:
                        if mode:
                            mode = mode.value
                        await self.addlocal(interaction , path , mode)
            else:
                await interaction.followup.send("目前bot未處於任一語音頻道內")
        else:
            await interaction.followup.send("此功能僅限開此bot的管理員使用")

    async def addlocal(self , interaction:discord.Interaction , path , mode):
        if mode == 0:
            if os.path.isfile(path):
                if await self.allMusicPlayingStatus[interaction.guild.id].getMusicQueueLen() < self.settings["musicBotOpts"]["maxQueueLen"] + 1:
                    self.allMusicPlayingStatus[interaction.guild.id].initTempMusic(1 , 0)
                    self.allMusicPlayingStatus[interaction.guild.id].tempMusicDict[1].title = os.path.basename(path)
                    self.allMusicPlayingStatus[interaction.guild.id].tempMusicDict[1].audio_url = path
                    self.allMusicPlayingStatus[interaction.guild.id].tempMusicDict[1].thumbnail_url = self.settings["musicBotOpts"]["localMusicIcon"]
                    music = self.allMusicPlayingStatus[interaction.guild.id].tempMusicDict[1]
                    await self.allMusicPlayingStatus[interaction.guild.id].putMusic()
                    embed = discord.Embed(title="本機音樂", description=music.title , color=0x00ffff)
                    embed.set_author(name="已加入隊列")
                    await interaction.followup.send(embed=embed)
                else:
                    await interaction.followup.send(f'播放隊列數量已達{self.settings["musicBotOpts"]["maxQueueLen"]}上限')
            else:
                await interaction.followup.send("找不到此檔案")
        elif mode == 1:
            if os.path.isdir(path):
                musicFiles = []
                for files in os.listdir(path):
                    if files[files.rfind(".")+1:] in self.settings["musicBotOpts"]["acceptableMusicContainer"]:
                        musicFiles.append(files)
                max = self.settings["musicBotOpts"]["maxQueueLen"] + 1 - await self.allMusicPlayingStatus[interaction.guild.id].getMusicQueueLen()
                atLimit = False
                if len(musicFiles) >= max:
                    overNum = len(musicFiles) - max
                    atLimit = True
                    for i in range(overNum):
                        musicFiles.pop()
                if musicFiles == []:
                    await interaction.followup.send("找不到可播放之音訊檔案")
                else:
                    self.allMusicPlayingStatus[interaction.guild.id].initTempMusic(len(musicFiles) , 0)
                    fileNames = ""
                    for i in range(1 , len(musicFiles)+1):
                        self.allMusicPlayingStatus[interaction.guild.id].tempMusicDict[i].title = musicFiles[i-1]
                        self.allMusicPlayingStatus[interaction.guild.id].tempMusicDict[i].audio_url = path+"/"+musicFiles[i-1]
                        self.allMusicPlayingStatus[interaction.guild.id].tempMusicDict[i].thumbnail_url = self.settings["musicBotOpts"]["localMusicIcon"]
                    for i in range(1 , len(musicFiles)+1):
                        if i > 10:
                            fileNames += f'\n...後面還有{len(musicFiles)-10}項'
                            break
                        elif i <= 10:
                            fileNames += f"{'%02d' % (i)}. {musicFiles[i-1]}\n"
                    if atLimit:
                        await interaction.followup.send(f'播放隊列數量已達{self.settings["musicBotOpts"]["maxQueueLen"]}上限')
                    if fileNames != "":
                        embed = discord.Embed(title="已加入隊列" , color=0x00ffff)
                        embed.add_field(name='\u200b', value=fileNames , inline=False)
                        await interaction.followup.send(embed=embed)
                    await self.allMusicPlayingStatus[interaction.guild.id].putMusic()
            else:
                await interaction.followup.send("找不到此資料夾")

    @discord.app_commands.command(name="pause" , description="暫停播放音樂")
    async def pause(self , interaction:discord.Interaction):
        await interaction.response.defer()
        if interaction.guild.voice_client:
            try:
                if interaction.guild.voice_client.channel != interaction.user.voice.channel:
                    raise
                else:
                    try:
                        if not self.allMusicPlayingStatus[interaction.guild.id].playing:
                            raise
                        else:
                            if interaction.guild.voice_client.is_playing():
                                embed = discord.Embed(title="已暫停播放", description=self.allMusicPlayingStatus[interaction.guild.id].music.title , color=0xffff00)
                                await interaction.followup.send(embed=embed)
                                interaction.guild.voice_client.pause()
                            else:
                                await interaction.followup.send("目前bot未播放音樂")
                    except:
                        await interaction.followup.send("目前bot未播放音樂")
            except:
                await interaction.followup.send("請先進入頻道")
        else:
            await interaction.followup.send("目前bot未處於任一語音頻道內")

    @discord.app_commands.command(name="resume" , description="恢復播放音樂")
    async def resume(self , interaction:discord.Interaction):
        await interaction.response.defer()
        if interaction.guild.voice_client:
            try:
                if interaction.guild.voice_client.channel != interaction.user.voice.channel:
                    raise
                else:
                    try:
                        if not self.allMusicPlayingStatus[interaction.guild.id].playing:
                            raise
                        else:
                            if interaction.guild.voice_client.is_paused():
                                embed = discord.Embed(title="已恢復播放", description=self.allMusicPlayingStatus[interaction.guild.id].music.title , color=0x00ff00)
                                await interaction.followup.send(embed=embed)
                                interaction.guild.voice_client.resume()
                            else:
                                await interaction.followup.send("未暫停播放")
                    except:
                        await interaction.followup.send("目前bot未播放音樂")
            except:
                await interaction.followup.send("請先進入頻道")
        else:
            await interaction.followup.send("目前bot未處於任一語音頻道內")

    @discord.app_commands.command(name="skip" , description="跳過目前曲目")
    async def skip(self , interaction:discord.Interaction):
        await interaction.response.defer()
        if interaction.guild.voice_client:
            try:
                if interaction.guild.voice_client.channel != interaction.user.voice.channel:
                    raise
                else:
                    if await self.allMusicPlayingStatus[interaction.guild.id].getMusicQueueLen() == 1:
                        embed = discord.Embed(title="已停止播放" , color=0xff0000)
                        await interaction.followup.send(embed=embed)
                        await self.leaveChannel(interaction)
                    else:
                        self.allMusicPlayingStatus[interaction.guild.id].singleLoop = False
                        await self.allMusicPlayingStatus[interaction.guild.id].setSingleLoop()
                        embed = discord.Embed(title="已跳過", description=self.allMusicPlayingStatus[interaction.guild.id].music.title , color=0x00ffff)
                        await interaction.followup.send(embed=embed)
                        interaction.guild.voice_client.stop()
            except:
                await interaction.followup.send("請先進入頻道")
        else:
            await interaction.followup.send("目前bot未處於任一語音頻道內")

    @discord.app_commands.command(name="loop" , description="切換單曲重複播放")
    async def loop(self , interaction:discord.Interaction):
        await interaction.response.defer()
        if interaction.guild.voice_client:
            try:
                if interaction.guild.voice_client.channel != interaction.user.voice.channel:
                    raise
            except:
                await interaction.followup.send("請先進入頻道")
            else:
                try:
                    if self.allMusicPlayingStatus[interaction.guild.id].playing == False:
                        raise
                    else:
                        await self.allMusicPlayingStatus[interaction.guild.id].getLoop()
                        if self.allMusicPlayingStatus[interaction.guild.id].singleLoop == False:
                            self.allMusicPlayingStatus[interaction.guild.id].singleLoop = True
                            embed = discord.Embed(title="已啟用單曲重複播放", description=self.allMusicPlayingStatus[interaction.guild.id].music.title , color=0x00ff00)
                            await interaction.followup.send(embed=embed)
                        else:
                            self.allMusicPlayingStatus[interaction.guild.id].singleLoop = False
                            embed = discord.Embed(title="已停用單曲重複播放", description=self.allMusicPlayingStatus[interaction.guild.id].music.title , color=0x00ff00)
                            await interaction.followup.send(embed=embed)
                        await self.allMusicPlayingStatus[interaction.guild.id].setSingleLoop()
                except:
                    await interaction.followup.send("目前bot未播放音樂")
        else:
            await interaction.followup.send("目前bot未處於任一語音頻道內")

    @discord.app_commands.command(name="stop" , description="停止播放音樂 並清除音樂資料")
    async def stop(self , interaction:discord.Interaction):
        await interaction.response.defer()
        if interaction.guild.voice_client:
            try:
                if interaction.guild.voice_client.channel != interaction.user.voice.channel:
                    raise
            except:
                await interaction.followup.send("請先進入頻道")
            else:
                embed = discord.Embed(title="已停止播放" , color=0xff0000)
                await interaction.followup.send(embed=embed)
                await self.leaveChannel(interaction)
        else:
            await interaction.followup.send("目前bot未處於任一語音頻道內")

    @discord.app_commands.command(name="join" , description="加入用戶所在語音頻道")
    async def join(self , interaction:discord.Interaction):
        await interaction.response.defer()
        if interaction.user.voice:
            await self.joinChannel(interaction)
        else:
            await interaction.followup.send("請先進入頻道")

    @discord.app_commands.command(name="nowplaying" , description="查看現正播放的音樂")
    async def nowplaying(self , interaction:discord.Interaction):
        await interaction.response.defer()
        try:
            if self.allMusicPlayingStatus[interaction.guild.id].playing == False:
                raise
            else:
                music = self.allMusicPlayingStatus[interaction.guild.id].music
                loop = "重複" if self.allMusicPlayingStatus[interaction.guild.id].singleLoop else ""
                if music.type == 0:
                    embed = discord.Embed(title=music.title , color=0x00ff00)
                    embed.set_author(name=f'現正{loop}播放 本機音樂')
                elif music.type == 1:
                    if music.file_name == "live":
                        text = "直播"
                    else:
                        text =  f'長度：{music.duration}' if music.duration != "0:00:00" else None
                    embed = discord.Embed(title=music.title , description=text , url=music.url , color=0x00ff00)
                    embed.set_author(name=f'現正{loop}播放 YouTube')
                elif music.type == 2:
                    embed = discord.Embed(title=music.title , url=music.url , color=0x00ff00)
                    embed.set_author(name=f'現正{loop}播放 Google雲端硬碟')
                elif music.type == 3:
                    embed = discord.Embed(title=music.title, description=music.duration , url=music.url , color=0x00ff00)
                    embed.set_author(name=f'現正{loop}播放 bilibili')
                embed.set_thumbnail(url=music.thumbnail_url) 
                await interaction.followup.send(embed=embed)
        except:
            await interaction.followup.send("目前bot未播放音樂")

    @discord.app_commands.command(name="queue" , description="查看音樂播放隊列")
    async def queue(self , interaction:discord.Interaction):
        await interaction.response.defer()
        try:
            if await self.allMusicPlayingStatus[interaction.guild.id].getMusicQueueLen() == 0:      #這是舊的程式碼 應該不會觸發
                raise
        except:
            await interaction.followup.send("無音樂待播放")
        else:
            queue = await self.allMusicPlayingStatus[interaction.guild.id].getMusicQueue()
            loop = "重複" if self.allMusicPlayingStatus[interaction.guild.id].singleLoop else ""
            embed = discord.Embed(title="音樂隊列" , color=0x00ffff)
            if queue[0][8] == 0:
                MusicNames = f'現正{loop}播放\n本機音樂：{queue[0][1]}\n\n'
            elif queue[0][8] == 1:
                MusicNames = f'現正{loop}播放\nYouTube：{queue[0][1]} {queue[0][3] if str(queue[0][3]) != "0:00:00" else ""}'
                MusicNames += " (直播)\n\n" if queue[0][2] == "live" else "\n\n"
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
                    MusicNames += " (直播)\n" if queue[i][2] == "live" else "\n"
                elif queue[i][8] == 2:
                    MusicNames += f'{"%02d" % (i)}. Google Drive：{queue[i][1]}\n'
                elif queue[i][8] == 3:
                    MusicNames += f'{"%02d" % (i)}. bilibili：{queue[i][1]} {queue[i][3]}\n'
                if i == 10:
                    if len(queue) > 11:
                        MusicNames += f'\n...後面還有{len(queue)-11}項'
                    break
            if self.settings["webSettings"]["url"]:
                MusicNames += "\n\n更多資訊請至 bot 附屬網頁瀏覽"
            embed.add_field(name='\u200b', value=MusicNames , inline=False)
            await interaction.followup.send(embed=embed)

    async def audioPlayerTask(self , interaction:discord.Interaction , sendInteractionFollowupForOnce=False):
        while True:
            self.allMusicPlayingStatus[interaction.guild.id].playNextMusic.clear()
            if not self.allMusicPlayingStatus[interaction.guild.id].singleLoop:
                if self.allMusicPlayingStatus[interaction.guild.id].music.type == 2:
                    if os.path.isfile("assets/musicBot/musicTemp/"+str(interaction.guild.id)+"/"+self.allMusicPlayingStatus[interaction.guild.id].music.file_name):
                        os.remove("assets/musicBot/musicTemp/"+str(interaction.guild.id)+"/"+self.allMusicPlayingStatus[interaction.guild.id].music.file_name)
                await self.allMusicPlayingStatus[interaction.guild.id].getMusic()
                if self.allMusicPlayingStatus[interaction.guild.id].music == None:
                    await self.leaveChannel(interaction)
                    break
            try:
                if self.allMusicPlayingStatus[interaction.guild.id].music.type == 0:
                    music = self.allMusicPlayingStatus[interaction.guild.id].music
                    if os.path.isfile(music.audio_url):
                        interaction.guild.voice_client.play(discord.FFmpegOpusAudio(executable = "assets/musicBot/ffmpeg.exe" , bitrate = self.settings["musicBotOpts"]["bitrate"] , source = music.audio_url , before_options=self.settings["ffmpegopts"]["local"]["before_options"] , options=self.settings["ffmpegopts"]["local"]["options"]) , after = lambda _: self.togglePlayNextMusic(interaction))
                        embed = discord.Embed(title=music.title , color=0x00ff00)
                        embed.set_author(name="現正播放 本機音樂")
                    else:
                        embed = discord.Embed(title=music.title , description="未找到檔案 將跳過" , color=0x00ff00)
                elif self.allMusicPlayingStatus[interaction.guild.id].music.type == 1:
                    try:
                        await self.allMusicPlayingStatus[interaction.guild.id].renewYTMusicInfo()
                    except asyncio.CancelledError:
                        break
                    except:
                        embed = discord.Embed(title="播放時發生問題 將跳過", description=self.allMusicPlayingStatus[interaction.guild.id].music.url , color=0x00ff00)
                    else:
                        music = self.allMusicPlayingStatus[interaction.guild.id].music
                        interaction.guild.voice_client.play(discord.FFmpegOpusAudio(executable = "assets/musicBot/ffmpeg.exe" , bitrate = self.settings["musicBotOpts"]["bitrate"] , source = music.audio_url , before_options=self.settings["ffmpegopts"]["online"]["before_options"] , options=self.settings["ffmpegopts"]["online"]["options"]) , after = lambda _: self.togglePlayNextMusic(interaction))
                        if music.file_name == "live":
                            embed = discord.Embed(title=music.title , description="直播" , url=music.url , color=0x00ff00)
                        else:
                            embed = discord.Embed(title=music.title , description=f'長度：{music.duration}' if music.duration != "0:00:00" else None , url=music.url , color=0x00ff00)
                        embed.set_author(name="現正播放 YouTube")
                elif self.allMusicPlayingStatus[interaction.guild.id].music.type == 2:
                    music = self.allMusicPlayingStatus[interaction.guild.id].music
                    await self.allMusicPlayingStatus[interaction.guild.id].downloadGDMusic()
                    interaction.guild.voice_client.play(discord.FFmpegOpusAudio(executable = "assets/musicBot/ffmpeg.exe" , bitrate = self.settings["musicBotOpts"]["bitrate"] , source = "assets/musicBot/musicTemp/"+str(interaction.guild.id)+"/"+music.file_name , before_options=self.settings["ffmpegopts"]["local"]["before_options"] , options=self.settings["ffmpegopts"]["local"]["options"]) , after = lambda _: self.togglePlayNextMusic(interaction))
                    embed = discord.Embed(title=music.title , url=music.url , color=0x00ff00)
                    embed.set_author(name="現正播放 Google雲端硬碟")
                elif self.allMusicPlayingStatus[interaction.guild.id].music.type == 3:
                    try:
                        await self.allMusicPlayingStatus[interaction.guild.id].renewBiliMusicInfo()
                    except asyncio.CancelledError:
                        break
                    except:
                        embed = discord.Embed(title="播放時發生問題 將跳過", description=self.allMusicPlayingStatus[interaction.guild.id].music.url , color=0x00ff00)
                    else:
                        music = self.allMusicPlayingStatus[interaction.guild.id].music
                        interaction.guild.voice_client.play(discord.FFmpegOpusAudio(executable = "assets/musicBot/ffmpeg.exe" , bitrate = self.settings["musicBotOpts"]["bitrate"] , source = music.audio_url , before_options=self.settings["ffmpegopts"]["online"]["before_options"] , options=self.settings["ffmpegopts"]["online"]["options"]) , after = lambda _: self.togglePlayNextMusic(interaction))
                        embed = discord.Embed(title=music.title, description=music.duration , url=music.url , color=0x00ff00)
                        embed.set_author(name="現正播放 bilibili")
                embed.set_thumbnail(url=music.thumbnail_url)
                if sendInteractionFollowupForOnce:
                    await interaction.followup.send(embed=embed)
                    sendInteractionFollowupForOnce = False
                else:
                    await interaction.channel.send(embed=embed , delete_after=10)
                await self.allMusicPlayingStatus[interaction.guild.id].playNextMusic.wait()
                if not self.allMusicPlayingStatus[interaction.guild.id].singleLoop:
                    await self.allMusicPlayingStatus[interaction.guild.id].popMusic()
            except asyncio.CancelledError:
                break
            except:
                self.togglePlayNextMusic(interaction)

    def togglePlayNextMusic(self , interaction:discord.Integration):
        try:
            self.allMusicPlayingStatus[interaction.guild.id].playNextMusic.set()
        except:
            pass

    async def joinChannel(self , interaction:discord.Interaction):
        if interaction.user.voice:
            if interaction.guild.voice_client:
                if interaction.guild.voice_client.channel != interaction.user.voice.channel:
                    await interaction.guild.change_voice_state(channel=interaction.user.voice.channel, self_mute=False, self_deaf=True)
            else:
                await interaction.user.voice.channel.connect()
                await interaction.guild.change_voice_state(channel=interaction.user.voice.channel, self_mute=False, self_deaf=True)
        else:
            await interaction.response.send_message("請先進入頻道")

    async def leaveChannel(self , interaction:discord.Interaction):
        try:
            if self.allMusicPlayingStatus[interaction.guild.id].playing == False:
                raise
        except:
            await interaction.guild.voice_client.disconnect()
        else:
            try:
                await interaction.guild.voice_client.disconnect()
                self.allMusicPlayingStatus[interaction.guild.id].cleanMusicTable()
                self.allMusicPlayingStatus[interaction.guild.id].audioPlayerTask.cancel()
                del self.allMusicPlayingStatus[interaction.guild.id]
            except:      #通常是AttributeError
                pass
        shutil.rmtree("assets/musicBot/musicTemp/"+str(interaction.guild.id) , ignore_errors=True)

    @discord.app_commands.command(name="download" , description="下載現正播放的音樂")
    async def download(self , interaction:discord.Interaction):
        await interaction.response.defer()
        try:
            if self.allMusicPlayingStatus[interaction.guild.id].playing == False:
                raise
            else:
                music = self.allMusicPlayingStatus[interaction.guild.id].music
                if music.type == 0:
                    embed = discord.Embed(title="本地音樂 不開放下載" , color=0xff0000)
                    embed.set_author(name=music.title)
                elif music.type == 1:
                    if music.file_name == "live":
                        embed = discord.Embed(title="YouTube直播 不開放下載" , color=0xff0000)
                        embed.set_author(name=music.title)
                    else:
                        embed = discord.Embed(title="請按此下載" , url=music.audio_url , color=0x00ff00)
                        embed.set_author(name=music.title)
                elif music.type == 2:
                    embed = discord.Embed(title="請按此下載" , url=music.url , color=0x00ff00)
                    embed.set_author(name=music.title)
                elif music.type == 3:
                    embed = discord.Embed(title="請按此下載" , url=music.audio_url , color=0x00ff00)
                    embed.set_author(name=music.title)
                embed.set_thumbnail(url=music.thumbnail_url) 
                await interaction.followup.send(embed=embed)
        except:
            await interaction.followup.send("目前bot未播放音樂")

async def setup(bot):
    await bot.add_cog(music_bot(bot))