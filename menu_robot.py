from telebot import types
from API_TG import bot  
from db_tg import reset_user


def support(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton(
            text="Написать в поддержку",
            url="https://t.me/Kseniia999"
        )
    )

    bot.send_message(
        message.chat.id,
        "Нажмите кнопку ниже:",
        reply_markup=markup
    )


def faq(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton(
            text="Ответы здесь",
            url="https://t.me/Kseniia999"
        )
    )    

    bot.send_message(
        message.chat.id,
        "Нажмите кнопку ниже:",
        reply_markup=markup
    )


def cancel_handler(message):
    chat_id = message.chat.id

    reset_user(chat_id)

    bot.send_message(
        chat_id,
        "Данные стерты",
        reply_markup=types.ReplyKeyboardRemove()
    )



