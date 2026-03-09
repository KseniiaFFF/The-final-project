import logging

from log_settings import set
from db_tg import set_user_state, get_user_state
from API_TG import bot
from db_tg import init_db, reset_user, save_keys, set_robot_running, set_robot_stopped, get_keys, set_user_risk, set_user_max_leverage, get_user_max_leverage
from keyb_robot import create_keyboards, robot_menu
from menu_robot import support, faq, cancel_handler
from telebot import types
from binance_info import start_scanner, stop_scanner
from check_user_api import validate_all
from config import settings, pnl


#инициализация БД, конфиг логов, временный апи словарь 
init_db()
user_temp = {}
set()
logger = logging.getLogger(__name__)

#переменные ид юзера и имя юзера
def get_user_data(message):
    return message.chat.id, message.chat.username

#запуск робота, фикс состояние юзера,  проверка сохр ключей, первый лог, апи меню
@bot.message_handler(commands=["start"])
def start(message):
    chat_id, user_name = get_user_data(message)
    set_user_state(chat_id, None)

    if get_keys(chat_id):
        bot.send_message(chat_id, "✅ Ключи уже сохранены.")
        create_keyboards(message)

    logger.info(f'commands "start"| user_name = {user_name}, chat_id = {chat_id}')    

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

    keyboard.add(
        types.KeyboardButton("Ввести API(с функцией торговли)"),
        types.KeyboardButton("Продолжить без API(только сканнер)")
    )

    bot.send_message(
        chat_id,
        "Выберите действие:",
        reply_markup=keyboard
    )

#направляет на ввод апи, изм сост юзера    
def ask_api(message):
    msg = bot.send_message(message.chat.id, "Введите API Binance", reply_markup=cancel_keyboard())
    set_user_state(message.chat.id, "waiting_api_key")
    bot.register_next_step_handler(msg, get_api_key)

#редактирование апи
def edit_api_key(message):
    msg = bot.send_message(message.chat.id, "🔐 Введите новый API KEY", reply_markup=cancel_keyboard())
    bot.register_next_step_handler(msg, get_api_key)
       
#получение апи, изм сост юзера
def get_api_key(message):
    chat_id, user_name = get_user_data(message)
    text = message.text.strip()
    # keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

    if text == "Отмена":
        bot.clear_step_handler_by_chat_id(chat_id)
        logging.info(f'Exit get_api_key {message.text} | user_name -> {user_name}, chat_id -> {message.chat.id}')
        reset_user(chat_id)
        bot.send_message(chat_id, "❌ Ввод отменён", reply_markup=types.ReplyKeyboardRemove())
        
        create_keyboards(message)
        return
    
    user_temp[chat_id] = {"api_key": text}

    msg = bot.send_message(chat_id, "Введите SECRET KEY", reply_markup=cancel_keyboard())
    set_user_state(chat_id, "waiting_secret_key")
    bot.register_next_step_handler(msg, get_secret_key)

#получение секретного ключа,  валидация ключей, сохранение ключей
def get_secret_key(message):
    chat_id, user_name = get_user_data(message)
    text = message.text.strip()

    current_state = get_user_state(chat_id)

    if text == "Отмена" or current_state != "waiting_secret_key":
        bot.clear_step_handler_by_chat_id(chat_id)
        logging.info(f'Exit get_secret_key {message.text} | user_name -> {user_name}, chat_id -> {message.chat.id}')
        reset_user(chat_id)
        set_user_state(chat_id, None)
        bot.send_message(chat_id, "❌ Ввод отменён", reply_markup=types.ReplyKeyboardRemove())
        
        create_keyboards(message)
        return
    
    secret = text
    
    api_key = user_temp.get(chat_id, {}).get("api_key")

    if not api_key:
        bot.send_message(chat_id, "Ошибка. Введите API заново.")
        logging.warning(f'Ошибка. Введите API заново {message.text} | user_name -> {user_name}, chat_id -> {message.chat.id}')
        set_user_state(chat_id, None)
        return

    results = validate_all(api_key, secret)

    result = results.get("futures_testnet")
    if not result or not result[0]:
        bot.send_message(chat_id, "❌ Ключи неверные или нет доступа")
        logging.warning(
            f'Ключи неверные или нет доступа {message.text} | '
            f'user_name -> {user_name}, chat_id -> {message.chat.id}'
        )
        return

    save_keys(chat_id, api_key=api_key, secret_key=secret)

    bot.send_message(chat_id, "✅ Ключи сохранены. Готов к торговле.")
    set_user_state(chat_id, None)
    logging.info(f'Ключи сохранены {'-'} | user_name -> {user_name}, chat_id -> {message.chat.id}')
    create_keyboards(message)

