import requests
import time

from typing import Optional, Tuple
from API_TG import bot
from db_tg import get_keys, get_connection, is_robot_active, get_user_risk, get_user_max_leverage
from check_user_api import get_server_time, sign_request
from binance_info import scan_market 
from config import TESTNET_BASE_URL, SL_INTERVAL, TRADE_INTERVAL, get_usdt_balance, logger, get_current_price, set_leverage, get_open_positions
from exchange_info import adjust_price_precision, adjust_quantity_precision


#логика и расчет для СЛ, рассчитывает средний диапазон свечей (high - low),умножает на коэффициент(MULTIPLIER) 
def get_stop_loss_price(symbol: str, side: str, current_price: float) -> Optional[float]:
    try:
        params = {
            "symbol": symbol.upper(),
            "interval": SL_INTERVAL,
            "limit": 5                
        }
        url = f"{TESTNET_BASE_URL}/fapi/v1/klines"
        r = requests.get(url, params=params, timeout=6)
        r.raise_for_status()

        data = r.json()
        if len(data) < 4:
            logger.warning(f"Мало свечей для {symbol}: {len(data)}")
            return None

        #последние 3 закрытые свечи
        candles = data[-4:-1]       

        ranges = [float(c[2]) - float(c[3]) for c in candles]  #high - low
        avg_range = sum(ranges) / len(ranges)

        MULTIPLIER = 1.3         
        sl_distance = avg_range * MULTIPLIER

        side_upper = side.upper()
        MIN_DISTANCE = 0.005  
        if side_upper == "LONG":
            sl_price = current_price - sl_distance
            if sl_price > current_price * (1 - MIN_DISTANCE):
                sl_price = current_price * (1 - MIN_DISTANCE)
            print("LONG", sl_price, "price", sl_distance, "sl_dist", current_price, "cur_price")
        elif side_upper == "SHORT":
            sl_price = current_price + sl_distance
            if sl_price < current_price * (1 + MIN_DISTANCE):
                sl_price = current_price * (1 + MIN_DISTANCE)    
            print("SHORT", sl_price, "price", sl_distance, "sl_dist", current_price, "cur_price")

        else:
            return None

        logger.debug(f"{symbol} {side_upper} | curr={current_price:.4f} | avg_rng={avg_range:.6f} | dist={sl_distance:.6f} | SL={sl_price:.4f}")
        return round(sl_price, 8)   

    except Exception as e:
        logger.exception(f"SL calc error {symbol}")
        return None
    
#расчет ТП (по умолчанию в два раза больше длины СЛ)    
def get_take_profit_price(symbol: str, side: str, entry_price: float, stop_loss: float, multiplier: float = 2.0) -> float | None:
    if side.upper() not in ["LONG", "SHORT"]:
        return None

    if side.upper() == "LONG":
        distance = entry_price - stop_loss
        tp = entry_price + distance * multiplier
    else:
        distance = stop_loss - entry_price
        tp = entry_price - distance * multiplier

    tp_adjusted = adjust_price_precision(symbol, tp)
    if not tp_adjusted:
        return None

    return float(tp_adjusted)    
    

