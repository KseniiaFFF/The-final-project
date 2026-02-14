import requests
import time
import threading
from API_TG import bot

BASE_URL = "https://fapi.binance.com"
MIN_VOLUME = 50_000_000
INTERVAL = "3m"
LIMIT = 20
CHANGE_THRESHOLD = 2.0

active_scanners = {}
last_signals = {}
cached_pairs = []


def get_usdt_pairs():
    global cached_pairs

    if cached_pairs:
        return cached_pairs

    url = f"{BASE_URL}/fapi/v1/ticker/24hr"
    response = requests.get(url, timeout=10)
    data = response.json()

    pairs = []

    for item in data:
        symbol = item["symbol"]
        quote_volume = float(item["quoteVolume"])

        if symbol.endswith("USDT") and quote_volume >= MIN_VOLUME:
            pairs.append(symbol)

    cached_pairs = pairs
    return pairs


def get_klines(symbol):
    url = f"{BASE_URL}/fapi/v1/klines"

    params = {
        "symbol": symbol,
        "interval": INTERVAL,
        "limit": LIMIT
    }

    response = requests.get(url, params=params, timeout=10)
    return response.json()


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
        print(f"Ошибка {symbol}: {e}")
        return None


def scan_market():
    pairs = get_usdt_pairs()

    print(f"Сканируем {len(pairs)} фьючерсных пар")

    results = []

    for symbol in pairs:
        change = check_pair(symbol)

        if change:
            results.append((symbol, change))

        time.sleep(0.05)

    results.sort(key=lambda x: abs(x[1]), reverse=True)

    return results[:5]


def scanner_loop(chat_id):
    while active_scanners.get(chat_id):

        signals = scan_market()

        for symbol, change in signals:
            direction = "📈 Рост" if change > 0 else "📉 Падение"

            bot.send_message(
                chat_id,
                f"🚨 {symbol} | {direction} | {change}%"
            )

        time.sleep(180)


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


def stop_scanner(message):
    chat_id = message.chat.id

    active_scanners[chat_id] = False
    bot.send_message(chat_id, " Сканер остановлен")
