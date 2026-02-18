import time
import hmac
import hashlib
import requests

import logging

logger = logging.getLogger(__name__)

def get_server_time(base_url):
    try:
        if "future" in base_url or "fapi" in base_url:
            url = f"{base_url}/fapi/v1/time"
        else:
            url = f"{base_url}/api/v3/time"

        response = requests.get(url, timeout=5)
        return response.json()["serverTime"]
    except Exception as e:
        print("Time sync error:", e)
        logging.exception(f'Time sync error {e}')
        return int(time.time() * 1000)


def sign_request(secret_key, query_string):
    return hmac.new(
        secret_key.encode(),
        query_string.encode(),
        hashlib.sha256
    ).hexdigest()
    

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
        data = response.json()

        print(data)

        if "code" in data:
            logger.warning(
                f"Binance API error | endpoint={endpoint} | "
                f"code={data.get('code')} | msg={data.get('msg')}"
            )
            return False, data.get("msg", "Ошибка")
        
        logger.info(f"Binance endpoint OK | {endpoint}")
        return True, "OK"

    except Exception as e:
        logger.exception(
            f"Exception in check_endpoint | endpoint={endpoint}"
        )
        return False, "Request failed"


def validate_all(api_key, secret_key):

    results = {}

    results["futures_testnet"] = check_endpoint(
        "https://testnet.binancefuture.com",
        "/fapi/v2/account",
        api_key,
        secret_key
    )

    return results
