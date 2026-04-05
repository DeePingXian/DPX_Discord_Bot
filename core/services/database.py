from psycopg2 import pool
import logging
import json

class DatabaseService:
    """PostgreSQL Database Management Service"""
    
    def __init__(self, db_url):
        self.logger = logging.getLogger("Database")
        try:
            self.pool = pool.SimpleConnectionPool(1, 10, db_url)
            self._ensure_schema()
        except Exception as e:
            self.logger.critical(f"Failed to establish database connection pool: {e}")
            raise

    def _ensure_schema(self):
        """Verify and initialize database schema"""
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cursor:
                # Guild Configuration Table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS guild_configs (
                        guild_id BIGINT PRIMARY KEY,
                        welcome_config JSONB DEFAULT '{}'::jsonb,
                        answering_config JSONB DEFAULT '[]'::jsonb,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)

                # Global Message Logs Table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS message_logs (
                        id SERIAL PRIMARY KEY,
                        guild_id BIGINT NOT NULL,
                        channel_id BIGINT NOT NULL,
                        author_id BIGINT NOT NULL,
                        author_name VARCHAR(100),
                        content TEXT,
                        content_old TEXT,
                        attachment_url TEXT,
                        message_type SMALLINT DEFAULT 0, -- 0:Original, 1:Edited, 2:Deleted
                        sent_at TIMESTAMP NOT NULL,
                        recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                    CREATE INDEX IF NOT EXISTS idx_msg_channel ON message_logs(channel_id);
                    CREATE INDEX IF NOT EXISTS idx_msg_guild ON message_logs(guild_id);
                """)

                # File Registry for S3 Deduplication
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS file_registry (
                        file_hash VARCHAR(64) PRIMARY KEY,
                        s3_key TEXT NOT NULL,
                        file_size BIGINT,
                        mime_type VARCHAR(50),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                conn.commit()
                self.logger.info("Database schema verification completed.")
        except Exception as e:
            self.logger.error(f"Schema verification failed: {e}")
            conn.rollback()
            raise
        finally:
            self.pool.putconn(conn)

    def execute(self, query, params=None):
        """Execute a write operation"""
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                conn.commit()
        except Exception as e:
            self.logger.error(f"Database execution error: {e}")
            conn.rollback()
            raise
        finally:
            self.pool.putconn(conn)

    def fetch_all(self, query, params=None):
        """Execute a query operation"""
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()
        except Exception as e:
            self.logger.error(f"Database fetch_all error: {e}")
            raise
        finally:
            self.pool.putconn(conn)

    def fetch_one(self, query, params=None):
        """Execute a query operation and return one result"""
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchone()
        except Exception as e:
            self.logger.error(f"Database fetch_one error: {e}")
            raise
        finally:
            self.pool.putconn(conn)

    # --- Guild Configuration Methods ---

    def get_guild_config(self, guild_id):
        """Retrieve configurations for a specific guild"""
        query = "SELECT guild_id, welcome_config, answering_config FROM guild_configs WHERE guild_id = %s"
        return self.fetch_one(query, (guild_id,))

    def update_answering_config(self, guild_id, config_list):
        """Update answering rules for a guild"""
        query = """
            INSERT INTO guild_configs (guild_id, answering_config) VALUES (%s, %s)
            ON CONFLICT (guild_id) DO UPDATE SET answering_config = EXCLUDED.answering_config, updated_at = CURRENT_TIMESTAMP
        """
        self.execute(query, (guild_id, json.dumps(config_list)))

    def update_welcome_config(self, guild_id, config_dict):
        """Update welcome message settings for a guild"""
        query = """
            INSERT INTO guild_configs (guild_id, welcome_config) VALUES (%s, %s)
            ON CONFLICT (guild_id) DO UPDATE SET welcome_config = EXCLUDED.welcome_config, updated_at = CURRENT_TIMESTAMP
        """
        self.execute(query, (guild_id, json.dumps(config_dict)))
