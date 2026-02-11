from API_TG import bot
from telebot import types

def create_keyboards(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

    keyboard.add(
        types.KeyboardButton('Запустить/остановить робота'),
        types.KeyboardButton('Частые вопросы'),
        types.KeyboardButton('Поддержка')
    )
    keyboard.add(types.KeyboardButton('Отмена'))

    bot.send_message(
        message.chat.id,
        'Выберите действие: ',
        reply_markup=keyboard
    )   