#расчет позиции
def calculate_position_params(
    chat_id: int,
    symbol: str,
    side: str,
    entry_price: float,
    tp_multiplier: float = 2.0
) -> Optional[Tuple[float, float, int, float, float]]:

    # 1️⃣ Текущая цена
    current_price = entry_price
    if current_price is None:
        bot.send_message(chat_id, f"Не удалось получить текущую цену {symbol}")
        return None

    # 2️⃣ Стоп-лосс
    sl_price = get_stop_loss_price(symbol, side, current_price)
    if sl_price is None:
        bot.send_message(chat_id, f"Не удалось рассчитать стоп-лосс для {symbol}")
        return None
    
    sl_price_adjusted = adjust_price_precision(symbol, sl_price)
    if not sl_price_adjusted:
        return None

    sl_price_adjusted_float = float(sl_price_adjusted)

    # 3️⃣ Расстояние до SL
    if side.upper() == "LONG":
        risk_distance = (current_price - sl_price_adjusted_float) / current_price
    else:
        risk_distance = (sl_price_adjusted_float - current_price) / current_price

    MIN_DISTANCE = 0.0035  # 0.35%
    if risk_distance < MIN_DISTANCE:
        bot.send_message(chat_id, f"Стоп-лосс слишком близко ({risk_distance*100:.2f}%) — пропускаем {symbol}")
        return None

    # 4️⃣ Баланс и риск
    balance = get_usdt_balance(chat_id)
    if balance is None or balance <= 0:
        bot.send_message(chat_id, "Баланс USDT не доступен или равен нулю")
        return None

    risk_percent = get_user_risk(chat_id)
    risk_usdt = balance * risk_percent

    # 5️⃣ Номинал позиции, ограниченный max_leverage
    max_leverage = get_user_max_leverage(chat_id)
    required_notional = risk_usdt / risk_distance
    max_notional = balance * max_leverage
    position_value_usdt = min(required_notional, max_notional)

    # 6️⃣ Вычисляем плечо и проверяем лимиты
    leverage = position_value_usdt / balance  # реальное плечо
    leverage = min(leverage, max_leverage)    # не выше max_leverage
    leverage = max(1, leverage)               # минимум 1x
    leverage = int(leverage)                  # округление до целого, если биржа требует

    # 7️⃣ Количество монет
    quantity = position_value_usdt / entry_price

    adjusted_qty = adjust_quantity_precision(symbol, quantity)
    if not adjusted_qty:
        bot.send_message(chat_id, f"Количество {symbol} слишком мало")
        return None

    quantity = float(adjusted_qty)

    if quantity <= 0:
        bot.send_message(chat_id, f"Количество {symbol} слишком мало для открытия позиции")
        return None
    
    # 8️⃣ Тейк-профит
    tp_price = get_take_profit_price(symbol, side, entry_price, sl_price_adjusted_float, multiplier=tp_multiplier)
    if tp_price is None:
        bot.send_message(chat_id, f"Не удалось рассчитать TP для {symbol}")
        return None

    return position_value_usdt, quantity, leverage, sl_price_adjusted, tp_price   


def place_order(
    chat_id: int,
    symbol: str,
    side: str,
    quantity: float,
    leverage: int,
    stop_loss: float,
    take_profit: float | None = None,
    tp_multiplier: float = 2.0
) -> bool:

    if not get_keys(chat_id):
        bot.send_message(chat_id, "Нет API ключей")
        return False

    try:
        with get_connection() as conn:
            cursor = conn.execute(
                "SELECT api_key, secret_key FROM users WHERE chat_id = ?",
                (chat_id,)
            )
            api_key, secret_key = cursor.fetchone()

        headers = {"X-MBX-APIKEY": api_key}

        # 1️⃣ Устанавливаем плечо
        if not set_leverage(api_key, secret_key, symbol, leverage):
            bot.send_message(chat_id, "Не удалось установить плечо")
            return False    

        # 2️⃣ MARKET ордер
        adjusted_qty = adjust_quantity_precision(symbol, quantity)
        if not adjusted_qty:
            bot.send_message(chat_id, "Ошибка округления количества")
            return False

        params_order = (
            f"symbol={symbol}"
            f"&side={side}"
            f"&type=MARKET"
            f"&quantity={adjusted_qty}"
            f"&timestamp={get_server_time(TESTNET_BASE_URL)}"
        )

        sig_order = sign_request(secret_key, params_order)
        url_order = f"{TESTNET_BASE_URL}/fapi/v1/order?{params_order}&signature={sig_order}"

        r_order = requests.post(url_order, headers=headers, timeout=10)
        if r_order.status_code != 200:
            logger.warning(f"Ошибка ордера: {r_order.text}")
            bot.send_message(chat_id, f"Ошибка открытия позиции: {r_order.text}")
            return False

        bot.send_message(chat_id, f"Позиция открыта: {symbol} {side} | qty={quantity:.3f} | lev={leverage}x")

        current_price = get_current_price(symbol)
        entry_price = current_price 

        # 3️⃣ Рассчитываем TP

        if take_profit is not None:
            tp_price = take_profit
        else:
            tp_price = get_take_profit_price(symbol, side, entry_price, stop_loss, tp_multiplier)

        if side.upper() == "LONG" and tp_price <= current_price:
            logger.warning(f"TP {tp_price} ниже текущей цены {current_price}, ордер не будет поставлен")
        elif side.upper() == "SHORT" and tp_price >= current_price:
            logger.warning(f"TP {tp_price} выше текущей цены {current_price}, ордер не будет поставлен")


        # 4️⃣ Определяем сторону для SL и TP
        sl_side = "SELL" if side.upper() == "BUY" else "BUY"

        # 5️⃣ Выставляем стоп-лосс
        sl_adjusted = adjust_price_precision(symbol, stop_loss)
        if sl_adjusted:
            params_sl = {
                "symbol": symbol,
                "side": sl_side,
                "type": "STOP_MARKET",
                "algoType": "CONDITIONAL",
                "triggerPrice": sl_adjusted,
                "closePosition": "true",
                "timeInForce": "GTC",
                "workingType": "MARK_PRICE",
                "timestamp": get_server_time(TESTNET_BASE_URL)
            }

            query_sl = "&".join([f"{k}={v}" for k, v in sorted(params_sl.items())])
            sig_sl = sign_request(secret_key, query_sl)
            url_sl = f"{TESTNET_BASE_URL}/fapi/v1/algoOrder?{query_sl}&signature={sig_sl}"

            r_sl = requests.post(url_sl, headers=headers, timeout=15)
            if r_sl.status_code == 200:
                logger.info(f"SL успешно поставлен: {r_sl.json()}")
                bot.send_message(chat_id, f"SL установлен: {sl_adjusted}")
            else:
                logger.warning(f"Ошибка SL: {r_sl.text}")
                bot.send_message(chat_id, f"Позиция открыта, но SL не установлен: {r_sl.text}")

        # 6️⃣ Выставляем тейк-профит
        if tp_price:
            params_tp = {
                "symbol": symbol,
                "side": sl_side,  # SELL если LONG, BUY если SHORT
                "type": "TAKE_PROFIT_MARKET",
                "algoType": "CONDITIONAL",
                "triggerPrice": tp_price,
                "closePosition": "true",
                "timeInForce": "GTC",
                "workingType": "MARK_PRICE",
                "timestamp": get_server_time(TESTNET_BASE_URL)
            }

            query_tp = "&".join([f"{k}={v}" for k, v in sorted(params_tp.items())])
            sig_tp = sign_request(secret_key, query_tp)
            url_tp = f"{TESTNET_BASE_URL}/fapi/v1/algoOrder?{query_tp}&signature={sig_tp}"

            r_tp = requests.post(url_tp, headers=headers, timeout=15)
            if r_tp.status_code == 200:
                logger.info(f"TP успешно поставлен: {r_tp.json()}")
                bot.send_message(chat_id, f"TP установлен: {tp_price}")
            else:
                logger.warning(f"Ошибка TP: {r_tp.text}")
                bot.send_message(chat_id, f"Позиция открыта, но TP не установлен: {r_tp.text}")

        return True

    except Exception:
        logger.exception(f"Ошибка открытия позиции {symbol}")
        bot.send_message(chat_id, "Ошибка открытия позиции")
        return False


