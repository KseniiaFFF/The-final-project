from API_TG import bot
from db_tg import init_db
from db_tg import reset_user
from db_tg import save_keys
from db_tg import get_keys
from keyb_robot import create_keyboards
from menu_robot import support, faq, cancel_handler, state_bot
from telebot import types

BUTTON_HANDLERS = {
    'Запустить/остановить робота': state_bot,
    'Поддержка': support,
    'Частые вопросы': faq,
    'Отмена': cancel_handler
}


# init_db()

@bot.message_handler(commands=["start"])
def start(message):
    chat_id = message.chat.id

    reset_user(chat_id)

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
 


def trade(chat_id):
    keys = get_keys(chat_id)

    if not keys or None in keys:
        bot.send_message(chat_id, "❌ Ключи не заданы. Нажмите /start")
        return

    api_key, secret_key = keys

    print(api_key, secret_key)  


bot.polling()    

