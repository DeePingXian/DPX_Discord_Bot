# DPX_Discord_Bot

DPX Discord Bot 開源版本
---
刪減自閉源的自用版本，自用版本需要連接MySQL才能使用，這裡也跟著繼承，音樂佇列、部分訊息歷史紀錄會存在那，推薦使用XAMPP附帶的MySQL  
雖然這版本的功能不用MySQL也能做到，不過之後可能會把自用版本裡的PHP網頁功能整理出來，到時候就能用上  
程式運行參數於settings.json設定，這份說明文檔的指令前綴字皆是預設值「!!」，實際使用時可自行更改，為表達方便，以下指令前綴字均以預設值「!!」表示  
運行時可使用「!!help」查詢指令  
若播音樂時語音頻道所有人皆退出，此bot並不會跟著退出，而是繼續播下去，故可常駐頻道持續播音樂  
手動使用指令停止播音樂，退出頻道時會跳錯誤訊息，因為不影響運作所以也懶得修，無視即可  
若要使用 Python 環境運行原程式碼，建議使用本人開發時使用的3.10版，其他版本未測試過不知好壞  
這程式僅能使用單執行續執行，將吃重CPU的單核效能  
***
## 直接使用了以下第三方 Python 套件
- discord.py[voice]
- requests  （如果報錯 請更新urllib3）
- youtube-dl
- pytube
- gdown
- openpyxl
- PyMySQL
## 由上述套件呼叫的其他套件
- bs4
- filelock
- pkg_resources
- soupsieve
- tqdm
- optparse
- plistlib
***
## 使用說明
請先至：https://discord.com/developers/applications 註冊一bot，並將該bot的token設定到settings.json中，讓此程式套上使用
<br>

### **以下指令之command_prefix均以預設值「!!」表示**
<br>

### **settings.json**
<br>
說明較重要之項目
<br><br>
<table>
<tr><td>adminID</td><td>您的Discord帳號ID，用於驗證只有本人才能使用的功能</td></tr>
<tr><td>command_prefix</td><td>設定bot的指令前綴字，若訊息開頭為此字串，bot會當指令處理</td></tr>
<tr><td>log_channel_id</td><td>設定傳送log的Discord頻道ID，啟動時每隔一小時bot會在該頻道發送狀態訊息，配合訊息歷史紀錄功能可當log用</td></tr>
<tr><td>MySQLSettings</td><td>設定MySQL連線參數</td></tr>
<tr><td>cookiefile</td><td>設定連YouTube的cookie檔案，播YouTube音樂時使用，用於讓bot瀏覽有年齡限制的影片，若不設定將無法播放有年齡限制的影片</td></tr>
<tr><td>newestNhentaiBookNum</td><td>設定當下nhentai車號上限，隨機產生本子功能會用到</td></tr>
<tr><td>googleDriveFileSizeLimitInMB</td><td>設定播Google雲端音樂的檔案大小上限(單位為MB)，避免下載太大的檔案造成網路塞車</td></tr>
<tr><td>acceptableMusicContainer</td><td>設定播Google雲端音樂可接受的檔案容器，避免被用來播一些不支援的項目造成錯誤，實際可以自行修改</td></tr>
<tr><td>googleDriveIcon</td><td>設定Google雲端圖標的網址，播Google雲端音樂功能會用到</td></tr>
<tr><td>localMusicIcon</td><td>設定本機音樂圖標的網址，播本機音樂功能會用到</td></tr>
<tr><td>BotIconUrl</td><td>設定bot logo圖標網址，查指令功能會用到</td></tr>
<tr><td>TOKEN</td><td>設定bot token（廢話）</td></tr>
</table>
<br><br>

### **應答機**
<br>
使用\assets\AnsweringMachine\下的Excel表格設定<br>
若訊息符合設定條件，bot會回傳設定的訊息內容<br>
在線修改須使用!!reloadmsg讓bot重新載入內容<br>
<br><br><br>

### **產生連結功能**
<table>
<tr><td>!!nh rand</td><td>隨機產生本子</td></tr>
<tr><td>!!nh + (車號)</td><td>查該本子</td></tr>
<tr><td>!!pix + (作品號)</td><td>查該pixiv作品</td></tr>
<tr><td>!!pixu + (作者號)</td><td>查該pixiv作者</td></tr>
<tr><td>!!twiu + (用戶ID)</td><td>查該twitter用戶</td></tr>
</table>
<br><br>

### **播音樂功能**
<table>
<tr><td>!!play + (網址)</td><td>播放該音樂</td></tr>
<tr><td>playlocal + (音樂檔案路徑）</td><td>播放該本機音樂（僅限開bot的管理員使用）</td></tr>
<tr><td>!!add + (網址)</td><td>增加該音樂至播放隊列</td></tr>
<tr><td>addlocal + (音樂檔案路徑)</td><td>增加該本機音樂至播放隊列（僅限開bot的管理員使用）</td></tr>
<tr><td>!!pause</td><td>暫停播放</td></tr>
<tr><td>!!resume</td><td>恢復播放</td></tr>
<tr><td>!!skip</td><td>跳過目前曲目</td></tr>
<tr><td>!!stop</td><td>停止播放 並清除音樂資料</td></tr>
<tr><td>!!join</td><td>加入用戶所在語音頻道</td></tr>
<tr><td>!!queue</td><td>查看播放隊列</td></tr>
<tr><td>!!nowplaying</td><td>查看現正播放</td></tr>
</table>
支援播放的網站：YouTube、Google雲端<br>
並不支援播放YouTube合輯，播放將造成程式故障<br>
如果播音樂發生問題，請使用!!stop清除資料，並再重新操作一次，實在不行請重啟bot
<br><br>

### **其他功能**
<table>
<tr><td>!!status</td><td>回傳 bot 狀態</td></tr>
<tr><td>!!history + (數字)</td><td>回傳前第n個被刪除/編輯的文字訊息 (上限99則)</td></tr>
<tr><td>!!history all</td><td>回傳所有被刪除/編輯的文字訊息 (上限99則)</td></tr>
<tr><td>!!historyf + (數字)</td><td>回傳前第n個被刪除的檔案訊息</td></tr>
<tr><td>!!MajorArcana + (隨意內容)</td><td>產生一張大密儀塔羅牌</td></tr>
<tr><td>!!MajorArcana3 + (隨意內容)</td><td>產生三張大密儀塔羅牌</td></tr>
</table>