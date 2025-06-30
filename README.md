# DPX_Discord_Bot

DPX Discord Bot 開源版本
---
刪減自閉源的自用版本，需要連接MySQL/MariaDB資料庫才能使用，以儲存動態資料，下方有操作教學  
如果有安裝XAMPP或其他web server，也可順便裝上本bot附屬網站程式配合使用：<a href="https://github.com/DeePingXian/DPX_Discord_Bot_Website">DPX Discord Bot Website</a>  
若要使用Python環境運行原程式碼，最低需求是3.11版  
這程式僅能使用單執行緒執行，將吃重CPU的單核效能  
程式運行參數於settings.json設定  
大部分有年齡限制的YouTube影片都可以直接播，不需設置cookie，但不保證全部都能播  
***
## 特色重點
- 提供打包編譯版本，擁有比原生CPython更高的執行效率
- 連線至<a href="https://character.ai/">Character.AI</a>的AI聊天功能
- 可播 YouTube、Google雲端、bilibili、電腦本地檔案 來源的音樂
- 不偵測語音頻道裡是否有人，可常駐播放音樂
- 自由設定的聊天應答機、新人加入歡迎訊息
- 訊息歷史紀錄功能，可傳回被刪除、編輯的訊息(資料存於本地，無資安問題)
- 可即時查詢指令
- 方便閱讀大量資訊的附屬網頁
- 其他如下更多功能...
***
## 前置設定說明
簡易教學影片：<a href="https://www.youtube.com/watch?v=3XOrqhkXuA0">https://www.youtube.com/watch?v=3XOrqhkXuA0</a>，實際請以這GitHub頁面為主  
請至：<a href="https://discord.com/developers/applications">https://discord.com/developers/applications</a> 註冊一bot，並將該bot的token設定到settings.json中，讓此程式套上使用  
Discord討論群組：<a href="https://discord.gg/wJnNm8Fg9e">DPX Discord Bot 論道堂</a>，歡迎加入交流！
<br><br>

### **settings.json**
各項設定的範例都寫在檔案裡，標示☆為必須更改的項目，△為建議更改的項目，其餘隨意
<br><br>
<table>
<tr><td>項目</td><td>說明</td></tr>
<tr><td>☆TOKEN</td><td>設定bot token</td></tr>
<tr><td>☆logChannelID</td><td>設定傳送bot狀態的Discord頻道ID，請從您的Discord群組裡挑選一頻道按右鍵，複製頻道ID並貼上來，啟動時每隔一小時bot會在該頻道發送狀態訊息，配合訊息歷史紀錄功能可當log用</td></tr>
<tr><td>☆MySQLSettings</td><td>設定MySQL/MariaDB連線參數</td></tr>
<tr><td>maxMessagesSaved</td><td>設定每個頻道儲存在資料庫的訊息歷史紀錄數量上限</td></tr>
<tr><td>webSettings/url</td><td>設定本bot附屬網頁網址，若保留為空則不啟用相關功能</td></tr>
<tr><td>ffmpegopts</td><td>設定FFMPEG參數</td></tr>
<tr><th colspan="2">musicBotOpts</th></tr>
<tr><td>maxQueueLen</td><td>設定音樂隊列項目上限，請根據實際環境效能設置</td></tr>
<tr><td>bitrate</td><td>設定播音樂時之位元率（注意編碼是Opus，以及實際效果與該DC語音頻道設定有關）</td></tr>
<tr><td>△localMusicIcon</td><td>設定本機音樂圖標的網址，播本機音樂功能會用到</td></tr>
<tr><th colspan="2">googleDrive</th></tr>
<tr><td>fileSizeLimitInMB</td><td>設定播Google雲端音樂的檔案大小上限(單位為MB)，避免下載太大的檔案造成網路塞車</td></tr>
<tr><td>acceptableMusicContainer</td><td>設定播Google雲端音樂可接受的檔案副檔名，避免被用來播一些不支援的項目造成錯誤</td></tr>
<tr><td>△icon</td><td>設定Google雲端圖標的網址，播Google雲端音樂功能會用到</td></tr>
<tr><th colspan="2">characteraiSettings</th></tr>
<tr><td>characterID</td><td>設定聊天功能bot所連結的Character.AI角色ID，下方有設定說明，若保留為空則不啟用相關功能</td></tr>
<tr><td>clientToken</td><td>設定Character.AI的使用者token，下方有設定說明，若保留為空則不啟用相關功能</td></tr>
<tr><td>commandPrefix</td><td>已棄用，目前僅為discord套件運行的必要參數</td></tr>
</table>
<br>

