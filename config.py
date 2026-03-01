#часто исп переменные, базовые функции для торговли, не стратегические

import requests
import logging
import time

from telebot import types
from db_tg import get_keys, get_connection
from typing import Optional
from API_TG import bot
from check_user_api import get_server_time, sign_request
from db_tg import get_user_risk, get_user_max_leverage

BASE_URL = "https://fapi.binance.com"
MIN_VOLUME = 50_000_000
INTERVAL = "3m"
LIMIT = 20
CHANGE_THRESHOLD = 2.0

TESTNET_BASE_URL = "https://testnet.binancefuture.com"
RISK_PER_TRADE_DEFAULT = 0.001      # 0.1% от баланса
MAX_LEVERAGE_CAP = 20              # верхняя граница (реально зависит от символа)
SL_INTERVAL = "4h"                 # таймфрейм для стоп-лосса
TRADE_INTERVAL = 18  

logger = logging.getLogger(__name__)

#проверка сохр апи по chat_id, запрашивает и возвращает баланс USDT 
def get_usdt_balance(chat_id: int) -> Optional[float]:

    if not get_keys(chat_id):
        logger.warning(f"Нет ключей для chat_id {chat_id}")
        bot.send_message(chat_id, "Нет сохранённых API-ключей")
        return None

    try:
        with get_connection() as conn:
            cursor = conn.execute(
                "SELECT api_key, secret_key FROM users WHERE chat_id = ?",
                (chat_id,)
            )
            row = cursor.fetchone()
            if not row or not row[0] or not row[1]:
                return None
            api_key, secret_key = row

        timestamp = get_server_time(TESTNET_BASE_URL)
        query_string = f"timestamp={timestamp}"
        signature = sign_request(secret_key, query_string)

        url = f"{TESTNET_BASE_URL}/fapi/v2/balance?{query_string}&signature={signature}"
        headers = {"X-MBX-APIKEY": api_key}

        resp = requests.get(url, headers=headers, timeout=8)
        resp.raise_for_status()

        data = resp.json()  #список словарей

        for asset in data:
            if asset.get("asset") == "USDT":
                bal = float(asset.get("balance", 0))
                logger.info(f"USDT balance для {chat_id}: {bal}")
                return bal

        logger.warning(f"USDT не найден в балансе для {chat_id}")
        return 0.0

    except Exception as e:
        logger.exception(f"Ошибка получения баланса USDT | chat_id={chat_id}")
        bot.send_message(chat_id, "Не удалось получить баланс USDT")
        return None
    
#получает текущую рын цену по символу
def get_current_price(symbol: str) -> Optional[float]:
    try:
        url = f"{TESTNET_BASE_URL}/fapi/v1/ticker/price?symbol={symbol.upper()}"
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        data = r.json()
        return float(data.get("price"))
    except Exception as e:
        logger.exception(f"Ошибка получения цены {symbol}")
        return None    
    
#уст плечо для позиции
def set_leverage(api_key, secret_key, symbol, leverage, retries=3):
    headers = {"X-MBX-APIKEY": api_key}
    for i in range(retries):
        timestamp = get_server_time(TESTNET_BASE_URL)
        params = f"symbol={symbol}&leverage={leverage}&timestamp={timestamp}"
        sig = sign_request(secret_key, params)
        url = f"{TESTNET_BASE_URL}/fapi/v1/leverage?{params}&signature={sig}"
        r = requests.post(url, headers=headers, timeout=10)
        if r.status_code == 200:
            return True
        time.sleep(0.5)
    return False    

#вызов меню "Настройки" в меню "Робот"
def settings(message):
    chat_id = message.chat.id
    risk = get_user_risk(chat_id) * 100
    lev = get_user_max_leverage(chat_id)
    
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    keyboard.add('Изменить риск на сделку')
    keyboard.add('Изменить максимальное плечо')
    keyboard.add('Назад')
    
    text = (
        f"Текущие настройки:\n"
        f"• Риск на сделку: {risk:.2f}%\n"
        f"• Максимальное плечо: {lev}x\n\n"
        "Что хотите изменить?"
    )
    bot.send_message(chat_id, text, reply_markup=keyboard)


#возвращает список словарей с данными о позициях.
def get_open_positions(chat_id: int) -> list[dict]:
    if not get_keys(chat_id):
        logger.warning(f"Нет ключей для chat_id {chat_id}")
        return []

    try:
        with get_connection() as conn:
            cursor = conn.execute(
                "SELECT api_key, secret_key FROM users WHERE chat_id = ?",
                (chat_id,)
            )
            row = cursor.fetchone()
            if not row or not row[0] or not row[1]:
                return []
            api_key, secret_key = row

        timestamp = get_server_time(TESTNET_BASE_URL)
        query_string = f"timestamp={timestamp}"
        signature = sign_request(secret_key, query_string)

        url = f"{TESTNET_BASE_URL}/fapi/v2/positionRisk?{query_string}&signature={signature}"
        headers = {"X-MBX-APIKEY": api_key}

        resp = requests.get(url, headers=headers, timeout=8)
        resp.raise_for_status()

        positions = resp.json()  #список позиций

        #фильтр только открытые позиции (positionAmt != 0)
        active_positions = [
            pos for pos in positions
            if float(pos.get("positionAmt", 0)) != 0
        ]

        return active_positions

    except Exception as e:
        logger.exception(f"Ошибка получения позиций | chat_id={chat_id}")
        bot.send_message(chat_id, "Не удалось загрузить информацию о позициях")
        return []

#инфо get_open_positions, считает PNL для откр позиции, формирует и отправляет подробное сообщение юзеру в тг
def pnl(message):
    chat_id = message.chat.id

    positions = get_open_positions(chat_id)

    if not positions:
        bot.send_message(
            chat_id,
            "У вас сейчас нет открытых позиций на тестнете.\n"
            "PNL = 0.00 USDT"
        )
        return

    total_pnl = 0.0
    text_lines = ["📊 **Текущие позиции и PNL** (testnet)\n"]

    for pos in positions:
        symbol = pos.get("symbol", "—")
        position_amt = float(pos.get("positionAmt", 0))
        entry_price = float(pos.get("entryPrice", 0))
        mark_price = float(pos.get("markPrice", 0))
        unrealized_pnl = float(pos.get("unRealizedProfit", 0))
        leverage = pos.get("leverage", "—")

        side = "LONG" if position_amt > 0 else "SHORT"
        pnl_sign = "+" if unrealized_pnl >= 0 else ""
        pnl_percent = (unrealized_pnl / (abs(position_amt) * entry_price)) * 100 if entry_price > 0 else 0

        line = (
            f"{symbol} {side} {abs(position_amt):.3f} × {leverage}x\n"
            f"  Вход: {entry_price:.2f} | Текущая: {mark_price:.2f}\n"
            f"  PNL: {pnl_sign}{unrealized_pnl:.2f} USDT ({pnl_percent:+.2f}%)\n"
        )
        text_lines.append(line)

        total_pnl += unrealized_pnl

    total_sign = "+" if total_pnl >= 0 else ""
    summary = f"\n**Общий нереализованный PNL: {total_sign}{total_pnl:.2f} USDT**"

    full_text = "".join(text_lines) + summary

    bot.send_message(
        chat_id,
        full_text,
        parse_mode="Markdown"
    )

    logger.info(f"PNL запрошен | chat_id={chat_id} | позиций: {len(positions)} | total pnl: {total_pnl:.2f}")    