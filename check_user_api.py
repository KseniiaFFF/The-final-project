import time
import hmac
import hashlib
import requests


def sign_request(secret_key, query_string):
    return hmac.new(
        secret_key.encode(),
        query_string.encode(),
        hashlib.sha256
    ).hexdigest()


def check_endpoint(base_url, endpoint, api_key, secret_key):
    timestamp = int(time.time() * 1000)
    query_string = f"timestamp={timestamp}"
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
            return False, data.get("msg", "Ошибка")

        return True, "OK"

    except Exception as e:
        return False, str(e)


def validate_all(api_key, secret_key):

    results = {}

    results["spot"] = check_endpoint(
        "https://api.binance.com",
        "/api/v3/account",
        api_key,
        secret_key
    )

    results["futures"] = check_endpoint(
        "https://fapi.binance.com",
        "/fapi/v2/account",
        api_key,
        secret_key
    )

    results["futures_testnet"] = check_endpoint(
        "https://testnet.binancefuture.com",
        "/fapi/v2/account",
        api_key,
        secret_key
    )

    return results
