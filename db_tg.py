import sqlite3
import threading
import logging

from API_TG import bot

logger = logging.getLogger(__name__)

DB_NAME = "users.db"

#авт открытие/закрытие соед с DB_NAME
def get_connection():
    return sqlite3.connect(DB_NAME)

#инициализация таблицы users, созд колонок
def init_db():
    with get_connection() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            chat_id INTEGER PRIMARY KEY,
            api_key TEXT,
            secret_key TEXT,
            robot_status TEXT,
            state TEXT DEFAULT NULL,
            risk_per_trade REAL DEFAULT 0.005,      -- 0.5%
            max_leverage INTEGER DEFAULT 20
        )
        """)

        try:
            conn.execute("ALTER TABLE users ADD COLUMN risk_per_trade REAL DEFAULT 0.005")
        except sqlite3.OperationalError:
            pass

        try:
            conn.execute("ALTER TABLE users ADD COLUMN max_leverage REAL DEFAULT 0.005")
        except sqlite3.OperationalError:
            pass

#очищает апи ключи юзера 
def reset_user(chat_id):

    with get_connection() as conn:
        conn.execute("""
        UPDATE users
        SET api_key = NULL,
            secret_key = NULL
        WHERE chat_id = ?
        """, (chat_id,))

    logger.info(f'Команда "Стоп", данные стерты | chat_id = {chat_id}')     

#сохраняет ключи юзера
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


#проверяет сохр ключи по chat_id
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

#обновляет статус робота 'running', если запущена торговля, обновляет меню робота. Запускает торговый поток threading
def set_robot_running(message):
    from keyb_robot import robot_menu
    from strategy import trading_loop
    chat_id = message.chat.id

    if not get_keys(chat_id):
        bot.send_message(chat_id, "Нет API ключей")
        return False

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
    
    
    thread = threading.Thread(
        target=trading_loop,
        args=(chat_id,),
        daemon=True
    )
    thread.start()
    
    robot_menu(message)  

#обновляет статус робота 'stopped', если остановлена торговля, обновляет меню робота
def set_robot_stopped(message):
    from keyb_robot import robot_menu
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
    
    robot_menu(message)  

#проверка статуса робота для данного юзера
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
    
#установка состояния юзера
def set_user_state(chat_id: int, state: str | None):
    try:
        with get_connection() as conn:
            conn.execute("""
                UPDATE users
                SET state = ?
                WHERE chat_id = ?
            """, (state, chat_id))
            conn.commit()
        return True
    except Exception as e:
        logger.exception(f"Ошибка при установке state для {chat_id}: {e}")
        return False

#получение состояния юзера
def get_user_state(chat_id: int) -> str | None:
    try:
        with get_connection() as conn:
            cursor = conn.execute("""
                SELECT state FROM users WHERE chat_id = ?
            """, (chat_id,))
            result = cursor.fetchone()
            return result[0] if result else None
    except Exception as e:
        logger.exception(f"Ошибка при чтении state для {chat_id}: {e}")
        return None    
    
#получение риска для данного юзера(по умолчанию всегда 0.001)
def get_user_risk(chat_id: int) -> float:
    try:
        with get_connection() as conn:
            cursor = conn.execute(
                "SELECT risk_per_trade FROM users WHERE chat_id = ?",
                (chat_id,)
            )
            result = cursor.fetchone()
            return result[0] if result and result[0] is not None else 0.005
    except Exception as e:
        logger.exception(f"Ошибка чтения risk_per_trade {chat_id}")
        return 0.005

#установка риска для данного юзера(по умолчанию всегда 0.001)
def set_user_risk(chat_id: int, value: float):
    if not 0.001 <= value <= 0.05:  
        raise ValueError("Риск должен быть от 0.1% до 5%")
    
    try:
        with get_connection() as conn:
            conn.execute(
                "UPDATE users SET risk_per_trade = ? WHERE chat_id = ?",
                (value, chat_id)
            )
            conn.commit()
        return True
    except Exception as e:
        logger.exception(f"Ошибка сохранения risk_per_trade {chat_id}")
        return False

#получение макс плеча для данного юзера(по умолчанию всегда 20)
def get_user_max_leverage(chat_id: int) -> int:
    try:
        with get_connection() as conn:
            cursor = conn.execute(
                "SELECT max_leverage FROM users WHERE chat_id = ?",
                (chat_id,)
            )
            result = cursor.fetchone()
            return result[0] if result and result[0] is not None else 20
    except Exception as e:
        logger.exception(f"Ошибка чтения max_leverage {chat_id}")
        return 20

#установка макс плеча для данного юзера(по умолчанию всегда 20)
def set_user_max_leverage(chat_id: int, value: int):
    if not 1 <= value <= 125:
        raise ValueError("Макс. плечо должно быть от 1 до 125")
    
    try:
        with get_connection() as conn:
            conn.execute(
                "UPDATE users SET max_leverage = ? WHERE chat_id = ?",
                (value, chat_id)
            )
            conn.commit()
        return True
    except Exception as e:
        logger.exception(f"Ошибка сохранения max_leverage {chat_id}")
        return False
