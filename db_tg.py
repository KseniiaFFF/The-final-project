import sqlite3

DB_NAME = "users.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    with get_connection() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            chat_id INTEGER PRIMARY KEY,
            api_key TEXT,
            secret_key TEXT
        )
        """)

def reset_user(chat_id):
    with get_connection() as conn:
        conn.execute("""
        UPDATE users
        SET api_key = NULL,
            secret_key = NULL
        WHERE chat_id = ?
        """, (chat_id,))



def save_keys(chat_id, api_key=None, secret_key=None):
    with get_connection() as conn:
        conn.execute("""
        INSERT INTO users (chat_id, api_key, secret_key)
        VALUES (?, ?, ?)
        ON CONFLICT(chat_id)
        DO UPDATE SET
            api_key = COALESCE(?, api_key),
            secret_key = COALESCE(?, secret_key)
        """, (chat_id, api_key, secret_key,
              api_key, secret_key))



def get_keys(chat_id):
    with get_connection() as conn:
        cursor = conn.execute("""
        SELECT api_key, secret_key
        FROM users
        WHERE chat_id = ?
        """, (chat_id,))
        return cursor.fetchone()
