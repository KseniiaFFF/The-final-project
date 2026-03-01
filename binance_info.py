#сканер рынка

import requests
import time
import threading
import logging

from keyb_robot import robot_menu
from config import BASE_URL, MIN_VOLUME, INTERVAL, LIMIT, CHANGE_THRESHOLD
from API_TG import bot

logger = logging.getLogger(__name__)

active_scanners = {}
cached_pairs = []
pairs_last_update = 0
CACHE_TTL = 60 

#получаем список торговых USDT пар,фильтр по объёму торгов(MIN_VOLUME), использует кэш на CACHE_TTL секунд
def get_usdt_pairs():
    global cached_pairs, pairs_last_update

    current_time = time.time()

    if cached_pairs and (current_time - pairs_last_update) < CACHE_TTL:
        return cached_pairs

    try:
        url = f"{BASE_URL}/fapi/v1/ticker/24hr"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        pairs = []

        for item in data:
            symbol = item["symbol"]
            quote_volume = float(item["quoteVolume"])

            if symbol.endswith("USDT") and quote_volume >= MIN_VOLUME:
                pairs.append(symbol)

        cached_pairs = pairs
        pairs_last_update = current_time

        logger.info(f"Кэш пар обновлён. Найдено {len(pairs)} пар.")

        return cached_pairs

    except Exception:
        logger.exception("Ошибка обновления списка пар")
        return cached_pairs  

#получает свечи(ТФ - INTERVAL) по символу
def get_klines(symbol):
    url = f"{BASE_URL}/fapi/v1/klines"

    params = {
        "symbol": symbol,
        "interval": INTERVAL,
        "limit": LIMIT
    }

    response = requests.get(url, params=params, timeout=10)
    return response.json()

#проверяет движение цены(CHANGE_THRESHOLD) за выбр период(LIMIT)
def check_pair(symbol):
    try:
        klines = get_klines(symbol)

        first_open = float(klines[0][1])
        last_close = float(klines[-1][4])

        change = ((last_close - first_open) / first_open) * 100

        if abs(change) >= CHANGE_THRESHOLD:
            return round(change, 2)

        return None

    except Exception as e:
        logger.exception(f'Ошибка {symbol}: {e}')
        return None

#сортирует пары, с самым сильным движением в начале, возвр только пеервую пару
def scan_market():
    pairs = get_usdt_pairs()

    print(f"Сканируем {len(pairs)} фьючерсных пар")

    results = []

    for symbol in pairs:
        change = check_pair(symbol)

        if change:
            results.append((symbol, change))

        time.sleep(0.01)

    results.sort(key=lambda x: abs(x[1]), reverse=True)

    return results[:1]

#обеспечивает пост работу сканера, вывод сообщение в тг 
def scanner_loop(chat_id):
    while active_scanners.get(chat_id):

        signals = scan_market()

        for symbol, change in signals:
            if not active_scanners.get(chat_id):
                return
             
            direction = "📈 Рост" if change > 0 else "📉 Падение"

            bot.send_message(
                chat_id,
                f"🚨 {symbol} | {direction} | {change}%"
            )

        for _ in range(10):
            if not active_scanners.get(chat_id):
                return
            # time.sleep(1)

#запускает сканнер, выводит меню робота
def start_scanner(message):
    chat_id = message.chat.id

    if active_scanners.get(chat_id):
        bot.send_message(chat_id, "Сканер уже работает")
        return

    active_scanners[chat_id] = True

    thread = threading.Thread(
        target=scanner_loop,
        args=(chat_id,),
        daemon=True
    )
    thread.start()

    bot.send_message(chat_id, (f'({CHANGE_THRESHOLD} Сканер запущен)'))
    logger.info(f'Сканер запущен| user_name = {message.chat.username}, chat_id = {chat_id}')

    robot_menu(message)

#останавливает сканер, выводит меню робота
def stop_scanner(message):
    chat_id = message.chat.id

    if not active_scanners.get(chat_id, False):
        bot.send_message(chat_id, "Сканер и так не запущен")
        return

    active_scanners[chat_id] = False
    bot.send_message(chat_id, " Сканер остановлен")
    logger.info(f'Сканер остановлен| user_name = {message.chat.username}, chat_id = {chat_id}')

    robot_menu(message)  


      
