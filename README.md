# DPX_Discord_Bot

DPX Discord Bot 開源版本
---
刪減自閉源的自用版本，自用版本需要連接MySQL才能使用，這裡也跟著繼承，音樂佇列、部分訊息歷史紀錄會存在那，推薦使用XAMPP附帶的MySQL，可順便裝上附屬網站程式  
給bot操作的MySQL帳號需給予全域寫入權限，運行時bot將全自動操作MySQL  
本bot附屬網站程式，可以配合使用：<a href="https://github.com/DeePingXian/DPX_Discord_Bot_Website">https://github.com/DeePingXian/DPX_Discord_Bot_Website</a>  
若要使用Python環境運行原程式碼，最低需求是3.11版
這程式僅能使用單執行續執行，將吃重CPU的單核效能  
程式運行參數於settings.json設定，這份說明文檔的指令前綴字皆是預設值「!!」，實際使用時可自行更改，為表達方便，以下指令前綴字均以預設值「!!」表示  
大部分有年齡限制的影片都可以直接播，不需設置cookie，但不保證全部都能播  
***
## 特色重點
- 提供打包編譯版本，擁有比原生CPython更高的執行效率
- 可播 YouTube、Google雲端、bilibili、電腦本地檔案 來源的音樂
- 不偵測語音頻道裡是否有人，可常駐播放音樂
- 自由設定的聊天應答機
- 訊息歷史紀錄功能，可傳回被刪除、編輯的訊息（資料存於本地，無資安問題）
- 可即時查詢指令
- 方便閱讀大量資訊的附屬網頁
- 其他更多功能...
***
## 功能＆使用說明
簡易教學影片：<a href="https://www.youtube.com/watch?v=3XOrqhkXuA0">https://www.youtube.com/watch?v=3XOrqhkXuA0</a>，實際請以這GitHub頁面為主  
請至：<a href="https://discord.com/developers/applications">https://discord.com/developers/applications</a> 註冊一bot，並將該bot的token設定到settings.json中，讓此程式套上使用
<br><br>

### **settings.json**
<br>
各項設定的範例都寫在檔案裡，標示☆為必須更改的項目，△為建議更改的項目，其餘隨意
<br><br>
<table>
<tr><td>項目</td><td>說明</td></tr>
<tr><td>☆adminID</td><td>您的Discord帳號ID，用於驗證只有本人才能使用的功能</td></tr>
<tr><td>command_prefix</td><td>設定bot的指令前綴字，若訊息開頭為此字串，bot會當指令處理</td></tr>
<tr><td>☆log_channel_id</td><td>設定傳送log的Discord頻道ID，啟動時每隔一小時bot會在該頻道發送狀態訊息，配合訊息歷史紀錄功能可當log用</td></tr>
<tr><td>☆MySQLSettings</td><td>設定MySQL連線參數</td></tr>
<tr><td>webSettings/url</td><td>設定本bot附屬網頁網址，若為空則不啟用本bot相關功能</td></tr>
<tr><td>ffmpegopts</td><td>設定FFMPEG參數</td></tr>
<tr><th colspan="2">musicBotOpts</th></tr>
<tr><td>maxQueueLen</td><td>設定音樂隊列項目上限</td></tr>
<tr><td>bitrate</td><td>設定播音樂時之位元率（注意編碼是OPUS，以及實際效果與該DC語音頻道設定有關）</td></tr>
<tr><td>△localMusicIcon</td><td>設定本機音樂圖標的網址，播本機音樂功能會用到</td></tr>
<tr><th colspan="2">googleDrive</th></tr>
<tr><td>fileSizeLimitInMB</td><td>設定播Google雲端音樂的檔案大小上限(單位為MB)，避免下載太大的檔案造成網路塞車</td></tr>
<tr><td>acceptableMusicContainer</td><td>設定播Google雲端音樂可接受的檔案副檔名，避免被用來播一些不支援的項目造成錯誤</td></tr>
<tr><td>△icon</td><td>設定Google雲端圖標的網址，播Google雲端音樂功能會用到</td></tr>
<tr><td>HTTPHeader</td><td>設定抓Google雲端檔案時，向其發送的HTTP標頭</td></tr>
<tr><td>△newestNhentaiBookNum</td><td>設定當下nhentai車號上限，隨機產生本子功能會用到</td></tr>
<tr><td>error_message_file</td><td>設定報錯時傳送的圖片</td></tr>
<tr><td>△BotIconUrl</td><td>設定bot logo圖標網址，查指令功能會用到</td></tr>
<tr><td>☆TOKEN</td><td>設定bot token（廢話）</td></tr>
</table>
<br><br>

