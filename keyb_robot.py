from API_TG import bot
from telebot import types
from db_tg import is_robot_active

def create_keyboards(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

    keyboard.add(
        types.KeyboardButton('Робот'),
        types.KeyboardButton('Частые вопросы'),
        types.KeyboardButton('Поддержка'),
        types.KeyboardButton('Редактировать ключи')
    )
    keyboard.add(types.KeyboardButton('Стоп'))

    bot.send_message(
        message.chat.id,
        'Выберите действие: ',
        reply_markup=keyboard
    )   


def robot_menu(message):

    chat_id = message.chat.id
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

    if is_robot_active(chat_id):
        keyboard.add(types.KeyboardButton('Остановить торговлю'))
    else:
        keyboard.add(types.KeyboardButton('Начать торговлю'))

    keyboard.add(
        types.KeyboardButton('Настройки'),
        types.KeyboardButton('PNL'),
        types.KeyboardButton('Запустить сканнер')
    )
    keyboard.add(types.KeyboardButton('Назад'))

    bot.send_message(chat_id, 'Меню робота:', reply_markup=keyboard)



