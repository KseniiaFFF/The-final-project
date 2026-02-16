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

```text
binance-futures-bot/
├─ API_TG.py               # инициализация бота
├─ telegram_handler.py     # основной роутер и обработчики
├─ binance_info.py         # сканер рынка + логика уведомлений
├─ db_tg.py                # работа с SQLite
├─ check_user_api.py       # валидация ключей Binance
├─ keyb_robot.py           # клавиатуры
├─ menu_robot.py           # поддержка, FAQ, отмена
├─ strategy.py             # настройки + PNL (заготовка)
└─ users.db                # база данных (в .gitignore!)
```
## Roadmap / Что доделать

 Полноценная торговля (открытие/закрытие позиций)
 Настраиваемый порог изменения, интервал, топ-N пар
 Inline-кнопки и более удобное меню
 Логирование + уведомления об ошибках
 Docker + docker-compose для деплоя
 Тестнет-режим Binance
 Статистика и график PNL


 ==============================


 # Binance Futures Scanner & Trading Bot (Telegram)

A Telegram bot for scanning Binance Futures market + (in development) automated trading based on simple signals.

Get real-time notifications about strong price movements (≥2% in 3 minutes) and control your trading bot directly from Telegram.

## Current Features

- Scanning USDT-margined futures pairs with 24h volume ≥ $50M
- Price change alerts ≥ 2% over the last 20 candles (3m timeframe)
- Input and validation of Binance API keys (Spot + Futures)
- Start/stop scanner and "robot" (trading logic is a placeholder for now)
- Basic settings menu and PNL statistics (in development)
- SQLite database for storing user keys and statuses

**Roadmap (planned features):**

- Real automated trading triggered by scanner signals
- Configurable risk per trade, leverage, stop-loss / take-profit
- Trailing stop and custom pair filters
- Multi-user support without conflicts

## Requirements

- Python 3.9+
- Telegram Bot Token (get it from @BotFather)
- Binance API Key + Secret (with Futures trading permissions)

## Installation

1. Clone the repository
```bash
git clone https://github.com/KseniiaFFF/The-final-project.git
cd The-final-project
```

2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate      # Linux / macOS
venv\Scripts\activate         # Windows
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Create API_TG.py in the project root with your token:
```bash
import telebot

TOKEN = "your_telegram_bot_token_here"
bot = telebot.TeleBot(TOKEN)
```

5. Run the bot
```bash
python telegram_handler.py
```

## How to Use

- Find your bot in Telegram and send /start
- Choose one of the options:
- Enter API keys (for future trading functionality)
- Continue without API (scanner only)

- Go to «Robot» menu → «Start Scanner»
- Receive notifications about significant price movements

## Project Structure
```text
The-final-project/
├─ API_TG.py               # bot initialization
├─ telegram_handler.py     # main router and message handlers
├─ binance_info.py         # market scanner + notification logic
├─ db_tg.py                # SQLite database operations
├─ check_user_api.py       # Binance API key validation
├─ keyb_robot.py           # reply keyboards
├─ menu_robot.py           # support, FAQ, cancel logic
├─ strategy.py             # settings + PNL (placeholder)
└─ users.db                # user database (add to .gitignore!)
```

## Roadmap / To Do

 Implement real position opening/closing
 Add configurable change threshold, timeframe, top-N pairs
 Inline keyboards and improved menu navigation
 Proper logging + error notifications to user
 Docker + docker-compose deployment
 Binance testnet support
 PNL statistics and performance charts
