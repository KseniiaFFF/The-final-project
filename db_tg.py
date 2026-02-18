import sqlite3
from API_TG import bot
import logging

logger = logging.getLogger(__name__)

DB_NAME = "users.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    with get_connection() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            chat_id INTEGER PRIMARY KEY,
            api_key TEXT,
            secret_key TEXT,
            robot_status TEXT
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

    logger.info(f'Команда "Стоп", данные стерты | chat_id = {chat_id}')     


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
        result = cursor.fetchone()

        if result and result[0] and result[1]:
            return True

        return False

def set_robot_running(message):
    chat_id = message.chat.id

    with get_connection() as conn:
        conn.execute("""
        UPDATE users
        SET robot_status = 'running'
        WHERE chat_id = ?
        """, (chat_id,))

    logger.info(f'Торговля запущена| user_name = {message.chat.username}, chat_id = {chat_id}')    

    bot.send_message(
            message.chat.id,
            "Уже в поиске сделок 🫡"
        )    

def set_robot_stopped(message):
    chat_id = message.chat.id

    with get_connection() as conn:
        conn.execute("""
        UPDATE users
        SET robot_status = 'stopped'
        WHERE chat_id = ?
        """, (chat_id,))

    logger.info(f'Торговля остановлена| user_name = {message.chat.username}, chat_id = {chat_id}')       

    bot.send_message(
            message.chat.id,
            "Торговля остановлена 🫡"
        )     

def is_robot_active(chat_id):
    with get_connection() as conn:
        cursor = conn.execute("""
        SELECT robot_status FROM users
        WHERE chat_id = ?
        """, (chat_id,))
        result = cursor.fetchone()

        if result and result[0] == 'running':
            return True
        return False
