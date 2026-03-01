from API_TG import bot
from telebot import types
from db_tg import is_robot_active

#создание главного меню
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

#создание меню Робот ->
def robot_menu(message):

    from binance_info import active_scanners
    chat_id = message.chat.id
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

    if is_robot_active(chat_id):
        keyboard.add(types.KeyboardButton('Остановить торговлю'))
    else:
        keyboard.add(types.KeyboardButton('Начать торговлю'))

    if active_scanners.get(chat_id, False):
        keyboard.add(types.KeyboardButton('Остановить сканер'))
    else:
        keyboard.add(types.KeyboardButton('Запустить сканер'))

    keyboard.add(
        types.KeyboardButton('Настройки'),
        types.KeyboardButton('PNL')
    )
    keyboard.add(types.KeyboardButton('Назад'))

    status_text = "Сканер: " + ("активен 🟢" if active_scanners.get(chat_id, False) else "выключен ⚪")
    bot.send_message(chat_id, f'Меню робота:\n\n{status_text}', reply_markup=keyboard)







