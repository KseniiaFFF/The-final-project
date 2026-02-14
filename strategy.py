from API_TG import bot  

def settings(message):
    bot.send_message(
    message.chat.id,
    """Настройки по умолчанию:
Риск на сделку — 0.5%
Дополнительный текст"""
)


def pnl(message):
    pass