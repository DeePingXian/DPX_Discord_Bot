from core.classes import Cog_Extension
import pymysql

class MySQL(Cog_Extension):

    def test(self):
        try:
            MySQLConnection = pymysql.connect(**self.settings["MySQLSettings"])
            with MySQLConnection.cursor() as cursor:
                command = "CREATE DATABASE IF NOT EXISTS discord_test"
                cursor.execute(command)
                command = "CREATE TABLE IF NOT EXISTS discord_test.test (test BOOLEAN NOT NULL) ENGINE = InnoDB;"
                cursor.execute(command)
                command = "INSERT INTO discord_test.test (test) VALUES (1);"
                cursor.execute(command)
                MySQLConnection.commit()
                command = "TRUNCATE discord_test.test"
                cursor.execute(command)
                command = "DROP TABLE discord_test.test"
                cursor.execute(command)
                MySQLConnection.commit()
                command = "DROP DATABASE discord_test"
                cursor.execute(command)
                MySQLConnection.commit()
            MySQLConnection.close()
        except:
            return False
        else:
            return True

    def init(self):
        MySQLConnection = pymysql.connect(**self.settings["MySQLSettings"])
        with MySQLConnection.cursor() as cursor:
            command = f"CREATE DATABASE IF NOT EXISTS discord_status"
            cursor.execute(command)
            command = f"CREATE TABLE IF NOT EXISTS discord_status.guilds (id TEXT NOT NULL , name TEXT NOT NULL ) ENGINE = InnoDB;"
            cursor.execute(command)
            command = f"CREATE TABLE IF NOT EXISTS discord_status.music_guilds (id TEXT NOT NULL , name TEXT NOT NULL ) ENGINE = InnoDB;"
            cursor.execute(command)
        MySQLConnection.close()

    def createDatabase(self , GuildID):
        MySQLConnection = pymysql.connect(**self.settings["MySQLSettings"])
        with MySQLConnection.cursor() as cursor:
            command = f"CREATE DATABASE IF NOT EXISTS discord_{GuildID}"
            cursor.execute(command)
        MySQLConnection.close()
        
    def updateToken(self , guildID):
        from uuid import uuid4
        tokens = []
        MySQLConnection = pymysql.connect(**self.settings["MySQLSettings"])
        with MySQLConnection.cursor() as cursor:
            command = f"CREATE TABLE IF NOT EXISTS discord_status.tokens (guild_id TEXT NOT NULL , token TEXT NOT NULL) ENGINE = InnoDB;"
            cursor.execute(command)
            command = f"SELECT * FROM discord_status.tokens"
            cursor.execute(command)
            old_tokens = cursor.fetchall()
            tokens , guilds = [] , []
            for i in old_tokens:
                guilds.append(i[0])
                tokens.append(i[1])
            token = str(uuid4())[:8]
            while token in old_tokens:
                token = str(uuid4())[:8]
            if str(guildID) in guilds:
                command = f"UPDATE discord_status.tokens SET `token` = '{token}' WHERE `guild_id` = '{guildID}';"
            else:
                command = f"INSERT INTO discord_status.tokens (guild_id , token) VALUES ('{guildID}' , '{token}');"
            cursor.execute(command)
            MySQLConnection.commit()
        MySQLConnection.close()

    def updateAllToken(self):
        from uuid import uuid4
        tokens = []
        MySQLConnection = pymysql.connect(**self.settings["MySQLSettings"])
        with MySQLConnection.cursor() as cursor:
            command = f"CREATE TABLE IF NOT EXISTS discord_status.tokens (guild_id TEXT NOT NULL , token TEXT NOT NULL) ENGINE = InnoDB;"
            cursor.execute(command)
            command = f"SELECT id FROM discord_status.guilds"
            cursor.execute(command)
            guildsID = cursor.fetchall()
            command = f"SELECT token FROM discord_status.tokens"
            cursor.execute(command)
            oldTokens = cursor.fetchall()
            for _ in guildsID:
                token = str(uuid4())[:8]
                while token in tokens or (token,) in oldTokens:
                    token = str(uuid4())[:8]
                tokens.append(token)
            command = f"TRUNCATE discord_status.tokens"
            cursor.execute(command)
            count = 0
            for i in guildsID:
                command = f"INSERT INTO discord_status.tokens (guild_id , token) VALUES ('{i[0]}' , '{tokens[count]}');"
                cursor.execute(command)
                MySQLConnection.commit()
                count += 1
        MySQLConnection.close()

    def getToken(self , guildID):
        MySQLConnection = pymysql.connect(**self.settings["MySQLSettings"])
        with MySQLConnection.cursor() as cursor:
            command = f"SELECT token FROM discord_status.tokens WHERE `guild_id` = '{guildID}';"
            cursor.execute(command)
            token = cursor.fetchall()
        MySQLConnection.close()
        return token[0][0]
        
    #聊天功能相關

    def createCharacterAITable(self , guildID):
        MySQLConnection = pymysql.connect(**self.settings["MySQLSettings"])
        with MySQLConnection.cursor() as cursor:
            command = f"CREATE TABLE IF NOT EXISTS discord_{guildID}.characterai (`discord_bot_id` TEXT NOT NULL , `chat_info_id` TEXT NOT NULL ) ENGINE = InnoDB;"
            cursor.execute(command)

    def setCharacterAIChatID(self , guildID , chatInfoID):
        MySQLConnection = pymysql.connect(**self.settings["MySQLSettings"])
        with MySQLConnection.cursor() as cursor:
            command = f"SELECT `chat_info_id` FROM discord_{guildID}.characterai WHERE `discord_bot_id` = '{self.bot.user.id}';"
            cursor.execute(command)
            chatInfoID_ = cursor.fetchall()
            if chatInfoID_ != ():
                command = f"UPDATE discord_{guildID}.characterai SET `chat_info_id` = '{chatInfoID}' WHERE `discord_bot_id` = '{self.bot.user.id}';"
            else:
                command = f"INSERT INTO discord_{guildID}.characterai (`discord_bot_id` , `chat_info_id`) VALUES ('{self.bot.user.id}' , '{chatInfoID}');"
            cursor.execute(command)
            MySQLConnection.commit()
        
    def getCharacterAIChatID(self , guildID):
        MySQLConnection = pymysql.connect(**self.settings["MySQLSettings"])
        with MySQLConnection.cursor() as cursor:
            command = f"SELECT `chat_info_id` FROM discord_{guildID}.characterai WHERE `discord_bot_id` = '{self.bot.user.id}';"
            cursor.execute(command)
            id = cursor.fetchall()
        MySQLConnection.close()
        if id == ():
            return None
        else:
            return id[0][0]

    #訊息歷史紀錄功能相關

    def putMessageLog(self , message , message_before , deleted_at , type):
        MySQLConnection = pymysql.connect(**self.settings["MySQLSettings"])
        with MySQLConnection.cursor() as cursor:
            command = f"SELECT * FROM discord_status.guilds"
            cursor.execute(command)
            guilds = cursor.fetchall()
            if not (str(message.guild.id) , str(message.guild)) in guilds:
                GuildExists = False
                for i in guilds:        #檢查guild是否更名
                    if str(message.guild.id) == i[0]:
                        GuildExists = True
                if GuildExists:
                    command = f"UPDATE discord_status.guilds SET `name` = '{message.guild}' WHERE `id` = '{message.guild.id}';"
                else:
                    command = f"INSERT INTO discord_status.guilds (id , name) VALUES ('{message.guild.id}' , '{message.guild}');"
                    self.updateToken(message.guild.id)       #為沒有token的guild產生token
                cursor.execute(command)
                MySQLConnection.commit()
            command = f"CREATE DATABASE IF NOT EXISTS discord_{message.guild.id}_messagelog"
            cursor.execute(command)
            try:
                command = f"SELECT * FROM discord_{message.guild.id}_messagelog.channels"
                cursor.execute(command)
                channels = cursor.fetchall()
                if not (str(message.channel.id) , str(message.channel)) in channels:
                    ChannelExists = False
                    for i in channels:
                        if str(message.channel.id) == i[0]:
                            ChannelExists = True
                    if ChannelExists:
                        command = f"UPDATE discord_{message.guild.id}_messagelog.channels SET `name` = '{message.channel}' WHERE `id` = '{message.channel.id}';"
                    else:
                        command = f"INSERT INTO discord_{message.guild.id}_messagelog.channels (id , name) VALUES ('{message.channel.id}' , '{message.channel}');"
                    cursor.execute(command)
                    MySQLConnection.commit()
            except:
                command = f"CREATE TABLE IF NOT EXISTS discord_{message.guild.id}_messagelog.channels ( id TEXT NOT NULL , name TEXT NOT NULL ) ENGINE = InnoDB;"
                cursor.execute(command)
                command = f"INSERT INTO discord_{message.guild.id}_messagelog.channels (id , name) VALUES ('{message.channel.id}' , '{message.channel}');"
                cursor.execute(command)
                MySQLConnection.commit()
            command = f"CREATE TABLE IF NOT EXISTS discord_{message.guild.id}_messagelog.{message.channel.id} ( author TEXT NOT NULL , author_id TEXT NOT NULL , content TEXT NOT NULL , editted_content TEXT NOT NULL , attachment TEXT NOT NULL , sent_at DATETIME NOT NULL , editted_at DATETIME NOT NULL , type TINYINT UNSIGNED NOT NULL) ENGINE = InnoDB;"
            cursor.execute(command)            
            command = f"SELECT * FROM discord_{message.guild.id}_messagelog.{message.channel.id}"
            cursor.execute(command)
            MesLog = cursor.fetchall()
            try:
                attachment = message.attachments[0].url
            except:
                attachment = ''
            if len(MesLog) >= self.settings["maxMessagesSaved"]:
                command = f"DELETE FROM discord_{message.guild.id}_messagelog.{message.channel.id} limit 1"
                cursor.execute(command)
                MySQLConnection.commit()
            message.content = pymysql.converters.escape_string(message.content)
            if type == 0:
                command = f"INSERT INTO discord_{message.guild.id}_messagelog.{message.channel.id} (author , author_id ,  content , editted_content , attachment , sent_at , editted_at , type) VALUES ('{message.author}' , '{message.author.id}' , '{message.content}' , '' , '{attachment}' , '{message.created_at.strftime('%Y-%m-%d %H:%M:%S')}' , '0000-00-00 00:00:00' , 0);"
            elif type == 1:
                message_before.content = pymysql.converters.escape_string(message_before.content)
                command = f"INSERT INTO discord_{message.guild.id}_messagelog.{message.channel.id} (author , author_id ,  content , editted_content , attachment , sent_at , editted_at , type) VALUES ('{message.author}' , '{message.author.id}' , '{message_before.content}' , '{message.content}' , '{attachment}' , '{message.created_at.strftime('%Y-%m-%d %H:%M:%S')}' , '{message.edited_at.strftime('%Y-%m-%d %H:%M:%S')}' , 1);"
            elif type == 2:
                command = f"INSERT INTO discord_{message.guild.id}_messagelog.{message.channel.id} (author , author_id ,  content , editted_content , attachment , sent_at , editted_at , type) VALUES ('{message.author}' , '{message.author.id}' , '{message.content}' , '' , '{attachment}' , '{message.created_at.strftime('%Y-%m-%d %H:%M:%S')}' , '{deleted_at}' , 2);"
            cursor.execute(command)
            MySQLConnection.commit()
        MySQLConnection.close()
        
    def getMessageLog(self , guildID , channelID , msgType):
        MySQLConnection = pymysql.connect(**self.settings["MySQLSettings"])
        with MySQLConnection.cursor() as cursor:
            getMsgType = 0
            if type(msgType) == int:
                getMsgType = msgType
            elif type(msgType) == list or type(msgType) == tuple:
                getMsgType = ""
                for i in msgType:
                    getMsgType += f"{i}"
                    if i != msgType[-1]:
                        getMsgType += f" OR type = "
            try:
                command = f"SELECT * FROM discord_{guildID}_messagelog.{channelID} WHERE type = {getMsgType}"
                cursor.execute(command)
                messages = cursor.fetchall()
            except:
                raise Exception("Channel message log not found.")
        MySQLConnection.close()
        return messages

    #音樂機器人功能相關

    def createMusicTable(self , GuildID):
        MySQLConnection = pymysql.connect(**self.settings["MySQLSettings"])
        with MySQLConnection.cursor() as cursor:
            command = f"SELECT * FROM discord_status.guilds"
            cursor.execute(command)
            GuildName = str(self.bot.get_guild(GuildID))
            guilds = cursor.fetchall()
            if not (str(GuildID) , GuildName) in guilds:
                GuildExists = False
                for i in guilds:        #檢查guild是否更名
                    if str(GuildID) == i[0]:
                        GuildExists = True
                if GuildExists:
                    command = f"UPDATE discord_status.guilds SET `name` = '{GuildName}' WHERE `id` = '{GuildID}';"
                else:
                    command = f"INSERT INTO discord_status.guilds (id , name) VALUES ('{GuildID}' , '{GuildName}');"
                cursor.execute(command)
                MySQLConnection.commit()
            command = f"CREATE TABLE IF NOT EXISTS discord_{GuildID}.music_queue ( id INT UNSIGNED NOT NULL , title TEXT NOT NULL , file_name TEXT NOT NULL , duration TIME NOT NULL , url TEXT NOT NULL , audio_url TEXT NOT NULL , thumbnail_url TEXT NOT NULL , file_size BIGINT UNSIGNED NOT NULL , type TINYINT UNSIGNED NOT NULL ) ENGINE = InnoDB;"
            cursor.execute(command)
            command = f"CREATE TABLE IF NOT EXISTS discord_{GuildID}.music_status (playlist_loop BOOLEAN NOT NULL , playlist_loop_to_id INT UNSIGNED NOT NULL , single_loop BOOLEAN NOT NULL ) ENGINE = InnoDB;"
            cursor.execute(command)
            command = f"INSERT INTO discord_{GuildID}.music_status (playlist_loop , playlist_loop_to_id , single_loop) VALUES (0 , 0 , 0);"
            cursor.execute(command)
            MySQLConnection.commit()
            command = f"INSERT INTO discord_status.music_guilds (id, name) VALUES ('{GuildID}', '{self.bot.get_guild(GuildID)}');"
            cursor.execute(command)
            MySQLConnection.commit()
        MySQLConnection.close()

    def getMusicQueue(self , GuildID):
        MySQLConnection = pymysql.connect(**self.settings["MySQLSettings"])
        with MySQLConnection.cursor() as cursor:
            command = f"SELECT * FROM discord_{GuildID}.music_queue"
            cursor.execute(command)
            MusicQueue = cursor.fetchall()
        MySQLConnection.close()
        return MusicQueue

    def putMusic(self , GuildID , music):
        MySQLConnection = pymysql.connect(**self.settings["MySQLSettings"])
        with MySQLConnection.cursor() as cursor:
            command = f"SELECT * FROM discord_{GuildID}.music_queue"
            cursor.execute(command)
            MusicQueue = cursor.fetchall()
            music.title = pymysql.converters.escape_string(music.title)
            music.audio_url = pymysql.converters.escape_string(music.audio_url)
            music.file_name = pymysql.converters.escape_string(music.file_name)
            if MusicQueue == ():
                command = f"INSERT INTO discord_{GuildID}.music_queue (id , title , file_name , duration , url , audio_url , thumbnail_url , file_size , type) VALUES (0 , '{music.title}' , '{music.file_name}' , '{music.duration}' , '{music.url}' , '{music.audio_url}' , '{music.thumbnail_url}' , '{music.file_size}' , '{music.type}');"
            else:
                command = f"INSERT INTO discord_{GuildID}.music_queue (id , title , file_name , duration , url , audio_url , thumbnail_url , file_size , type) VALUES ({int(MusicQueue[-1][0])+1} , '{music.title}' , '{music.file_name}' , '{music.duration}' , '{music.url}' , '{music.audio_url}' , '{music.thumbnail_url}' , '{music.file_size}' , '{music.type}');"
            cursor.execute(command)
            MySQLConnection.commit()
        MySQLConnection.close()

    def getMusicStatus(self , GuildID):
        MySQLConnection = pymysql.connect(**self.settings["MySQLSettings"])
        with MySQLConnection.cursor() as cursor:
            command = f"SELECT * FROM discord_{GuildID}.music_status"
            cursor.execute(command)
            MusicStatus = cursor.fetchall()
        MySQLConnection.close()
        return MusicStatus

    def getMusicQueueLen(self , GuildID):
        MySQLConnection = pymysql.connect(**self.settings["MySQLSettings"])
        with MySQLConnection.cursor() as cursor:
            command = f"SELECT * FROM discord_{GuildID}.music_queue"
            cursor.execute(command)
            MusicQueue = cursor.fetchall()
        MySQLConnection.close()
        return len(MusicQueue)

    def getMusic(self , GuildID):
        class MusicDetail:
            def __init__(self , url):
                self.title = ''
                self.file_name = ''
                self.duration = ''
                self.url = url
                self.audio_url = ''
                self.thumbnail_url = ''
                self.file_size = 0
                self.type = 0
        MySQLConnection = pymysql.connect(**self.settings["MySQLSettings"])
        with MySQLConnection.cursor() as cursor:
            command = f"SELECT * FROM discord_{GuildID}.music_queue"
            cursor.execute(command)
            MusicQueue = cursor.fetchall()
        MySQLConnection.close()
        if MusicQueue == ():
            return None
        else:
            music1 = MusicQueue[0]
            music = MusicDetail(music1[4])
            music.title = music1[1]
            music.file_name = music1[2]
            music.duration = str(music1[3])
            music.audio_url = music1[5]
            music.thumbnail_url = music1[6]
            music.file_size = music1[7]
            music.type = music1[8]
            return music

    def popMusic(self , GuildID):
        MySQLConnection = pymysql.connect(**self.settings["MySQLSettings"])
        with MySQLConnection.cursor() as cursor:
            command = f"DELETE FROM discord_{GuildID}.music_queue limit 1"
            cursor.execute(command)
            MySQLConnection.commit()
        MySQLConnection.close()

    def setSingleLoop(self , GuildID , SingleLoop):
        MySQLConnection = pymysql.connect(**self.settings["MySQLSettings"])
        with MySQLConnection.cursor() as cursor:
            if SingleLoop:
                command = f"UPDATE discord_{GuildID}.music_status SET single_loop = 1"
            else:
                command = f"UPDATE discord_{GuildID}.music_status SET single_loop = 0"
            cursor.execute(command)
            MySQLConnection.commit()
        MySQLConnection.close()

    def getLoop(self , GuildID):
        MySQLConnection = pymysql.connect(**self.settings["MySQLSettings"])
        with MySQLConnection.cursor() as cursor:
            command = f"SELECT * FROM discord_{GuildID}.music_status"
            cursor.execute(command)
            loop = cursor.fetchall()
        MySQLConnection.close()
        loop = loop[0][2]
        if loop == 1:
            return True
        else:
            return False

    def cleanMusicTable(self , GuildID):
        MySQLConnection = pymysql.connect(**self.settings["MySQLSettings"])
        with MySQLConnection.cursor() as cursor:
            try:
                command = f"DELETE FROM discord_status.music_guilds WHERE id = {GuildID}"
                cursor.execute(command)
                MySQLConnection.commit()
            except:
                pass
            try:
                command = f"TRUNCATE discord_{GuildID}.music_queue"
                cursor.execute(command)
            except:
                pass
            try:
                command = f"TRUNCATE discord_{GuildID}.music_status"
                cursor.execute(command)
            except:
                pass
        MySQLConnection.close()

    def cleanAllMusicTable(self):
        MySQLConnection = pymysql.connect(**self.settings["MySQLSettings"])
        with MySQLConnection.cursor() as cursor:
            command = "SELECT * FROM discord_status.music_guilds"
            cursor.execute(command)
            music_guilds = cursor.fetchall()
            command = "TRUNCATE discord_status.music_guilds"
            cursor.execute(command)
            for i in music_guilds:
                try:
                    command = f"TRUNCATE discord_{i[0]}.music_queue"
                    cursor.execute(command)
                except:
                    pass
                try:
                    command = f"TRUNCATE discord_{i[0]}.music_status"
                    cursor.execute(command)
                except:
                    pass
            del music_guilds
        MySQLConnection.close()

async def setup(bot):
    await bot.add_cog(MySQL(bot))