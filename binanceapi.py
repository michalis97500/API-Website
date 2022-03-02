import hmac
import time
import hashlib
import requests
import json
import os

# Constants
uri = "https://api.binance.com"
dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, 'Json/config.json')
config = json.load(open(filename))
binance_api_key = config["api"]
binance_api_secret = config["secret"]
contype = "application/json"


def timestamp():
    return int(time.time() * 1000 + get_timestamp_offset())


def get_symbol_price(asset):
    query_string = "symbol={}".format(asset)
    url = "{}/api/v3/avgPrice/{}".format(uri, query_string)
    payload = {}
    headers = {
        "Content-Type": contype
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    return json.loads(response.text)["serverTime"] - int(time.time() * 1000)


def get_timestamp_offset():
    url = "{}/api/v3/time".format(uri)
    payload = {}
    headers = {
        "Content-Type": contype
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    return json.loads(response.text)["serverTime"] - int(time.time() * 1000)


def generate_signature(query_string):
    m = hmac.new(binance_api_secret.encode("utf-8"),
                 query_string.encode("utf-8"), hashlib.sha256)
    return m.hexdigest()


def get_flexible_savings_balance(asset):
    timestamp = int(time.time() * 1000 + get_timestamp_offset())
    query_string = "asset={}&timestamp={}".format(asset, timestamp)
    signature = generate_signature(query_string)
    url = "{}/sapi/v1/lending/daily/token/position?{}&signature={}".format(
        uri, query_string, signature)
    payload = {}
    headers = {
        "Content-Type": contype,
        "X-MBX-APIKEY": binance_api_key
    }
    return json.loads(requests.request("GET", url, headers=headers, data=payload).text)


def get_locked_savings_balance(asset):
    timestamp = int(time.time() * 1000 + get_timestamp_offset())
    query_string = "asset={}&timestamp={}".format(asset, timestamp)
    signature = generate_signature(query_string)
    url = "{}/sapi/v1/lending/project/position/list?{}&signature={}".format(
        uri, query_string, signature)
    payload = {}
    headers = {
        "Content-Type": contype,
        "X-MBX-APIKEY": binance_api_key
    }
    return json.loads(requests.request("GET", url, headers=headers, data=payload).text)


def get_account():
    timestamp = int(time.time() * 1000 + get_timestamp_offset())
    query_string = "timestamp={}".format(timestamp)
    signature = generate_signature(query_string)

    url = "{}/api/v3/account?{}&signature={}".format(
        uri, query_string, signature)

    payload = {}
    headers = {
        "Content-Type": contype,
        "X-MBX-APIKEY": binance_api_key
    }
    return json.loads(requests.request("GET", url, headers=headers, data=payload).text)


def get_lending():
    timestamp = int(time.time() * 1000 + get_timestamp_offset())
    query_string = "timestamp={}".format(timestamp)
    signature = generate_signature(query_string)

    url = "{}/sapi/v1/lending/union/account?{}&signature={}".format(
        uri, query_string, signature)

    payload = {}
    headers = {
        "Content-Type": contype,
        "X-MBX-APIKEY": binance_api_key
    }
    return json.loads(requests.request("GET", url, headers=headers, data=payload).text)


def get_binance_pay_history():
    timestamp = int(time.time() * 1000 + get_timestamp_offset())
    query_string = "timestamp={}".format(timestamp)
    signature = generate_signature(query_string)

    url = "{}/sapi/v1/pay/transactions?{}&signature={}".format(
        uri, query_string, signature)

    payload = {}
    headers = {
        "Content-Type": contype,
        "X-MBX-APIKEY": binance_api_key
    }
    return json.loads(requests.request("GET", url, headers=headers, data=payload).text)
