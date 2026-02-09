# The-final-project
# Trading Bot for Binance with Risk Management and Telegram Notifications
## Overview
This project is a simple trading bot designed for the Binance cryptocurrency exchange. It implements a basic trading strategy with built-in risk management features. The bot uses Binance API keys for trading operations and integrates with Telegram for real-time notifications about portfolio balance, open positions, and performance metrics. A database is used to store information about closed trades for calculating PNL (Profit and Loss) without considering deposits or withdrawals.
The bot supports customizable notifications: either timed updates on balance changes or on-demand queries via Telegram buttons/commands for balance, open positions, daily/weekly/monthly profitability.
The code is modularized into several Python files for better maintainability:

strategy.py: Contains all functions related to the trading strategy and risk calculations.
data_collector.py: Handles collecting and storing balance and trade data into the database.
telegram_handler.py: Manages Telegram bot interactions and notifications.
exchange_connector.py: Deals with Binance API connections and operations.
config.py: Settings and API keys
(Additional files may be added as needed during development, e.g., main.py for running the bot.)

## Features

Trading Strategy: A simple strategy (e.g., based on moving averages or other indicators – to be specified/implemented). Includes risk management: position sizing based on account balance, stop-loss, take-profit levels.
Risk Calculation: Automatically calculates risk per trade (e.g., max 1-2% of portfolio per trade) to prevent significant losses.
Binance Integration: Uses official Binance API for fetching market data, placing orders, and managing positions.
Telegram Notifications:
Real-time alerts on balance changes, position status.
Configurable modes: Timed notifications (e.g., every hour) or on-demand via buttons/commands.
Queries for: Current balance, open positions, PNL for day/week/month.

Database Integration: Stores closed trade data for historical analysis and profitability calculations (pure PNL, excluding deposits/withdrawals). Supports SQLite or other lightweight DB (e.g., PostgreSQL for scalability).
Modular Design: Code separated into files for easy extension and debugging.

## Requirements

Python 3.8+
Libraries:
ccxt or binance for Binance API interactions.
python-telegram-bot for Telegram integration.
sqlite3 or SQLAlchemy for database operations.
Other dependencies: pandas for data handling, ta-lib for technical indicators (if needed).

Binance API keys (with trading permissions).
Telegram Bot Token (create via BotFather).

Install dependencies via:
   ```bash
   pip install -r requirements.txt
 ```
## Installation
1. Clone the repository:
   ```bash
   textgit clone https://github.com/yourusername/trading-bot.git
   cd trading-bot
2. Install required packages:
   ```bash
   textpip install -r requirements.txt
3. Set up configuration:
# Binance API
   ```bash
      BINANCE_API_KEY = 'your_binance_api_key'
      BINANCE_SECRET_KEY = 'your_binance_secret_key'
```
# Telegram Bot
   ```bash
      TELEGRAM_BOT_TOKEN = 'your_telegram_bot_token'
      TELEGRAM_CHAT_ID = 'your_chat_id'  # For notifications
```
# Database
   ```bash
      DB_PATH = 'trades.db'  # SQLite file path
```
# Strategy Settings
   ```bash
      RISK_PER_TRADE = 0.01  # 1% of portfolio per trade
      STRATEGY_PARAMS = {'ma_short': 50, 'ma_long': 200}  # Example for moving average strategy
```
# Notification Settings
   ```bash
      NOTIFY_INTERVAL = 3600  # Seconds for timed notifications (0 to disable)
      Run the bot:textpython main.py
```
4. Run the bot:
   ```bash
      textpython main.py      



# Торговый робот для Binance с управлением рисками и уведомлениями в Telegram

## О проекте

Это простой торговый бот для биржи Binance. Реализована базовая торговая стратегия с обязательным контролем рисков.  
Бот использует API-ключи Binance для торговли и Telegram-бота для уведомлений.  
Есть база данных для хранения истории закрытых сделок и расчёта чистой прибыли/убытка (PnL) без учёта вводов и выводов средств.

Бот умеет:
- отправлять уведомления по расписанию (о балансе, позициях, изменениях)
- или выдавать информацию по командам/кнопкам в Telegram
- показывать: текущий баланс, открытые позиции, доходность за день / неделю / месяц

Код разбит на несколько файлов для удобства:

- `strategy.py` - вся логика торговой стратегии и расчёт рисков  
- `data_collector.py` - сбор данных о балансе и сделках → запись в базу  
- `telegram_handler.py` - работа с Telegram (уведомления, команды, кнопки)  
- `exchange_connector.py` - взаимодействие с Binance API
- `config.py` - основные конфигурации, ключи
- (по мере разработки могут появиться `main.py`, `utils.py` и др.)

## Возможности

- Простая торговая стратегия (например, пересечение скользящих средних или другая - будет дописано)  
- Управление рисками: размер позиции не более 1–2% от депозита, стоп-лосс, тейк-профит  
- Интеграция с Binance (через библиотеку `ccxt` или `python-binance`)  
- Уведомления в Telegram:  
  - автоматические по таймеру  
  - по запросу через команды или кнопки  
  - `/balance`, `/positions`, `/pnl day`, `/pnl week`, `/pnl month`  
- Хранение истории сделок в базе (SQLite или другая) для точного подсчёта PnL  
- Модульная структура кода

## Требования

- Python 3.8+  
- Библиотеки:
  - `ccxt` или `python-binance`
  - `python-telegram-bot`
  - `sqlite3` / `SQLAlchemy`
  - `pandas` (удобно для расчётов)
  - опционально: `ta` / `talib` для индикаторов

## Установка

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/ВАШ_НИК/trading-bot.git
   cd trading-bot

2. Установите зависимости:
   ```bash
    pip install -r requirements.txt
3. Настройте конфиг
# Binance
```bash
BINANCE_API_KEY    = 'ваш_api_key'
BINANCE_SECRET_KEY = 'ваш_secret_key'
```
# Telegram
```bash
TELEGRAM_BOT_TOKEN = '123456:AAF1b2C3d.....'
TELEGRAM_CHAT_ID   = 'ваш_chat_id'
```
# База данных
```bash
DB_PATH = 'trades.db'
```
# Настройки стратегии
```bash
RISK_PER_TRADE = 0.01       # 1% от депозита на сделку
STRATEGY_PARAMS = {'ma_short': 50, 'ma_long': 200}
```

# Уведомления
```bash
NOTIFY_INTERVAL = 3600      # интервал в секундах (0 = отключено)
```

!Важно: не коммитьте ключи в репозиторий! Добавьте config.py, .env в .gitignore!

Команды в Telegram (примеры)

/balance — текущий баланс портфеля
/positions — открытые позиции
/pnl day — результат за сегодня
/pnl week — за неделю
/pnl month — за месяц

База данных (пример структуры)
Таблица trades:

id
symbol (BTCUSDT, ETHUSDT и т.д.)
entry_price
exit_price
quantity
pnl
timestamp

Предупреждение
Это учебный / экспериментальный проект.
Торговля криптовалютой связана с высоким риском потери средств.
Используйте на свой страх и риск. Автор не несёт ответственности за убытки.
Удачной торговли и профита! 🚀
   
