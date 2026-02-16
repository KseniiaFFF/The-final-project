# Binance Futures Scanner & Trading Bot (Telegram)

Telegram-бот для сканирования рынка Binance Futures + (в разработке) автоматическая торговля по простым сигналам.

Получай уведомления о сильных движениях (≥2% за 3 минуты) и управляй торговым роботом прямо в Telegram.

## Возможности (на текущий момент)

- Сканирование фьючерсных пар USDT с объёмом ≥ $50M
- Уведомления о движении цены ≥ 2% за последние 20 свечей 3m
- Ввод и проверка Binance API-ключей (Spot + Futures)
- Запуск/остановка сканера и "робота" (пока заглушка)
- Простое меню настроек и статистики PNL (в разработке)
- SQLite база для хранения ключей и статусов пользователей

**В планах (roadmap):**
- Реальная торговля по сигналам сканера
- Настраиваемый риск на сделку, плечо, стоп/тейк
- Trailing stop и фильтры пар
- Мультипользовательская поддержка без конфликтов

## Требования

- Python 3.9+
- Telegram Bot Token (получи у @BotFather)
- Binance API Key + Secret (с правами на Futures)

## Установка

1. Клонируй репозиторий
```bash
git clone https://github.com/KseniiaFFF/The-final-project
cd The-final-project
```

2. Создай виртуальное окружение
```bash
python -m venv venv
source venv/bin/activate    # Linux/Mac
venv\Scripts\activate       # Windows
```

3. Установи зависимости
```bash
pip install -r requirements.txt
```

(если файла requirements.txt ещё нет — создай его с содержимым:)
```bash
pyTelegramBotAPI==4.22.1
requests==2.32.3
python-dotenv==1.0.1
```

4. Создай файл API_TG.py в корне проекта
```bash
import telebot
 
TOKEN = "ваш тг токен"
bot = telebot.TeleBot(TOKEN)
```

5. Запусти бота
```bash
python telegram_handler.py
```

## Как пользоваться

- Найди своего бота в Telegram и напиши /start
- Выбери вариант:
- Ввести API (для торговли(в разработке))
- Продолжить без API (только сканнер)

- В меню «Робот» → «Запустить сканнер»
- Получай уведомления о сильных движениях

## Структура проекта
├── API_TG.py              # инициализация бота
├── telegram_handler.py    # основной роутер и обработчики
├── binance_info.py        # сканер рынка + логика уведомлений
├── db_tg.py               # работа с SQLite
├── check_user_api.py      # валидация ключей Binance
├── keyb_robot.py          # клавиатуры
├── menu_robot.py          # поддержка, FAQ, отмена
├── strategy.py            # настройки + PNL (заготовка)
└── users.db               # база данных (git ignore!)

## Roadmap / Что доделать

 Полноценная торговля (открытие/закрытие позиций)
 Настраиваемый порог изменения, интервал, топ-N пар
 Inline-кнопки и более удобное меню
 Логирование + уведомления об ошибках
 Docker + docker-compose для деплоя
 Тестнет-режим Binance
 Статистика и график PNL
