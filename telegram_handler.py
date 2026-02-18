
import logging
from log_settings import set

from API_TG import bot
from db_tg import init_db, reset_user, save_keys, set_robot_running, set_robot_stopped, get_keys
from keyb_robot import create_keyboards, robot_menu
from menu_robot import support, faq, cancel_handler
from strategy import pnl, settings
from telebot import types
from binance_info import start_scanner
from check_user_api import validate_all



init_db()
user_temp = {}
set()
logger = logging.getLogger(__name__)


def get_user_data(message):
    return message.chat.id, message.chat.username

@bot.message_handler(commands=["start"])
def start(message):
    chat_id, user_name = get_user_data(message)

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

    
def ask_api(message):
    msg = bot.send_message(message.chat.id, "Введите API Binance", reply_markup=cancel_keyboard())
    bot.register_next_step_handler(msg, get_api_key)


def edit_api_key(message):
    msg = bot.send_message(message.chat.id, "🔐 Введите новый API KEY", reply_markup=cancel_keyboard())
    bot.register_next_step_handler(msg, get_api_key)
       

def get_api_key(message):
    chat_id, user_name = get_user_data(message)
    text = message.text.strip()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton('Стоп'))

    if text == "Отмена":
        bot.clear_step_handler_by_chat_id(chat_id)
        logging.info(f'Exit get_api_key {message.text} | user_name -> {user_name}, chat_id -> {message.chat.id}')
        reset_user(chat_id)
        bot.send_message(chat_id, "❌ Ввод отменён", reply_markup=types.ReplyKeyboardRemove())
        
        create_keyboards(message)
        return
    
    user_temp[chat_id] = {"api_key": text}

    msg = bot.send_message(chat_id, "Введите SECRET KEY", reply_markup=cancel_keyboard())
    bot.register_next_step_handler(msg, get_secret_key)

 
def get_secret_key(message):
    chat_id, user_name = get_user_data(message)
    text = message.text.strip()

    if text == "Отмена":
        bot.clear_step_handler_by_chat_id(chat_id)
        logging.info(f'Exit get_secret_key {message.text} | user_name -> {user_name}, chat_id -> {message.chat.id}')
        reset_user(chat_id)
        bot.send_message(chat_id, "❌ Ввод отменён", reply_markup=types.ReplyKeyboardRemove())
        
        create_keyboards(message)
        return
    
    secret = text
    
    api_key = user_temp.get(chat_id, {}).get("api_key")

    if not api_key:
        bot.send_message(chat_id, "Ошибка. Введите API заново.")
        logging.warning(f'Ошибка. Введите API заново {message.text} | user_name -> {user_name}, chat_id -> {message.chat.id}')
        return

    results = validate_all(api_key, secret)

    if not any(r[0] for r in results.values()):
        bot.send_message(chat_id, "❌ Ключи неверные или нет доступа")
        logging.warning(f'Ключи неверные или нет доступа {message.text} | user_name -> {user_name}, chat_id -> {message.chat.id}')
        return

    save_keys(chat_id, api_key=api_key, secret_key=secret)

    bot.send_message(chat_id, "✅ Ключи сохранены. Готов к торговле.")
    logging.info(f'Ключи сохранены {'-'} | user_name -> {user_name}, chat_id -> {message.chat.id}')
    create_keyboards(message)

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
    'Продолжить без API(только сканнер)' : create_keyboards
}    


@bot.message_handler(content_types=['text'])
def router(message):
    text = message.text.strip()

    handler = BUTTON_HANDLERS.get(text)

    if handler:
        handler(message)
    else:
        bot.send_message(
            message.chat.id,
            "Используйте кнопки меню 👇"
        )


def cancel_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton("Отмена"))
    return keyboard


bot.polling()    

