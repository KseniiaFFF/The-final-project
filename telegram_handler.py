from API_TG import bot
from db_tg import init_db, reset_user, save_keys, set_robot_running, set_robot_stopped, get_keys
from keyb_robot import create_keyboards, robot_menu
from menu_robot import support, faq, cancel_handler
from strategy import pnl, settings
from telebot import types

BUTTON_HANDLERS = {
    'Робот': robot_menu,
    'Поддержка': support,
    'Частые вопросы': faq,
    'Отмена': cancel_handler,
    'Начать торговлю' : set_robot_running,
    'Остановить торговлю' : set_robot_stopped,
    'Настройки' : settings,
    'PNL' : pnl,
    'Назад' : create_keyboards

}


init_db()

@bot.message_handler(commands=["start"])
def start(message):
    chat_id = message.chat.id

    if get_keys(chat_id):
        bot.send_message(chat_id, "✅ Ключи уже сохранены.")
        create_keyboards(message)
    else:
        bot.send_message(chat_id, "🔐 Введите API Binance")
        bot.register_next_step_handler(message, get_api_key)

def get_api_key(message):
    chat_id = message.chat.id
    text = message.text.strip()

    if text == "❌ Отмена":
        reset_user(chat_id)
        bot.send_message(chat_id, "❌ Ввод отменён",
                         reply_markup=types.ReplyKeyboardRemove())
        return

    save_keys(chat_id, api_key=text)

    bot.send_message(chat_id, "Введите SECRET KEY")
    bot.register_next_step_handler(message, get_secret_key)

 
def get_secret_key(message):
    chat_id = message.chat.id
    text = message.text.strip()

    if text == "❌ Отмена":
        reset_user(chat_id)
        bot.send_message(chat_id, "❌ Ввод отменён",
                         reply_markup=types.ReplyKeyboardRemove())
        return

    save_keys(chat_id, secret_key=text)

    bot.send_message(chat_id, "✅ Ключи сохранены. Готов к торговле.")
    create_keyboards(message)


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


bot.polling()    

