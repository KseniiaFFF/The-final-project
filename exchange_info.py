import requests

from decimal import Decimal, ROUND_DOWN
from functools import lru_cache
from config import TESTNET_BASE_URL

#получение информации о торговом символе. Кэширует результат через @lru_cache(maxsize=128) последующие вызовы для тех же символов идут из памяти, не делая новый запрос.
#возвращает словарь с информацией о символе (типы фильтров, минимальная цена, шаг лота и т.д.) или None, если символ не найден.
@lru_cache(maxsize=128)
def get_symbol_info_cached(symbol: str):
    url = f"{TESTNET_BASE_URL}/fapi/v1/exchangeInfo"
    r = requests.get(url, timeout=5)
    r.raise_for_status()
    data = r.json()

    for s in data["symbols"]:
        if s["symbol"] == symbol.upper():
            return s
    return None

#возвращает корректно отформатированную цену строкой, используя информацию из get_symbol_info_cached
def adjust_price_precision(symbol: str, price: float) -> str | None:
    info = get_symbol_info_cached(symbol)
    if not info:
        return None

    price_filter = next(f for f in info["filters"] if f["filterType"] == "PRICE_FILTER")

    tick = Decimal(price_filter["tickSize"])
    price = Decimal(str(price))

    adjusted = (price / tick).quantize(Decimal("1"), rounding=ROUND_DOWN) * tick

    return format(adjusted, "f")

#возвращает корректное количество строкой, используя информацию из get_symbol_info_cached
def adjust_quantity_precision(symbol: str, qty: float) -> str | None:
    info = get_symbol_info_cached(symbol)
    if not info:
        return None

    lot_filter = next(f for f in info["filters"] if f["filterType"] == "LOT_SIZE")

    step = Decimal(lot_filter["stepSize"])
    qty = Decimal(str(qty))

    adjusted = (qty / step).quantize(Decimal("1"), rounding=ROUND_DOWN) * step

    return format(adjusted, "f")