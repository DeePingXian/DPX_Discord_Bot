import discord
from yt_dlp import YoutubeDL
import os, shutil, asyncio, requests, gdown, uuid, logging
from core.classes import Cog_Extension

class music_bot(Cog_Extension):
    # Music Types
    TYPE_YOUTUBE = 1
    TYPE_BILIBILI = 2
    TYPE_GDRIVE = 3

    # Constants & Defaults
    DEFAULT_MAX_QUEUE_LEN = 500
    DEFAULT_BITRATE = 96
    DEFAULT_GD_SIZE_LIMIT_MB = 100
    TEMP_DIR = "temp/music" # 內部固定的下載路徑
    ALLOWED_AUDIO_FORMATS = ("aac", "flac", "m4a", "mp3", "mp4", "ogg", "opus", "wav", "weba")

    def __init__(self, bot):
        super().__init__(bot)
        self.logger = logging.getLogger("Music")
        
        # 讀取配置
        self.max_queue_len = int(os.getenv("MUSIC_MAX_QUEUE_LEN", self.DEFAULT_MAX_QUEUE_LEN))
        self.music_bitrate = int(os.getenv("MUSIC_BITRATE", self.DEFAULT_BITRATE))
        self.gd_size_limit_mb = int(os.getenv("MUSIC_GD_SIZE_LIMIT_MB", self.DEFAULT_GD_SIZE_LIMIT_MB))

        # In-memory task management
        self.audio_tasks = {} # guild_id: asyncio.Task
        self.play_events = {} # guild_id: asyncio.Event

        # Clear all temporary music data from Redis on startup
        self._clean_all_redis_music_data()
        
        # 初始化暫存目錄
        shutil.rmtree(self.TEMP_DIR, ignore_errors=True)
        os.makedirs(self.TEMP_DIR, exist_ok=True)

        # Hardcoded FFmpeg options
        self.ffmpeg_before_options = "-nostdin -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
        self.ffmpeg_options = "-vn -filter:a 'volume=0.5'"

        self.ytdl_opts = {"format": "bestaudio/best" , "extract_flat": "in_playlist" , "skip_download": True , "nocheckcertificate": True , "ignoreerrors": True , "logtostderr": False , "quiet": True , "no_warnings": True , "default_search": "auto" , "source_address": "0.0.0.0", "js_runtime": "node"}

    def _clean_all_redis_music_data(self):
        """Clean all music-related keys from Redis across all guilds."""
        try:
            self.redis.scan_and_delete_music_data()
            self.logger.info("Cleared all music keys from Redis using SCAN.")
        except Exception as e:
            self.logger.error(f"Failed to scan and clear Redis music data: {e}")

    class MusicDetail:
        """Structure for detailed music information."""
        def __init__(self, type):
            self.url = ""
            self.title = ""
            self.file_name = ""
            self.duration = "0:00:00"
            self.thumbnail_url = ""
            self.audio_url = ""
            self.file_size = 0
            self.type = type # 1:YouTube, 2:Bilibili, 3:GDrive

        def to_dict(self):
            return self.__dict__

        @classmethod
        def from_dict(cls, data):
            if not data: return None
            m = cls(data['type'])
            m.__dict__.update(data)
            return m

    # --- Redis & Task Helpers ---

    def _get_event(self, guild_id):
        if guild_id not in self.play_events:
            self.play_events[guild_id] = asyncio.Event()
        return self.play_events[guild_id]

    def _format_duration(self, dur):
        """將秒數格式化為 H:MM:SS"""
        try:
            dur = int(dur or 0)
            return f'{dur//3600}:{"%02d" % ((dur//60)%60)}:{"%02d" % (dur%60)}'
        except:
            return "0:00:00"

    def _fill_music_metadata(self, music, info_dict):
        """統一填充 MusicDetail 的元數據"""
        if not info_dict: return
        music.audio_url = info_dict.get("url")
        music.title = info_dict.get("title", "")
        # YouTube 直播處理
        if info_dict.get("is_live"):
            music.file_name = "live"
            music.title = music.title[:-16] if len(music.title) > 16 else music.title
        
        music.duration = self._format_duration(info_dict.get("duration"))
        thumbnails = info_dict.get("thumbnails", [])
        music.thumbnail_url = thumbnails[-1].get("url") if thumbnails else info_dict.get("thumbnail")

    # --- Information Fetching Logic ---

    async def getYTMusicInfo(self, url):
        music = self.MusicDetail(self.TYPE_YOUTUBE)
        music.url = url
        with YoutubeDL(self.ytdl_opts) as ytdl:
            infoDict = await asyncio.to_thread(ytdl.extract_info, url, download=False)
            if not infoDict: return None
            self._fill_music_metadata(music, infoDict)
        return music

    async def renewYTMusicInfo(self, music):
        with YoutubeDL(self.ytdl_opts) as ytdl:
            infoDict = await asyncio.to_thread(ytdl.extract_info, music.url, download=False)
            self._fill_music_metadata(music, infoDict)

    async def _fetch_bili_entry_metadata(self, entries):
        """利用 TaskGroup 併發抓取 Bilibili entries 的 metadata (解決 flat extraction 缺少標題的問題)"""
        if not entries: return entries
        
        sem = asyncio.Semaphore(10)
        
        async def fetch(entry):
            if entry.get("title") and entry.get("title") != "未知標題":
                return
            async with sem:
                try:
                    url = entry.get("url") or entry.get("webpage_url") or f"https://www.bilibili.com/video/{entry.get('id')}"
                    with YoutubeDL(self.ytdl_opts) as ytdl:
                        info = await asyncio.to_thread(ytdl.extract_info, url, download=False)
                        if info:
                            entry["title"] = info.get("title")
                            entry["duration"] = info.get("duration")
                            thumbnails = info.get("thumbnails", [])
                            entry["thumbnail"] = thumbnails[-1].get("url") if thumbnails else info.get("thumbnail")
                            entry["url"] = url
                except Exception as e:
                    self.logger.debug(f"Metadata fetch failed for {entry.get('id')}: {e}")

        async with asyncio.TaskGroup() as tg:
            for e in entries:
                tg.create_task(fetch(e))
        return entries

    async def getYTPlaylistEachUrl(self, url):
        with YoutubeDL(self.ytdl_opts) as ytdl:
            infoDict = await asyncio.to_thread(ytdl.extract_info, url, download=False)
        return infoDict.get("entries", []) if infoDict else []

    async def getBiliVideolistEachUrl(self, url):
        with YoutubeDL(self.ytdl_opts) as ytdl:
            infoDict = await asyncio.to_thread(ytdl.extract_info, url, download=False)
        if not infoDict: return []
        return await self._fetch_bili_entry_metadata(infoDict.get("entries", []))

    def _create_music_detail_from_entry(self, entry, music_type):
        """從播放清單的 entry 快速建立 MusicDetail，不進行額外網路請求"""
        m = self.MusicDetail(music_type)
        m.url = entry.get("url") or entry.get("webpage_url")
        if not m.url and entry.get("id"):
            base_urls = {self.TYPE_YOUTUBE: "https://www.youtube.com/watch?v=", self.TYPE_BILIBILI: "https://www.bilibili.com/video/"}
            if music_type in base_urls:
                m.url = f"{base_urls[music_type]}{entry.get('id')}"
        
        m.title = entry.get("title") or "未知標題"
        m.duration = self._format_duration(entry.get("duration"))
        
        thumbnails = entry.get("thumbnails", [])
        m.thumbnail_url = thumbnails[-1].get("url") if thumbnails else entry.get("thumbnail")
        return m

    async def getGDMusicInfo(self, url):
        music = self.MusicDetail(self.TYPE_GDRIVE)
        music.url = url
        resp = await asyncio.to_thread(requests.get, url, stream=True, headers={"user-agent": self.userAgent.random})
        title = (resp.text.partition("</title>")[0]).partition("<title>")[2]
        music.title = title[:title.rfind(" -")]
        
        ext = music.title[music.title.rfind(".")+1:]
        if ext in self.ALLOWED_AUDIO_FORMATS:
            file_id = (url.lstrip("https://drive.google.com/file/d/")).partition("/")[0]
            uc_url = f"https://drive.google.com/uc?export=open&confirm=yTib&id={file_id}"
            final_resp = await asyncio.to_thread(requests.get, uc_url, stream=True, headers={"user-agent": self.userAgent.random})
            music.audio_url = final_resp.url
            music.file_size = int(final_resp.headers.get("Content-length", 0))
            
            if music.file_size <= self.gd_size_limit_mb * 1048576:
                music.file_name = str(uuid.uuid4()) + music.title[music.title.rfind("."):]
            else:
                music.title = f"檔案過大 ({round(music.file_size/1048576, 1)} MB)，上限為 {self.gd_size_limit_mb} MB"
        else:
            music.title = "未經驗證的格式"
        
        return music

    async def downloadGDMusic(self, guild_id, music):
        dest_dir = f"{self.TEMP_DIR}/{guild_id}"
        os.makedirs(dest_dir, exist_ok=True)
        # 透過 UUID 檔名與檢查機制，確保不會覆蓋或重複下載正在使用的檔案
        if music.file_name != "" and music.file_name not in os.listdir(dest_dir):
            file_id = (music.url.lstrip("https://drive.google.com/file/d/")).partition("/")[0]
            await asyncio.to_thread(gdown.download, id=file_id, output=f"{dest_dir}/{music.file_name}", quiet=True)

    async def getBiliMusicInfo(self, url):
        music = self.MusicDetail(self.TYPE_BILIBILI)
        music.url = url
        with YoutubeDL(self.ytdl_opts) as ytdl:
            infoDict = await asyncio.to_thread(ytdl.extract_info, url, download=False)
            if not infoDict: return None
            self._fill_music_metadata(music, infoDict)
        return music

    async def renewBiliMusicInfo(self, music):
        with YoutubeDL(self.ytdl_opts) as ytdl:
            infoDict = await asyncio.to_thread(ytdl.extract_info, music.url, download=False)
            if not infoDict: return
            # 確保獲取到有效的音檔連結
            for _ in range(3): # 最多嘗試 3 次
                if infoDict.get("url", "").startswith("http"): break
                infoDict = await asyncio.to_thread(ytdl.extract_info, music.url, download=False)
            self._fill_music_metadata(music, infoDict)

    # --- Core Playback Logic ---

    async def audioPlayerTask(self, interaction: discord.Interaction, sendInteractionFollowupForOnce=False):
        guild_id = interaction.guild.id
        event = self._get_event(guild_id)
        
        while True:
            event.clear()
            is_loop = self.redis.get_loop(guild_id)
            current_data = self.redis.get_current_music(guild_id)
            current_music = self.MusicDetail.from_dict(current_data) if current_data else None

            if not is_loop:
                # 播放下一首前，清理掉上一個 GD 暫存檔
                if current_music and current_music.type == self.TYPE_GDRIVE:
                    file_path = f"{self.TEMP_DIR}/{guild_id}/{current_music.file_name}"
                    if os.path.isfile(file_path):
                        try: os.remove(file_path)
                        except: pass
                
                # Fetch next song from Redis queue
                next_data = self.redis.pop_queue(guild_id)
                if next_data:
                    current_music = self.MusicDetail.from_dict(next_data)
                    self.redis.set_current_music(guild_id, current_music.to_dict())
                else:
                    self.redis.clear_current_music(guild_id)
                    await self.leaveChannel(interaction)
                    break
            
            try:
                vc = interaction.guild.voice_client
                if not vc: break

                if current_music.type == self.TYPE_YOUTUBE: # YouTube
                    try:
                        await self.renewYTMusicInfo(current_music)
                        self.redis.set_current_music(guild_id, current_music.to_dict())
                        vc.play(discord.FFmpegOpusAudio(source=current_music.audio_url, bitrate=self.music_bitrate, before_options=self.ffmpeg_before_options, options=self.ffmpeg_options), after=lambda _: self.bot.loop.call_soon_threadsafe(event.set))
                        desc = "直播" if current_music.file_name == "live" else (f'長度：{current_music.duration}' if current_music.duration != "0:00:00" else None)
                        embed = discord.Embed(title=current_music.title, description=desc, url=current_music.url, color=0x00ff00)
                        embed.set_author(name="▶️ 現正播放 YouTube")
                    except Exception as e:
                        self.logger.error(f"YouTube 播放錯誤: {e}")
                        embed = discord.Embed(title="⚠️ 播放時發生問題 將跳過", description=current_music.url, color=0x00ff00)
                        self.bot.loop.call_soon_threadsafe(event.set)

                elif current_music.type == self.TYPE_GDRIVE: # GDrive
                    await self.downloadGDMusic(guild_id, current_music)
                    file_path = f"{self.TEMP_DIR}/{guild_id}/{current_music.file_name}"
                    if os.path.isfile(file_path):
                        vc.play(discord.FFmpegOpusAudio(source=file_path, bitrate=self.music_bitrate, options=self.ffmpeg_options), after=lambda _: self.bot.loop.call_soon_threadsafe(event.set))
                        embed = discord.Embed(title=current_music.title, url=current_music.url, color=0x00ff00)
                        embed.set_author(name="▶️現正播放 Google雲端硬碟")
                    else:
                        embed = discord.Embed(title="⚠️ 下載失敗 將跳過", description=current_music.title, color=0x00ff00)
                        self.bot.loop.call_soon_threadsafe(event.set)

                elif current_music.type == self.TYPE_BILIBILI: # Bilibili
                    try:
                        await self.renewBiliMusicInfo(current_music)
                        self.redis.set_current_music(guild_id, current_music.to_dict())
                        # Bilibili 必須帶上 Referer 與 User-Agent 標頭，且需以 \r\n 結尾
                        headers = f"Referer: https://www.bilibili.com/\r\nUser-Agent: {self.userAgent.random}\r\n"
                        bili_before_options = self.ffmpeg_before_options + f' -headers "{headers}"'
                        vc.play(discord.FFmpegOpusAudio(source=current_music.audio_url, bitrate=self.music_bitrate, before_options=bili_before_options, options=self.ffmpeg_options), after=lambda _: self.bot.loop.call_soon_threadsafe(event.set))
                        embed = discord.Embed(title=current_music.title, description=current_music.duration, url=current_music.url, color=0x00ff00)
                        embed.set_author(name="▶️ 現正播放 bilibili")
                    except Exception as e:
                        self.logger.error(f"Bilibili 播放錯誤: {e}")
                        embed = discord.Embed(title="⚠️ 播放時發生問題 將跳過", description=current_music.url, color=0x00ff00)
                        self.bot.loop.call_soon_threadsafe(event.set)

                if current_music.thumbnail_url:
                    embed.set_thumbnail(url=current_music.thumbnail_url)
                
                if sendInteractionFollowupForOnce:
                    await interaction.followup.send(embed=embed)
                    sendInteractionFollowupForOnce = False
                else:
                    await interaction.channel.send(embed=embed, delete_after=10)
                
                # Wait for track finish
                await event.wait()
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"⚠️ 播放迴圈錯誤: {e}")
                self.bot.loop.call_soon_threadsafe(event.set)

    async def joinChannel(self, interaction: discord.Interaction):
        if interaction.user.voice:
            if interaction.guild.voice_client:
                if interaction.guild.voice_client.channel != interaction.user.voice.channel:
                    await interaction.guild.voice_client.move_to(interaction.user.voice.channel)
            else:
                await interaction.user.voice.channel.connect()
                await interaction.guild.change_voice_state(channel=interaction.user.voice.channel, self_mute=False, self_deaf=True)
            return True
        else:
            await interaction.response.send_message("❌ 請先進入語音頻道")
            return False

    async def leaveChannel(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        if interaction.guild.voice_client:
            await interaction.guild.voice_client.disconnect()
        
        self.redis.clear_all_music_data(guild_id)
        
        if guild_id in self.audio_tasks:
            self.audio_tasks[guild_id].cancel()
            del self.audio_tasks[guild_id]
        
        # 離開頻道時清理該伺服器的暫存檔
        shutil.rmtree(f"{self.TEMP_DIR}/{guild_id}", ignore_errors=True)

    async def _check_user_state(self, interaction: discord.Interaction):
        if not interaction.user.voice:
            await interaction.response.send_message("❌ 你必須先進入一個語音頻道", ephemeral=True)
            return False
        
        if interaction.guild.voice_client and interaction.guild.voice_client.channel:
            if interaction.user.voice.channel != interaction.guild.voice_client.channel:
                await interaction.response.send_message(f"❌ 你必須進入 `{interaction.guild.voice_client.channel.name}` 才能操作機器人", ephemeral=True)
                return False
        return True

    async def _get_playing_music(self, interaction: discord.Interaction):
        """輔助方法：獲取目前播放中的音樂，若無則發送錯誤訊息並回傳 None"""
        guild_id = interaction.guild.id
        
        # 1. 檢查語音客戶端狀態
        vc = interaction.guild.voice_client
        if not vc or not (vc.is_playing() or vc.is_paused()):
            await interaction.response.send_message("❌ 目前沒有正在播放的音樂", ephemeral=True)
            return None
            
        # 2. 從 Redis 獲取資料
        current_data = self.redis.get_current_music(guild_id)
        music = self.MusicDetail.from_dict(current_data) if current_data else None
        
        if not music:
            await interaction.response.send_message("❌ 找不到播放中的音樂資訊", ephemeral=True)
            return None
            
        return music

    async def _internal_add(self, interaction: discord.Interaction, url: str):
        """內部方法：解析 URL 並加入 Redis 隊列，回傳 (成功標題列表, 失敗列表, 是否已滿)"""
        guild_id = interaction.guild.id
        added_titles = []
        failed_items = [] 
        is_full = False

        # URL 標準化
        url = url.replace("www.youtube.com/", "youtube.com/")
        url = url.replace("music.youtube.com/", "youtube.com/").replace("m.youtube.com/", "youtube.com/").replace("youtu.be/", "youtube.com/watch?v=").replace("youtube.com/shorts/", "youtube.com/watch?v=")
        if "youtube.com/" in url:
            url = url.replace("youtube.com/", "www.youtube.com/")

        # 檢查起始長度
        if self.redis.get_queue_len(guild_id) >= self.max_queue_len:
            return [], [], True

        if "www.youtube.com" in url:
            if "list=" in url:
                try:
                    entries = await self.getYTPlaylistEachUrl(url)
                    if not entries:
                        failed_items.append(url)
                    else:
                        start_index = 0
                        if "watch?v=" in url:
                            vid = url.split("watch?v=")[1].split("&")[0]
                            for i, entry in enumerate(entries):
                                if entry and vid in entry.get("id", ""):
                                    start_index = i
                                    break
                        for entry in entries[start_index:]:
                            if self.redis.get_queue_len(guild_id) >= self.max_queue_len:
                                is_full = True
                                break
                            
                            if not entry or entry.get("title") == "[Private video]":
                                failed_items.append(f"私人影片 {entry.get('url')}" if entry else "未知項目")
                                continue
                                
                            try:
                                m = self._create_music_detail_from_entry(entry, self.TYPE_YOUTUBE)
                                self.redis.push_queue(guild_id, m.to_dict())
                                added_titles.append(m.title)
                            except:
                                failed_items.append(entry.get("title") or "解析失敗項目")
                except:
                    failed_items.append(url)
            else:
                try:
                    m = await self.getYTMusicInfo(url)
                    if m:
                        self.redis.push_queue(guild_id, m.to_dict())
                        added_titles.append(m.title)
                    else:
                        failed_items.append(url)
                except:
                    failed_items.append(url)
        elif "bilibili.com" in url or "b23.tv" in url:
            try:
                entries = await self.getBiliVideolistEachUrl(url)
                if entries:
                    for entry in entries:
                        if self.redis.get_queue_len(guild_id) >= self.max_queue_len:
                            is_full = True
                            break
                        if not entry: continue
                        try:
                            m = self._create_music_detail_from_entry(entry, self.TYPE_BILIBILI)
                            self.redis.push_queue(guild_id, m.to_dict())
                            added_titles.append(m.title)
                        except:
                            failed_items.append(entry.get("title") or "解析失敗項目")
                else:
                    try:
                        m = await self.getBiliMusicInfo(url)
                        if m:
                            self.redis.push_queue(guild_id, m.to_dict())
                            added_titles.append(m.title)
                        else:
                            failed_items.append(url)
                    except:
                        failed_items.append(url)
            except:
                failed_items.append(url)
        elif "drive.google.com" in url:
            try:
                m = await self.getGDMusicInfo(url)
                if m and not m.title.startswith("未經驗證的格式") and not m.title.startswith("檔案過大"):
                    self.redis.push_queue(guild_id, m.to_dict())
                    added_titles.append(m.title)
                else:
                    failed_items.append(m.title if m else url)
            except:
                failed_items.append(url)
        
        return added_titles, failed_items, is_full

    # --- Commands ---

    @discord.app_commands.command(name="play", description="▶️ 播放或加入音樂至隊列 (支援 YouTube, Bilibili, Google Drive)")
    @discord.app_commands.describe(url="連結")
    async def play(self, interaction: discord.Interaction, url: str):
        await interaction.response.defer()
        if not await self._check_user_state(interaction): return

        guild_id = interaction.guild.id
        
        # 加入隊列並取得詳細回饋 (先解析網址，再決定是否進入頻道)
        added_titles, failed_items, is_full = await self._internal_add(interaction, url)
        
        # 處理失敗項目 (Embed 1)
        if failed_items:
            error_embed = discord.Embed(title="以下項目無法播放", color=0xffff00)
            error_text = ""
            for i, item_url in enumerate(failed_items[:10]):
                error_text += f"{i+1:02d}. {item_url}\n"
            if len(failed_items) > 10:
                error_text += f"\n... 以及其他 {len(failed_items)-10} 個項目"
            error_embed.add_field(name="\u200b", value=error_text, inline=False)
            await interaction.followup.send(embed=error_embed)

        # 處理成功項目
        if len(added_titles) > 0:
            is_playing = guild_id in self.audio_tasks and not self.audio_tasks[guild_id].done()
            
            # 如果是播放清單 (多於一首) 或者 機器人本來就在播放，就顯示清單摘要
            if len(added_titles) > 1 or is_playing:
                success_embed = discord.Embed(title="✅ 已成功加入隊列", color=0x00ffff)
                msg = ""
                for i, title in enumerate(added_titles[:10]):
                    msg += f"{i+1:02d}. {title}\n"
                if len(added_titles) > 10:
                    msg += f"\n...後面還有 {len(added_titles)-10} 首音樂"
                success_embed.add_field(name="\u200b", value=msg, inline=False)
                success_embed.set_footer(text=f"本次共加入 {len(added_titles)} 首音樂" + (f"\n⚠️ 隊列已達上限 ({self.max_queue_len})，後續歌曲未加入。" if is_full else ""))
                await interaction.followup.send(embed=success_embed)

            if not is_playing:
                # 確定有歌要播才進入頻道
                if await self.joinChannel(interaction):
                    # 啟動播放任務
                    self.audio_tasks[guild_id] = asyncio.create_task(self.audioPlayerTask(interaction, sendInteractionFollowupForOnce=True))
        elif not failed_items and not is_full:
            await interaction.followup.send("❌ 無法解析或加入該音樂連結")

    @discord.app_commands.command(name="pause", description="⏸️ 暫停播放音樂")
    async def pause(self, interaction: discord.Interaction):
        if not await self._check_user_state(interaction): return
        music = await self._get_playing_music(interaction)
        if not music: return
        
        if interaction.guild.voice_client.is_playing():
            interaction.guild.voice_client.pause()
            embed = discord.Embed(title="⏸️ 已暫停播放", description=music.title, color=0xffff00)
            if music.thumbnail_url: embed.set_thumbnail(url=music.thumbnail_url)
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("目前音樂已經是暫停狀態", ephemeral=True)

    @discord.app_commands.command(name="resume", description="▶️ 恢復播放音樂")
    async def resume(self, interaction: discord.Interaction):
        if not await self._check_user_state(interaction): return
        music = await self._get_playing_music(interaction)
        if not music: return
        
        if interaction.guild.voice_client.is_paused():
            interaction.guild.voice_client.resume()
            embed = discord.Embed(title="▶️ 已恢復播放", description=music.title, color=0x00ff00)
            if music.thumbnail_url: embed.set_thumbnail(url=music.thumbnail_url)
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("目前音樂並非暫停狀態", ephemeral=True)

    @discord.app_commands.command(name="skip", description="⏭️ 跳過目前曲目")
    async def skip(self, interaction: discord.Interaction):
        if not await self._check_user_state(interaction): return
        music = await self._get_playing_music(interaction)
        if not music: return
        
        guild_id = interaction.guild.id
        # 檢查並取消重複播放模式
        is_loop = self.redis.get_loop(guild_id)
        loop_status = ""
        if is_loop:
            self.redis.set_loop(guild_id, False)
            loop_status = "\n(已取消重複播放模式)"

        embed = discord.Embed(title="⏭️ 已跳過目前曲目", description=f"{music.title}{loop_status}", color=0x00ffff)
        if music.thumbnail_url: embed.set_thumbnail(url=music.thumbnail_url)
        interaction.guild.voice_client.stop()
        await interaction.response.send_message(embed=embed)

    @discord.app_commands.command(name="loop", description="🔄 切換單曲重複播放")
    async def loop(self, interaction: discord.Interaction):
        if not await self._check_user_state(interaction): return
        music = await self._get_playing_music(interaction)
        if not music: return
        
        guild_id = interaction.guild.id
        current = self.redis.get_loop(guild_id)
        new_state = not current
        self.redis.set_loop(guild_id, new_state)
        
        embed = discord.Embed(title=f"🔄 單曲重複播放：{'已啟用' if new_state else '已停用'}", description=music.title, color=0x00ffff)
        if music.thumbnail_url: embed.set_thumbnail(url=music.thumbnail_url)
        await interaction.response.send_message(embed=embed)

    @discord.app_commands.command(name="stop", description="⏹️ 停止播放 並清除音樂資料")
    async def stop(self, interaction: discord.Interaction):
        if not await self._check_user_state(interaction): return
        await self.leaveChannel(interaction)
        embed = discord.Embed(title="⏹️ 已停止播放", color=0xff0000)
        await interaction.response.send_message(embed=embed)

    @discord.app_commands.command(name="join", description="加入用戶所在語音頻道")
    async def join(self, interaction: discord.Interaction):
        if await self.joinChannel(interaction):
            await interaction.response.send_message("✅ 已加入頻道")

    @discord.app_commands.command(name="nowplaying", description="查看現正播放的音樂")
    async def nowplaying(self, interaction: discord.Interaction):
        music = await self._get_playing_music(interaction)
        if not music: return
        
        guild_id = interaction.guild.id
        source_map = {self.TYPE_YOUTUBE: "YouTube", self.TYPE_GDRIVE: "Google雲端硬碟", self.TYPE_BILIBILI: "bilibili"}
        loop_str = " (單曲循環中)" if self.redis.get_loop(guild_id) else ""

        desc = "直播" if music.file_name == "live" else (f'長度：{music.duration}' if music.duration != "0:00:00" else None)        
        embed = discord.Embed(title=music.title, description=desc, url=music.url if music.url else None, color=0x00ff00)
        embed.set_author(name=f"現正播放 {source_map.get(music.type, '未知來源')}{loop_str}")
        if music.thumbnail_url: embed.set_thumbnail(url=music.thumbnail_url)
        await interaction.response.send_message(embed=embed)

    @discord.app_commands.command(name="queue", description="查看音樂播放隊列")
    async def queue(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        queue = self.redis.get_queue(guild_id)
        current_data = self.redis.get_current_music(guild_id)
        current = self.MusicDetail.from_dict(current_data) if current_data else None
        
        if not queue and not current:
            await interaction.response.send_message("隊列目前是空的")
            return

        is_loop = self.redis.get_loop(guild_id)
        source_map = {self.TYPE_YOUTUBE: "YT", self.TYPE_BILIBILI: "Bili", self.TYPE_GDRIVE: "GD"}
        embed = discord.Embed(title="音樂隊列", color=0x00ffff)
        msg = ""
        
        if current:
            source_tag = f"[{source_map.get(current.type, '??')}]"
            dur_tag = f" ({current.duration})" if current.duration != "0:00:00" else ""
            title_label = "**現正重複播放：**" if is_loop else "**現正播放：**"
            msg += f"{title_label}\n{source_tag} {current.title}{dur_tag}\n\n"
            
        if queue:
            msg += "**即將播放：**\n"
            for i, song_data in enumerate(queue[:10]):
                m_type = song_data.get('type')
                title = song_data.get('title', '未知曲目')
                dur = song_data.get('duration', '0:00:00')
                
                source_tag = f"[{source_map.get(m_type, '??')}]"
                dur_tag = f" ({dur})" if dur != "0:00:00" else ""
                msg += f"{i+1:02d}. {source_tag} {title}{dur_tag}\n"
                
            if len(queue) > 10:
                msg += f"\n...後面還有 {len(queue)-10} 首"
        
        embed.description = msg
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(music_bot(bot))
