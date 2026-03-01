# Binance Futures Scanner & Trading Bot (Telegram)

Telegram-бот для сканирования рынка Binance Futures и автоматической торговли по простым сигналам.  
Получай уведомления о сильных движениях цены (≥2% за 3 минуты) и управляй торговым роботом прямо в Telegram.  
Бот работает на тестнете Binance для безопасности, но можно адаптировать для реального аккаунта.

## Возможности (на текущий момент)

- **Сканер рынка**: Автоматическое сканирование фьючерсных пар USDT с объёмом торгов ≥ $50M. Уведомления о движении цены ≥ 2% за последние 20 свечей (3m таймфрейм).
- **Автоматическая торговля**: Открытие LONG/SHORT позиций по сигналам сканера. Расчёт стоп-лосса (SL) на основе волатильности, тейк-профита (TP) в 2x от SL. Риск-менеджмент: настраиваемый риск на сделку (0.1–5% от депозита), максимальное плечо (1–125x).
- **Ввод и валидация API-ключей**: Поддержка Binance Futures (тестнет). Проверка ключей на доступ к торговле.
- **Меню в Telegram**: Запуск/остановка сканера и торговли, настройки (риск, плечо), статистика PNL (нереализованная прибыль/убыток по открытым позициям).
- **База данных**: SQLite для хранения API-ключей, статусов и настроек пользователей.
- **Логирование**: Детальные логи в файл `log_tg_bot.txt` для отладки.

Бот поддерживает нескольких пользователей без конфликтов (мультипоточность через threading).

**В планах (roadmap):**
- Добавить дополнительные фильтры пар (например, по волатильности или тренду).
- Интеграция с реальным Binance API (сейчас только тестнет).
- Улучшенная статистика: Графики PNL, история сделок.
- Inline-кнопки для меню, уведомления об ошибках в Telegram.
- Фильтры сигналов: Настраиваемый порог изменения, интервал

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
The-final-project/
├─ API_TG.py               # Инициализация Telegram-бота
├─ telegram_handler.py     # Основной роутер, обработчики сообщений и меню
├─ binance_info.py         # Сканер рынка, уведомления в Telegram
├─ exchange_info.py        # Получение информации о символах (фильтры, precision)
├─ strategy.py             # Логика торговли: расчёт SL/TP, позиции, trading_loop
├─ menu_robot.py           # Обработчики меню (поддержка, FAQ, стоп)
├─ db_tg.py                # Работа с SQLite (хранение ключей, статусов, настроек)
├─ keyb_robot.py           # Клавиатуры и меню
├─ log_settings.py         # Настройка логирования
├─ config.py               # Константы, базовые функции (баланс, цена, PNL)
├─ check_user_api.py       # Валидация API-ключей Binance
├─ users.db                # База данных (игнорируется в .gitignore)
├─ log_tg_bot.txt          # Файл логов (игнорируется в .gitignore)
└─ requirements.txt        # Зависимости
```

 ==============================


 # Binance Futures Scanner & Trading Bot (Telegram)

A Telegram bot that scans the **Binance Futures** market in real time and automatically executes trades based on simple momentum signals.  
Receive instant notifications about strong price movements (≥2% in 3 minutes) and control everything directly from Telegram.

**Currently runs only on Binance Testnet** for safety and testing purposes.

## Current Features

- **Market Scanner**  
  Scans USDT-margined perpetual futures pairs with 24h quote volume ≥ $50M  
  Alerts on price change ≥ **2%** over the last **20 candles** (3-minute timeframe)

- **Automated Trading (Testnet)**  
  Opens LONG or SHORT positions based on scanner signals  
  Calculates dynamic **Stop-Loss** (based on recent volatility)  
  Sets **Take-Profit** (default 2× SL distance)  
  Risk management: configurable risk per trade (0.1–5%), max leverage (1–125×)

- **Binance API Integration**  
  Secure input & validation of API keys (Futures permissions required)  
  Works with **Binance Testnet** by default

- **Telegram Interface**  
  Start / stop scanner and trading loop  
  Settings menu: adjust risk %, max leverage  
  PNL command — shows unrealized profit/loss for open positions  
  Support / FAQ / emergency Stop buttons

- **Storage & Logging**  
  SQLite database for user settings, API keys and robot status  
  Detailed logging to `log_tg_bot.txt`

- **Multi-user support**  
  Each user has independent scanner/trading sessions (thread-based)

## Roadmap (Planned Improvements)

- Switch to real Binance mainnet (with careful safeguards)
- Additional signal filters (volatility, trend)
- Configurable scan parameters (threshold %, timeframe, candle count)
- Trade history & performance statistics
- Inline keyboards & richer messages
- Error notifications & recovery mechanisms
  
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
├── API_TG.py               # Telegram bot initialization
├── telegram_handler.py     # Main message router & menu logic
├── binance_info.py         # Market scanner & Telegram alerts
├── exchange_info.py        # Symbol filters, price/quantity precision
├── strategy.py             # Trading logic: SL/TP calculation, order placement
├── config.py               # Constants, helpers (balance, price, leverage…)
├── db_tg.py                # SQLite operations (users, keys, settings)
├── keyb_robot.py           # Reply keyboards
├── menu_robot.py           # Support, FAQ, cancel handlers
├── check_user_api.py       # Binance API key validation
├── log_settings.py         # Logging configuration
├── users.db                # SQLite database (should be in .gitignore)
├── log_tg_bot.txt          # Log file (add to .gitignore)
└── requirements.txt
```