### **連接資料庫懶人包**
上方影片推薦的XAMPP整合包由於過於老舊，且遲遲未修復PHP的<a href="https://nvd.nist.gov/vuln/detail/CVE-2024-4577">CVE-2024-4577</a>漏洞，已不推薦使用  
這裡介紹Windows下連接本地MariaDB的懶人包：  
1.下載並安裝<a href="https://mariadb.org/download/?t=mariadb&p=mariadb&r=11.4.2&os=windows&cpu=x86_64&pkg=msi&mirror=ossplanet">MariaDB</a>，<a href="https://officeguide.cc/windows-install-mariadb-database-server-tutorial/">可以參考這篇文章</a>，root帳號的密碼自己記下就行，之後MariaDB會隨著電腦開機自動啟動，不用再手動開啟  
2.開啟順帶安裝的HeidiSQL，點左下角的新增，在右邊輸入root的密碼並點下面的開啟  
3.成功開啟後在左上角的工具打開使用者管理，加入一名使用者，用戶名和密碼隨意設置並記下，並在下方的允許存取勾選全域權限，接著按儲存就可以關閉了，之後不用再開  
4.將剛才的用戶名和密碼設定至settings.json的MySQLSettings項目裡，然後就可以啟動bot了  
<br>

### **從舊版升級教學**
在這個頁面右邊的Releases下載新版程式，解壓縮後將舊版程式裡的assets資料夾移至新版，然後設定新版的settings.json即可  
如果有不相容的地方會在每次更新時說明  
<br>

## 功能說明
### 範例圖片均為示意用途，使用時會根據實際情況、程式版本而變化<br>圖中之指令前綴「!!」已棄用，現已固定為「/」

### **AI聊天功能**

這是讓此bot串接至Character.AI，使其能夠作為AI虛擬角色聊天，目前只能讀取文字訊息，且所有訊息均會視為由同一人發出  
前置設定方法：  
1.請至<a href="https://character.ai/">Character.AI</a>申請帳號，並記下該帳號的E-mail，可以順便調整一下使用者名稱方便AI稱呼  
2.選擇一位要讓bot串接的虛擬角色，並至與該角色聊天的頁面，記下位於網址處的ID（如下圖）  
<img src="https://i.imgur.com/CksxaQl.png"><br>
3.使用此bot的/getchattokenemaillink指令輸入Character.AI的帳號，並至E-mail收取信件  
4.使用此bot的/getchattoken指令輸入E-mail及信件裡的登入連結，即可取得token  
5.將角色ID和token設定至settings.json的characteraiSettings項目裡，重啟bot後就設定完成了

<table>
<tr><td>直接tag此bot + (訊息內容)</td><td>與本bot聊天</td></tr>
<tr><td>/resetchat</td><td>重設聊天狀態</td></tr>
<tr><td>/dellastmsg</td><td>刪除上一則聊天訊息</td></tr>
<tr><td>/getchattokenemaillink</td><td>取得Character.AI的連線token (步驟1/2)</td></tr>
<tr><td>/getchattoken</td><td>取得Character.AI的連線token (步驟2/2)</td></tr>
</table>

<img src="https://i.imgur.com/EpOv0AT.png"><br><br>

### **播音樂功能**
<table>
<tr><td>/play + (網址)</td><td>播放該音樂，若為播放清單將從該項的位置依序加入</td></tr>
<tr><td>/playlocal + (音樂檔案路徑)</td><td>播放本機音樂檔案(僅限開bot的管理員使用)</td></tr>
<tr><td>/add + (網址)</td><td>增加該音樂至播放隊列，若為播放清單將從該項的位置依序加入</td></tr>
<tr><td>/addlocal + (音樂檔案路徑)</td><td>增加本機音樂檔案至播放隊列(僅限開bot的管理員使用)</td></tr>
<tr><td>/pause</td><td>暫停播放音樂</td></tr>
<tr><td>/resume</td><td>恢復播放音樂</td></tr>
<tr><td>/skip</td><td>跳過目前曲目</td></tr>
<tr><td>/loop</td><td>切換單曲重複播放</td></tr>
<tr><td>/stop</td><td>停止播放音樂 並清除音樂資料</td></tr>
<tr><td>/queue</td><td>查看音樂播放隊列</td></tr>
<tr><td>/nowplaying</td><td>查看現正播放的音樂</td></tr>
<tr><td>/download</td><td>下載現正播放的音樂</td></tr>
<tr><td>/join</td><td>加入用戶所在語音頻道</td></tr>
</table>
支援播放的來源：YouTube影片、直播、播放清單、合輯，Google雲端檔案，bilibili影片、影片列表、電腦本地檔案<br>
如果播音樂發生問題，請使用/stop清除資料，並再重新操作一次，實在不行請重啟bot
<br><br>

<img src="https://i.imgur.com/wP00thf.png"><br>
<img src="https://i.imgur.com/Nanq16d.png"><br>
<img src="https://i.imgur.com/4izMhJm.png"><br><br>

