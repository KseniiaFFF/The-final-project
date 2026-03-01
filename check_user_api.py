import time
import hmac
import hashlib
import requests
import logging

logger = logging.getLogger(__name__)

#получение время сервера
def get_server_time(base_url="https://testnet.binancefuture.com"):
    try:
        url = f"{base_url}/fapi/v1/time"
        response = requests.get(url, timeout=5)
        return response.json()["serverTime"]
    except Exception as e:
        logger.exception(f'Time sync error {e}')
        return int(time.time() * 1000)

#создает hmac подпись запроса для апи
def sign_request(secret_key, query_string):
    return hmac.new(
        secret_key.encode(),
        query_string.encode(),
        hashlib.sha256
    ).hexdigest()

#проверка endpoint и корректно ли работают ключи,
def check_endpoint(base_url, endpoint, api_key, secret_key):
    server_time = get_server_time(base_url)
    query_string = f"timestamp={server_time}"
    signature = sign_request(secret_key, query_string)

    headers = {
        "X-MBX-APIKEY": api_key
    }

    url = f"{base_url}{endpoint}?{query_string}&signature={signature}"

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()               

        data = response.json()

        if "code" in data and data["code"] != 200:   
            logger.warning(f"Binance API error | endpoint={endpoint} | code={data.get('code')} | msg={data.get('msg')}")
            return False, data.get("msg", "Неизвестная ошибка от Binance")

        logger.info(f"Binance endpoint OK | {endpoint}")
        return True, "OK"

    except requests.exceptions.RequestException as e:
        logger.exception(f"Request failed | endpoint={endpoint} | {e}")
        return False, f"Ошибка соединения: {str(e)}"

    except ValueError as e:
        logger.exception(f"Invalid JSON from Binance | endpoint={endpoint}")
        return False, "Некорректный ответ от сервера"

#проверяет endpoint для testnet апи
def validate_all(api_key, secret_key):

    results = {}

    results["futures_testnet"] = check_endpoint(
        "https://testnet.binancefuture.com",
        "/fapi/v2/account",
        api_key,
        secret_key
    )

    return results