### **以下指令之command_prefix均以預設值「!!」表示**
<br><br>

### **應答機**
<br>
<table>
<tr><td>!!sendansweringcontentlist</td><td>傳送應答列表</td></tr>
<tr><td>!!editansweringcontentlist</td><td>修改應答列表（請附上應答列表檔案）</td></tr>
</table>
若訊息符合設定條件，bot會回傳設定的訊息內容<br>
修改訊息附件檔案須手動於\assets\answeringMachine\下修改<br>
<br><br>

### **產生連結功能**
<table>
<tr><td>!!nh rand</td><td>隨機傳送本子連結</td></tr>
<tr><td>!!nh + (車號)</td><td>傳送該本子連結</td></tr>
<tr><td>!!pix + (作品號)</td><td>傳送該pixiv作品連結</td></tr>
<tr><td>!!pixu + (作者號)</td><td>傳送該pixiv作者連結</td></tr>
<tr><td>!!twiu + (用戶ID)</td><td>傳送該twitter用戶連結</td></tr>
</table>
<br><br>

### **播音樂功能**
<table>
<tr><td>!!play + (網址)</td><td>播放該音樂</td></tr>
<tr><td>!!playlocal + (音樂檔案路徑）</td><td>播放該本機音樂（僅限開bot的管理員使用）</td></tr>
<tr><td>!!add + (網址)</td><td>增加該音樂至播放隊列</td></tr>
<tr><td>!!addlocal + (音樂檔案路徑)</td><td>增加該本機音樂至播放隊列（僅限開bot的管理員使用）</td></tr>
<tr><td>!!pause</td><td>暫停播放</td></tr>
<tr><td>!!resume</td><td>恢復播放</td></tr>
<tr><td>!!skip</td><td>跳過目前曲目</td></tr>
<tr><td>!!stop</td><td>停止播放 並清除音樂資料</td></tr>
<tr><td>!!join</td><td>加入用戶所在語音頻道</td></tr>
<tr><td>!!queue</td><td>查看播放隊列</td></tr>
<tr><td>!!nowplaying</td><td>查看現正播放</td></tr>
</table>
支援播放的來源：YouTube影片、直播、播放清單、合輯，Google雲端檔案，bilibili影片、影片列表(beta)，電腦本地檔案<br>
播放B站影片時受限於機制，bot反應會較慢<br>
如果播音樂發生問題，請使用!!stop清除資料，並再重新操作一次，實在不行請重啟bot
<br><br><br>

### **本 bot 附屬網頁相關**
<table>
<tr><td>!!getguildid</td><td>取得本 Discord 伺服器（群組）的 ID</td></tr>
<tr><td>!!getwebtoken</td><td>取得存取網頁用的 token</td></tr>
</table>
<br><br>

### **訊息歷史紀錄功能**
<table>
<tr><td>!!history + (數字)</td><td>回傳前第n個被刪除/編輯的文字訊息 (上限99則)</td></tr>
<tr><td>!!history all</td><td>回傳所有被刪除/編輯的文字訊息 (上限99則)</td></tr>
<tr><td>!!historyf + (數字)</td><td>回傳前第n個被刪除的檔案訊息</td></tr>
</table>
<br><br>

### **其他功能**
<table>
<tr><td>!!help</td><td>查詢指令</td></tr>
<tr><td>!!status</td><td>回傳 bot 狀態</td></tr>
<tr><td>!!majorArcana + (隨意內容)</td><td>產生一張大密儀塔羅牌</td></tr>
<tr><td>!!majorArcana3 + (隨意內容)</td><td>產生三張大密儀塔羅牌</td></tr>
</table>
<br><br>

***
## 直接使用了以下第三方 Python 套件
- discord.py[voice] v2.1.1
- requests
- yt-dlp 2023.2.17
- gdown
- openpyxl
- PyMySQL
***
## 已知錯誤
- 無法播放「<a href="https://www.youtube.com/watch?v=rPJz3syNbtE">https://www.youtube.com/watch?v=rPJz3syNbtE</a>」，且會造成程式錯誤
- 手動使用指令停止播音樂，退出頻道時會跳錯誤訊息，因為不影響運作所以也懶得修，無視即可
- 播放B站影片可能會產生一些錯誤訊息