### **訊息歷史紀錄功能**
<table>
<tr><td>/history</td><td>查詢最近25則修改的文字訊息</td></tr>
<tr><td>/historyf + (數字)</td><td>回傳前第n個被刪除的檔案訊息</td></tr>
<tr><td>/historyflist</td><td>回傳已刪除的附件檔案列表</td></tr>
<tr><td>/historyall + (選項 選項 選項)</td><td>匯出欲查詢的的文字訊息類型總集之Excel檔，只選擇欲查詢的項目即可</td></tr>
</table>

<img src="https://i.imgur.com/OjLJWQ1.png"><br>
<img src="https://i.imgur.com/numxDRL.png"><br>
<img src="https://i.imgur.com/cD4lOMI.png"><br><br>

### **應答機功能**
<table>
<tr><td>/sendansweringmsglist</td><td>傳送應答訊息列表檔案</td></tr>
<tr><td>/editansweringmsglist</td><td>修改應答訊息列表（請附上應答訊息列表檔案）</td></tr>
</table>
每個Discord群組都是單獨設置，彼此不會互相干擾<br>
若訊息符合設定條件，bot會回傳設定的訊息內容，若要關閉此功能請將應答列表清空<br>
\assets\answeringMachine\資料夾裡有設定範例<br>
新增/刪除訊息附件檔案須手動於\assets\answeringMachine\(該Discord群組ID)\下放置檔案/刪除<br>
<br><br>

### **新人加入歡迎訊息功能**
<table>
<tr><td>/sendwelcomemsglist</td><td>傳送新人加入歡迎訊息列表檔案</td></tr>
<tr><td>/editwelcomemsglist</td><td>修改新人加入歡迎訊息（請附上歡迎訊息列表檔案）</td></tr>
</table>
每個Discord群組都是單獨設置，彼此不會互相干擾<br>
<br><br>

### **產生連結功能**
<table>
<tr><td>/nh + (車號)</td><td>傳送該nh本子連結</td></tr>
<tr><td>/jm + (車號)</td><td>傳送該JM本子連結</td></tr>
<tr><td>/wn + (車號)</td><td>傳送該wnacg本子連結</td></tr>
<tr><td>/pix + (作品號)</td><td>傳送該pixiv作品連結</td></tr>
<tr><td>/pixu + (作者號)</td><td>傳送該pixiv作者連結</td></tr>
<tr><td>/twiu + (用戶ID)</td><td>傳送該X(twitter)用戶連結</td></tr>
</table>
<br><br>

### **其他功能**
<table>
<tr><td>/help</td><td>查詢指令</td></tr>
<tr><td>/status</td><td>回傳bot狀態</td></tr>
<tr><td>/majorarcana + (訊息)</td><td>根據訊息內容使用大密儀塔羅牌占卜</td></tr>
<tr><td>/majorarcana3 + (訊息)</td><td>根據訊息內容使用三張大密儀塔羅牌占卜</td></tr>
</table>

<img src="https://i.imgur.com/nD9AF8u.png"><br>
<img src="https://i.imgur.com/ttdxmLe.png"><br><br>
<img src="https://i.imgur.com/gyIRSVa.png"><br><br>

***
## 使用了以下非標準 Python package
<table>
<tr><td>項目</td><td>版本</td><td>授權</td></tr>
<tr><td>discord.py[voice]</td><td>2.4.0</td><td>MIT License</td></tr>
<tr><td>AioCAI</td><td>1.0.1</td><td>MIT License</td></tr>
<tr><td>fake-useragent</td><td>2.2.0</td><td>Apache License Version 2.0</td></tr>
<tr><td>gdown</td><td>5.2.0</td><td>MIT License</td></tr>
<tr><td>openpyxl</td><td>3.1.2</td><td>MIT License</td></tr>
<tr><td>PyCharacterAI</td><td>2.2.47</td><td>MIT License</td></tr>
<tr><td>PyMySQL</td><td>1.1.1</td><td>MIT License</td></tr>
<tr><td>Requests</td><td>2.31.0</td><td>Apache License Version 2.0</td></tr>
<tr><td>yt-dlp</td><td>2025.6.25</td><td>The Unlicense</td></tr>
</table>

***
## 已知問題
- 更新版本時，Discord裡的斜線指令無法自動更新，須重邀一遍bot加入群組才行(不須踢出bot)，雖然網路上有許多自動、手動、分群組更新的方法，但這裡測試後發現全部無法使用，所以更新程式版本也需一併重邀bot
- 無法播放「<a href="https://www.youtube.com/watch?v=rPJz3syNbtE">https://www.youtube.com/watch?v=rPJz3syNbtE</a>」，且會造成程式錯誤
- 本專案完全由本人於閒暇時間維護，更新較慢，敬請見諒！