#направляет на настройку риска на сделку 
def ask_risk(message):
    msg = bot.send_message(
        message.chat.id,
        "Введите новый риск (0.1–5%)",
        reply_markup=cancel_keyboard()
    )
    bot.register_next_step_handler(msg, process_risk)

#настройка риска на сделку от депозита, записывает риск в таблицу users
def process_risk(message):
    try:
        percent = float(message.text.strip())
        if not 0.1 <= percent <= 5:
            raise ValueError

        val = percent / 100
        set_user_risk(message.chat.id, val)
        bot.send_message(message.chat.id, f"Риск обновлён: {percent}%")
        settings(message)

    except:
        bot.send_message(message.chat.id, "Введите число от 0.1 до 5")
        bot.register_next_step_handler(message, process_risk)

#направляет на функцию изменения макс плеча
def start_change_leverage(message):
    chat_id = message.chat.id
    current_lev = get_user_max_leverage(chat_id)

    msg = bot.send_message(
        chat_id,
        f"Текущее максимальное плечо: {current_lev}x\n\n"
        "Введите новое значение (целое число от 1 до 125)\n"
        "Примеры: 10   20   50",
        reply_markup=cancel_keyboard()
    )

    bot.register_next_step_handler(msg, process_leverage)

#изменение макс плеча
def process_leverage(message):
    chat_id = message.chat.id
    text = message.text.strip()

    if text == "Отмена":
        bot.clear_step_handler_by_chat_id(chat_id)
        bot.send_message(chat_id, "❌ Изменение отменено", reply_markup=types.ReplyKeyboardRemove())
        settings(message)
        return

    try:
        val = int(text)

        if not 1 <= val <= 125:
            raise ValueError

        success = set_user_max_leverage(chat_id, val)

        if success:
            bot.send_message(chat_id, f"✅ Максимальное плечо обновлено: {val}x")
        else:
            bot.send_message(chat_id, "Не удалось сохранить значение. Попробуйте позже.")
            return

        settings(message)

    except ValueError:
        msg = bot.send_message(
            chat_id,
            "Введите целое число от 1 до 125\nПример: 20 или 50"
        )
        bot.register_next_step_handler(msg, process_leverage)

#словарь по кнопкам
BUTTON_HANDLERS = {
    'Робот': robot_menu,
    'Поддержка': support,
    'Частые вопросы': faq,
    'Редактировать ключи' : edit_api_key,
    'Стоп': cancel_handler,
    'Начать торговлю' : set_robot_running,
    'Остановить торговлю' : set_robot_stopped,
    'Настройки' : settings,
    'PNL' : pnl,
    'Назад' : create_keyboards,
    'Отмена' : start,
    'Запустить сканнер' : start_scanner,
    'Ввести API(с функцией торговли)' : ask_api,
    'Запустить сканер'     : start_scanner,
    'Остановить сканер'    : stop_scanner,
    'Продолжить без API(только сканнер)' : create_keyboards,
    'Изменить риск на сделку' : ask_risk,
    'Изменить максимальное плечо' : start_change_leverage
}    

#направление юзера по состоянию и кнопкам
@bot.message_handler(content_types=['text'])
def router(message):
    chat_id = message.chat.id
    state = get_user_state(chat_id)
    text = message.text.strip()

    if state == "waiting_api_key":
        get_api_key(message)
        return

    if state == "waiting_secret_key":
        get_secret_key(message)
        return

    handler = BUTTON_HANDLERS.get(text)

    if handler:
        handler(message)
        set_user_state(chat_id, None)
    else:
        bot.send_message(
            chat_id,
            "Используйте кнопки меню 👇"
        )     

#возвращает одну кнопку "Отмена"
def cancel_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton("Отмена"))
    return keyboard


bot.polling()    