#получает сигнал через scan_market, определяет направление позиции, проверяет открытые позиции (get_open_positions), предотвращает повт открытие
#получает текущую цену, вызывает calculate_position_params, вызывыет place_order, ждёт TRADE_INTERVAL между циклами.
def trading_loop(chat_id: int):
    logger.info(f"Запущен trading_loop для chat_id={chat_id}")

    while is_robot_active(chat_id):
        open_positions = get_open_positions(chat_id)

        try:
            signals = scan_market()  # [(symbol, change), ...]
            if not signals:
                bot.send_message(chat_id, "Нет сильных движений на рынке")
                time.sleep(TRADE_INTERVAL)
                continue

            symbol, change = signals[0]

            if change > 0:
                side = "SHORT"
                order_side = "SELL"
            else:
                side = "LONG"
                order_side = "BUY"

            bot.send_message(chat_id, f"Сигнал: {symbol} change={change}% → открываем {side}")

            entry_price = get_current_price(symbol)
            if entry_price is None:
                time.sleep(TRADE_INTERVAL)
                continue

            params = calculate_position_params(chat_id, symbol, side, entry_price)
            if params is None:
                time.sleep(TRADE_INTERVAL)
                continue

            position_value_usdt, quantity, leverage, sl_price, tp_price = params

            if open_positions:
                bot.send_message(chat_id, "Уже есть открытая позиция. Ждём закрытия.")
                time.sleep(TRADE_INTERVAL)
                continue

            success = place_order(chat_id, symbol, order_side, quantity, leverage, sl_price, take_profit=tp_price)
            if not success:
                bot.send_message(chat_id, f"Не удалось открыть позицию {symbol}")

            time.sleep(TRADE_INTERVAL)

        except Exception:
            logger.exception(f"Ошибка в trading_loop chat_id={chat_id}")
            time.sleep(10)

    logger.info(f"trading_loop завершён для chat_id={chat_id}")

