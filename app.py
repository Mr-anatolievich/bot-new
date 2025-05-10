from flask import Flask, render_template, request
from binance.client import Client as BinanceClient
from pybit.unified_trading import HTTP as BybitClient
from kucoin.client import Client as KucoinClient
import gate_api
from gate_api.exceptions import ApiException, GateApiException
from huobi import HuobiRestClient
from mexc_api.spot import Spot
from pybitget import Client as BitgetClient
from datetime import datetime, timezone
from collections import defaultdict
import requests
import time
import os
import hmac
import hashlib
import pybase64 as base64
import datetime
from dotenv import load_dotenv
import re
from flask import redirect, url_for

app = Flask(__name__)

load_dotenv()

binance_client = BinanceClient(
    api_key=os.getenv('BINANCE_API_KEY'),
    api_secret=os.getenv('BINANCE_API_SECRET')
)
bybit_client = BybitClient(
    api_key=os.getenv('BYBIT_API_KEY'),
    api_secret=os.getenv('BYBIT_API_SECRET'),
    testnet=False
)
OKX_API_KEY = os.getenv('OKX_API_KEY')
OKX_API_SECRET = os.getenv('OKX_API_SECRET')
OKX_PASSPHRASE = os.getenv('OKX_PASSPHRASE')

KUCOIN_API_KEY = os.getenv('KUCOIN_API_KEY')
KUCOIN_API_SECRET = os.getenv('KUCOIN_API_SECRET')
KUCOIN_API_PASSPHRASE = os.getenv('KUCOIN_API_PASSPHRASE')

GATEIO_API_KEY = os.getenv('GATEIO_API_KEY')
GATEIO_API_SECRET = os.getenv('GATEIO_API_SECRET')

HUOBI_API_KEY = os.getenv('HUOBI_API_KEY')
HUOBI_API_SECRET = os.getenv('HUOBI_API_SECRET')

MEXC_API_KEY = os.getenv('MEXC_API_KEY')
MEXC_API_SECRET = os.getenv('MEXC_API_SECRET')

BITGET_API_KEY = os.getenv('BITGET_API_KEY')
BITGET_API_SECRET = os.getenv('BITGET_API_SECRET')
BITGET_API_PASSPHRASE = os.getenv('BITGET_API_PASSPHRASE')

CRYPTOCOM_API_KEY = os.getenv('CRYPTOCOM_API_KEY')
CRYPTOCOM_API_SECRET = os.getenv('CRYPTOCOM_API_SECRET')

kucoin_client = KucoinClient(KUCOIN_API_KEY, KUCOIN_API_SECRET, KUCOIN_API_PASSPHRASE)

gate_config = gate_api.Configuration(key=GATEIO_API_KEY, secret=GATEIO_API_SECRET)
gate_client = gate_api.ApiClient(gate_config)
gate_spot_api = gate_api.SpotApi(gate_client)
gate_wallet_api = gate_api.WalletApi(gate_client)

huobi_client = HuobiRestClient(access_key=HUOBI_API_KEY, secret_key=HUOBI_API_SECRET)

mexc_client = Spot(api_key=os.getenv('MEXC_API_KEY'), api_secret=os.getenv('MEXC_API_SECRET'))

bitget_client = BitgetClient(BITGET_API_KEY, BITGET_API_SECRET, BITGET_API_PASSPHRASE)

# --- Кеші та таймінги ---
binance_networks_cache = {}
bybit_networks_cache = {}
okx_networks_cache = {}
kucoin_networks_cache = {}
gateio_networks_cache = {}
huobi_networks_cache = {}
mexc_networks_cache = {}
bitget_networks_cache = {}
cryptocom_networks_cache = {}

binance_cache_time = 0
bybit_cache_time = 0
okx_cache_time = 0
kucoin_cache_time = 0
gateio_cache_time = 0
huobi_cache_time = 0
mexc_cache_time = 0
bitget_cache_time = 0
cryptocom_cache_time = 0
CACHE_DURATION = 3600

def normalize_symbol(symbol):
    symbol = symbol.replace('-', '').replace('_', '').replace('/', '').upper()
    if symbol.endswith(('USDT', 'USDC')):  # Стандартизація для стейблкоінів
        return symbol[:-4] + symbol[-4:]
    return symbol

def get_base_token(symbol):
    match = re.match(r'^([A-Z]+)(USDT|BTC|ETH|BUSD|USDC)$', symbol)
    return match.group(1) if match else symbol

def get_binance_data():
    try:
        tickers = binance_client.get_ticker()
        binance = {}
        for item in tickers:
            symbol = item['symbol']
            if not symbol.endswith('USDT'):
                continue
            normalized_symbol = normalize_symbol(symbol)
            binance[normalized_symbol] = {
                'symbol': item['symbol'],
                'bid': float(item['bidPrice']),
                'ask': float(item['askPrice']),
                'volume': float(item.get('volume', 0))
            }
        return binance
    except Exception as e:
        app.logger.error(f"Binance error: {str(e)}")
        return {}

def get_bybit_data():
    try:
        result = bybit_client.get_tickers(category='spot')
        bybit = {}
        for item in result.get('result', {}).get('list', []):
            symbol = item['symbol']
            if not symbol.endswith('USDT'):
                continue
            normalized_symbol = normalize_symbol(symbol)
            bybit[normalized_symbol] = {
                'symbol': item['symbol'],
                'bid': float(item.get('bid1Price', 0)),
                'ask': float(item.get('ask1Price', 0)),
                'volume': float(item.get('volume24h', 0))
            }
        return bybit
    except Exception as e:
        app.logger.error(f"Bybit error: {str(e)}")
        return {}

def get_okx_data():
    try:
        timestamp = datetime.now(timezone.utc).isoformat()[:-13]+'Z'
        method = 'GET'
        endpoint = '/api/v5/market/tickers'
        params = 'instType=SPOT'
        message = timestamp + method + endpoint + params
        signature = base64.b64encode(
            hmac.new(OKX_API_SECRET.encode(), message.encode(), hashlib.sha256).digest()
        ).decode()
        headers = {
            'OK-ACCESS-KEY': OKX_API_KEY,
            'OK-ACCESS-SIGN': signature,
            'OK-ACCESS-TIMESTAMP': timestamp,
            'OK-ACCESS-PASSPHRASE': OKX_PASSPHRASE
        }
        response = requests.get(
            f"https://www.okx.com{endpoint}?{params}",
            headers=headers,
            timeout=10
        )
        okx = {}
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == '0':
                for item in data['data']:
                    symbol = item['instId']
                    if not symbol.endswith('USDT'):
                        continue
                    normalized_symbol = normalize_symbol(symbol)
                    okx[normalized_symbol] = {
                        'symbol': item['instId'],
                        'bid': float(item['bidPx']),
                        'ask': float(item['askPx']),
                    }
        return okx
    except Exception as e:
        app.logger.error(f"OKX error: {str(e)}")
        return {}

def get_kucoin_data():
    try:
        tickers = kucoin_client.get_tickers()
        kucoin = {}
        if 'ticker' in tickers:
            for item in tickers['ticker']:
                symbol = item.get('symbol', '').replace('-', '')
                if not symbol.endswith('USDT'):
                    continue
                normalized_symbol = normalize_symbol(symbol)
                bid = item.get('buy') or '0'
                ask = item.get('sell') or '0'
                last = item.get('last') or '0'
                volume = item.get('vol') or '0'
                kucoin[normalized_symbol] = {
                    'symbol': item.get('symbol', ''),
                    'bid': float(bid),
                    'ask': float(ask),
                    'last': float(last),
                    'volume': float(volume)
                }
        return kucoin
    except Exception as e:
        app.logger.error(f"KuCoin error: {str(e)}")
        return {}

def get_gateio_data():
    try:
        response = requests.get("https://api.gateio.ws/api/v4/spot/tickers", timeout=10)
        gateio = {}
        if response.status_code == 200:
            data = response.json()
            for item in data:
                symbol = item['currency_pair'].replace('_', '')
                if not symbol.endswith('USDT'):
                    continue
                normalized_symbol = normalize_symbol(symbol)
                bid = item.get('bid', '0')
                ask = item.get('ask', '0')
                if bid and ask:
                    try:
                        gateio[normalized_symbol] = {
                            'symbol': item['currency_pair'],
                            'bid': float(bid),
                            'ask': float(ask),
                        }
                    except ValueError:
                        continue
        return gateio
    except Exception as e:
        app.logger.error(f"Gate.io error: {str(e)}")
        return {}

def get_huobi_data():
    try:
        response = requests.get("https://api.huobi.pro/market/tickers", timeout=10)
        huobi = {}
        if response.status_code == 200:
            data = response.json()
            if 'data' in data:
                for item in data['data']:
                    symbol = item['symbol'].upper()
                    if not symbol.endswith('USDT'):
                        continue
                    normalized_symbol = normalize_symbol(symbol)
                    try:
                        bid = float(item['bid'][0]) if isinstance(item['bid'], list) and len(item['bid']) >= 1 else float(item['bid'])
                        ask = float(item['ask'][0]) if isinstance(item['ask'], list) and len(item['ask']) >= 1 else float(item['ask'])
                        huobi[normalized_symbol] = {
                            'symbol': item['symbol'],
                            'bid': bid,
                            'ask': ask,
                        }
                    except (ValueError, TypeError, IndexError):
                        continue
        return huobi
    except Exception as e:
        app.logger.error(f"Huobi error: {str(e)}")
        return {}

def get_mexc_data():
    try:
        response = mexc_client.market.ticker()
        data = response.json() if isinstance(response, requests.Response) else response
        mexc = {}
        for item in data.get('data', []):
            symbol = item.get('symbol', '')
            if not symbol.endswith('USDT'):
                continue
            normalized_symbol = normalize_symbol(symbol)
            mexc[normalized_symbol] = {
                'symbol': item.get('symbol', ''),
                'bid': float(item.get('bidPrice', 0) or 0),
                'ask': float(item.get('askPrice', 0) or 0),
                'last': float(item.get('lastPrice', 0) or 0),
                'volume': float(item.get('volume', 0) or 0)
            }
        return mexc
    except Exception as e:
        app.logger.error(f"MEXC error: {str(e)}")
        return {}

def get_bitget_data():
    try:
        response = requests.get("https://api.bitget.com/api/spot/v1/market/tickers", timeout=10)
        bitget = {}
        if response.status_code == 200:
            data = response.json()
            if 'data' in data:
                for item in data['data']:
                    symbol = item['symbol'].replace('_', '')
                    if not symbol.endswith('USDT'):
                        continue
                    normalized_symbol = normalize_symbol(symbol)
                    if 'bidPrice' in item and 'askPrice' in item:
                        try:
                            bitget[normalized_symbol] = {
                                'symbol': item['symbol'],
                                'bid': float(item['bidPrice']),
                                'ask': float(item['askPrice']),
                                'volume': float(item['volume'])
                            }
                        except (ValueError, TypeError):
                            continue
        return bitget
    except Exception as e:
        app.logger.error(f"Bitget error: {str(e)}")
        return {}

def get_cryptocom_data():
    try:
        response = requests.get("https://api.crypto.com/v2/public/get-ticker", timeout=10)
        cryptocom = {}
        if response.status_code == 200:
            data = response.json()
            if 'result' in data and 'data' in data['result']:
                for item in data['result']['data']:
                    symbol = item['i']
                    if not symbol.endswith('USDT'):
                        continue
                    normalized_symbol = normalize_symbol(symbol)
                    bid = item.get('b')
                    ask = item.get('a')
                    if bid is not None and ask is not None:
                        try:
                            cryptocom[normalized_symbol] = {
                                'symbol': item['i'],
                                'bid': float(bid),
                                'ask': float(ask),
                            }
                        except (ValueError, TypeError):
                            continue
        return cryptocom
    except Exception as e:
        app.logger.error(f"Crypto.com error: {str(e)}")
        return {}


def get_binance_networks_for_coins():
    global binance_networks_cache, binance_cache_time
    current_time = time.time()
    if current_time - binance_cache_time > CACHE_DURATION:
        try:
            result = binance_client.get_all_coins_info()
            binance_networks_cache = {
                coin['coin']: [
                    {
                        'name': net['network'],
                        'deposit': net['depositEnable'],
                        'withdraw': net['withdrawEnable'],
                        'fee': net['withdrawFee']
                    } for net in coin['networkList']
                ] for coin in result
            }
            binance_cache_time = current_time
        except Exception as e:
            app.logger.error(f"Binance networks error: {str(e)}")
    return binance_networks_cache

def get_bybit_networks_for_coins():
    global bybit_networks_cache, bybit_cache_time
    current_time = time.time()
    if current_time - bybit_cache_time > CACHE_DURATION:
        try:
            result = bybit_client.get_coin_info()
            bybit_networks_cache = {
                row['coin']: [
                    {
                        'name': chain['chain'],
                        'deposit': chain['chainDeposit'] == '1',
                        'withdraw': chain['chainWithdraw'] == '1',
                        'fee': chain['withdrawFee']
                    } for chain in row.get('chains', [])
                ] for row in result.get('result', {}).get('rows', [])
            }
            bybit_cache_time = current_time
        except Exception as e:
            app.logger.error(f"Bybit networks error: {str(e)}")
    return bybit_networks_cache

def get_okx_networks_for_coins():
    global okx_networks_cache, okx_cache_time
    current_time = time.time()
    if current_time - okx_cache_time > CACHE_DURATION:
        try:
            timestamp = datetime.datetime.utcnow().isoformat()[:-3]+'Z'
            method = 'GET'
            endpoint = '/api/v5/asset/currencies'
            message = timestamp + method + endpoint
            signature = base64.b64encode(
                hmac.new(OKX_API_SECRET.encode(), message.encode(), hashlib.sha256).digest()
            ).decode()
            headers = {
                'OK-ACCESS-KEY': OKX_API_KEY,
                'OK-ACCESS-SIGN': signature,
                'OK-ACCESS-TIMESTAMP': timestamp,
                'OK-ACCESS-PASSPHRASE': OKX_PASSPHRASE
            }
            response = requests.get(
                f"https://www.okx.com{endpoint}",
                headers=headers,
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                okx_networks_cache = {}
                for item in data.get('data', []):
                    ccy = item['ccy']
                    if ccy not in okx_networks_cache:
                        okx_networks_cache[ccy] = []
                    okx_networks_cache[ccy].append({
                        'name': item['chain'],
                        'deposit': item['canDep'] == 'true',
                        'withdraw': item['canWd'] == 'true',
                        'fee': item['minFee']
                    })
                okx_cache_time = current_time
        except Exception as e:
            app.logger.error(f"OKX networks error: {str(e)}")
    return okx_networks_cache

def get_kucoin_networks_for_coins():
    global kucoin_networks_cache, kucoin_cache_time
    current_time = time.time()
    if current_time - kucoin_cache_time > CACHE_DURATION:
        try:
            response = requests.get("https://api.kucoin.com/api/v3/currencies", timeout=10)
            if response.status_code == 200:
                data = response.json()
                kucoin_networks_cache = {}
                if data.get('code') == '200000' and 'data' in data:
                    coins_data = data.get('data', [])
                    if coins_data is None:
                        coins_data = []
                    for coin in coins_data:
                        if 'currency' in coin and 'chains' in coin:
                            chains = coin.get('chains', [])
                            if chains is None:
                                chains = []
                            networks = []
                            for chain in chains:
                                if 'chainName' in chain:
                                    networks.append({
                                        'name': chain['chainName'],
                                        'deposit': chain.get('isDepositEnabled', False),
                                        'withdraw': chain.get('isWithdrawEnabled', False),
                                        'fee': chain.get('withdrawalMinFee', '0')
                                    })
                            kucoin_networks_cache[coin['currency']] = networks
                kucoin_cache_time = current_time
        except Exception as e:
            app.logger.error(f"KuCoin networks error: {str(e)}")
    return kucoin_networks_cache

def get_gateio_networks_for_coins():
    global gateio_networks_cache, gateio_cache_time
    current_time = time.time()
    if current_time - gateio_cache_time > CACHE_DURATION:
        try:
            # Використовуємо Gate.io API для отримання інформації про ланцюги валют
            response = requests.get("https://api.gateio.ws/api/v4/wallet/currency_chains", timeout=10)
            if response.status_code == 200:
                data = response.json()
                gateio_networks_cache = {}
                for item in data:
                    currency = item['currency']
                    if currency not in gateio_networks_cache:
                        gateio_networks_cache[currency] = []
                    gateio_networks_cache[currency].append({
                        'name': item['chain'],
                        'deposit': item.get('is_deposit_disabled', 0) == 0,
                        'withdraw': item.get('is_withdraw_disabled', 0) == 0,
                        'fee': str(item.get('withdraw_fee', '0'))
                    })
                gateio_cache_time = current_time
        except Exception as e:
            app.logger.error(f"Gate.io networks error: {str(e)}")
    return gateio_networks_cache

def get_huobi_networks_for_coins():
    global huobi_networks_cache, huobi_cache_time
    current_time = time.time()
    if current_time - huobi_cache_time > CACHE_DURATION:
        try:
            # Використовуємо Huobi API для отримання інформації про валюти та мережі
            response = requests.get("https://api.huobi.pro/v2/reference/currencies", timeout=10)
            if response.status_code == 200:
                data = response.json()
                huobi_networks_cache = {}
                if 'data' in data:
                    for currency in data['data']:
                        if 'chains' in currency and currency['chains']:
                            currency_code = currency['currency']
                            networks = []
                            for chain in currency['chains']:
                                networks.append({
                                    'name': chain['chain'],
                                    'deposit': chain.get('depositStatus', 'allowed') == 'allowed',
                                    'withdraw': chain.get('withdrawStatus', 'allowed') == 'allowed',
                                    'fee': str(chain.get('transactFeeWithdraw', '0'))
                                })
                            huobi_networks_cache[currency_code] = networks
                huobi_cache_time = current_time
        except Exception as e:
            app.logger.error(f"Huobi networks error: {str(e)}")
    return huobi_networks_cache

def get_mexc_networks_for_coins():
    global mexc_networks_cache, mexc_cache_time
    current_time = time.time()

    if current_time - mexc_cache_time > CACHE_DURATION:
        try:
            # Автентифікація
            timestamp = int(time.time() * 1000)
            params = f'timestamp={timestamp}'
            signature = hmac.new(
                os.getenv('MEXC_API_SECRET').encode(),
                params.encode(),
                hashlib.sha256
            ).hexdigest()

            # Запит з підписом
            response = requests.get(
                "https://api.mexc.com/api/v3/capital/config/getall",
                params={'timestamp': timestamp, 'signature': signature},
                headers={'X-MEXC-APIKEY': os.getenv('MEXC_API_KEY')},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                mexc_networks_cache = {}

                # Нова структура відповіді (список валют)
                for currency in data:
                    coin = currency.get('coin')
                    networks = []
                    for network in currency.get('networkList', []):
                        networks.append({
                            'name': network.get('network'),
                            'deposit': network.get('depositEnable', False),
                            'withdraw': network.get('withdrawEnable', False),
                            'fee': str(network.get('withdrawFee', '0'))
                        })
                    if coin and networks:
                        mexc_networks_cache[coin] = networks

                mexc_cache_time = current_time
        except Exception as e:
            app.logger.error(f"MEXC networks error: {str(e)}")

    return mexc_networks_cache

def get_bitget_networks_for_coins():
    global bitget_networks_cache, bitget_cache_time
    current_time = time.time()
    if current_time - bitget_cache_time > CACHE_DURATION:
        try:
            # Використовуємо публічний API Bitget для отримання інформації про мережі
            response = requests.get("https://api.bitget.com/api/spot/v1/public/coins", timeout=10)
            if response.status_code == 200:
                data = response.json()
                bitget_networks_cache = {}
                if 'data' in data:
                    for coin in data['data']:
                        if 'coinName' in coin and 'chains' in coin:
                            coin_name = coin['coinName']
                            networks = []
                            chains = coin.get('chains', [])
                            if chains is None:
                                chains = []
                            for chain in chains:
                                networks.append({
                                    'name': chain.get('chain', ''),
                                    'deposit': chain.get('depositable', False),
                                    'withdraw': chain.get('withdrawable', False),
                                    'fee': str(chain.get('withdrawFee', '0'))
                                })
                            bitget_networks_cache[coin_name] = networks
                bitget_cache_time = current_time
        except Exception as e:
            app.logger.error(f"Bitget networks error: {str(e)}")
    return bitget_networks_cache

def get_cryptocom_networks_for_coins():
    global cryptocom_networks_cache, cryptocom_cache_time
    current_time = time.time()
    if current_time - cryptocom_cache_time > CACHE_DURATION:
        try:
            # Crypto.com має обмежений публічний API для інформації про мережі
            response = requests.get("https://api.crypto.com/v2/public/get-currencies", timeout=10)
            if response.status_code == 200:
                data = response.json()
                cryptocom_networks_cache = {}
                if 'result' in data and 'currencies' in data['result']:
                    for currency in data['result']['currencies']:
                        if 'currency' in currency:
                            currency_code = currency['currency']
                            if currency_code not in cryptocom_networks_cache:
                                cryptocom_networks_cache[currency_code] = []
                            cryptocom_networks_cache[currency_code].append({
                                'name': currency.get('network', currency_code),
                                'deposit': True,  # За замовчуванням вважаємо доступним
                                'withdraw': True,  # За замовчуванням вважаємо доступним
                                'fee': str(currency.get('fee', '0'))
                            })
                cryptocom_cache_time = current_time
        except Exception as e:
            app.logger.error(f"Crypto.com networks error: {str(e)}")
    return cryptocom_networks_cache

def get_networks_for_token(symbol):
    base_token = get_base_token(symbol)
    # Отримуємо мережі з усіх бірж
    networks_by_exchange = {
        'Binance': get_binance_networks_for_coins().get(base_token, []),
        'Bybit': get_bybit_networks_for_coins().get(base_token, []),
        'OKX': get_okx_networks_for_coins().get(base_token, []),
        'KuCoin': get_kucoin_networks_for_coins().get(base_token, []),
        'Gate.io': get_gateio_networks_for_coins().get(base_token, []),
        'Huobi': get_huobi_networks_for_coins().get(base_token, []),
        'Crypto.com': get_cryptocom_networks_for_coins().get(base_token, []),
        'MEXC': get_mexc_networks_for_coins().get(base_token, []),
        'Bitget': get_bitget_networks_for_coins().get(base_token, []),
    }
    # Формуємо список для виводу: по біржі - які мережі є
    result = []
    for exchange, networks in networks_by_exchange.items():
        if networks:
            net_names = ', '.join(sorted({net['name'] for net in networks}))
            result.append({'exchange': exchange, 'networks': net_names})
    return result

def is_stablecoin_pair(symbol):
    return symbol.endswith('USDT')

def get_table_data():
    exchange_data = {
        "Binance": get_binance_data(),
        "Bybit": get_bybit_data(),
        "OKX": get_okx_data(),
        "KuCoin": get_kucoin_data(),
        "Gate.io": get_gateio_data(),
        "Huobi": get_huobi_data(),
        "Crypto.com": get_cryptocom_data(),
        "MEXC": get_mexc_data(),
        "Bitget": get_bitget_data()
    }

    # Всі символи, присутні хоча б на двох біржах
    all_symbols = set()
    for data in exchange_data.values():
        all_symbols.update(data.keys())

        valid_symbols = [
            s for s in all_symbols
            if sum(1 for data in exchange_data.values() if s in data) >= 2
               and is_stablecoin_pair(s)
        ]

    table = []
    for symbol in sorted(valid_symbols):
        ask_prices = {}
        bid_prices = {}
        for ex, data in exchange_data.items():
            if symbol in data:
                ask_prices[ex] = data[symbol]['ask']
                bid_prices[ex] = data[symbol]['bid']

        if not ask_prices or not bid_prices:
            continue

        best_buy_ex, best_buy_price = min(ask_prices.items(), key=lambda x: x[1])
        best_sell_ex, best_sell_price = max(bid_prices.items(), key=lambda x: x[1])

        # Не на одній біржі
        if best_buy_ex == best_sell_ex:
            bids = bid_prices.copy()
            del bids[best_buy_ex]
            if bids:
                best_sell_ex, best_sell_price = max(bids.items(), key=lambda x: x[1])
            else:
                continue

        spread = ((best_sell_price - best_buy_price) / best_buy_price) * 100 if best_buy_price > 0 else 0
        networks = get_networks_for_token(symbol)
        if not networks:
            continue

        table.append({
            "pair": symbol,
            "buy_price": best_buy_price,
            "buy_exchange": best_buy_ex,
            "sell_price": best_sell_price,
            "sell_exchange": best_sell_ex,
            "spread": spread,
            "networks": networks
        })

    return sorted(table, key=lambda x: x['spread'], reverse=True)

def get_all_exchanges_data():

    return {
        "Binance": get_binance_data(),
        "Bybit": get_bybit_data(),
        "OKX": get_okx_data(),
        "KuCoin": get_kucoin_data(),
        "Gate.io": get_gateio_data(),
        "Huobi": get_huobi_data(),
        "MEXC": get_mexc_data(),
        "Bitget": get_bitget_data()
    }

from collections import defaultdict

def find_arbitrage_opportunities(exchange_data, min_spread=0.1):
    symbol_counts = defaultdict(int)
    for data in exchange_data.values():
        for symbol in data.keys():
            if is_stablecoin_pair(symbol):
                symbol_counts[symbol] += 1

    common_symbols = [s for s, count in symbol_counts.items() if count >= 2]

    opportunities = []
    for symbol in common_symbols:
        prices = {}
        for exchange, data in exchange_data.items():
            if symbol in data and data[symbol]['ask'] > 0:
                prices[exchange] = {
                    'bid': data[symbol]['bid'],
                    'ask': data[symbol]['ask']
                }

        if len(prices) < 2:
            continue

        best_ask = min(prices.items(), key=lambda x: x[1]['ask'])
        best_bid = max(prices.items(), key=lambda x: x[1]['bid'])

        spread_percent = ((best_bid[1]['bid'] - best_ask[1]['ask']) / best_ask[1]['ask']) * 100
        if spread_percent < min_spread:
            continue

        opportunities.append({
            'symbol': symbol,
            'buy_exchange': best_ask[0],
            'buy_price': best_ask[1]['ask'],
            'sell_exchange': best_bid[0],
            'sell_price': best_bid[1]['bid'],
            'spread': spread_percent,
            'profit': best_bid[1]['bid'] - best_ask[1]['ask']
        })

    return sorted(opportunities, key=lambda x: x['spread'], reverse=True)

# --- Flask routes ---
@app.route('/')
def home():
    return redirect(url_for('arbitrage'))

@app.route('/api/data')
def api_data():
    table = get_table_data()
    return render_template('table_body.html', table=table)

@app.route('/table')
def table_ajax():
    selected_networks = request.args.getlist('networks[]')
    min_profit = request.args.get('min_profit', default=0, type=float)
    table = get_table_data()

    if selected_networks:
        filtered_table = []
        for row in table:
            if any(net["name"] in selected_networks for net in row["networks"]):
                filtered_table.append(row)
        table = filtered_table

    table = [row for row in table if row['spread'] >= min_profit]
    return render_template('table_body.html', table=table)

@app.route('/tokens')
def tokens():
    exchanges_data = {
        "binance": format_tokens(get_binance_data(), get_binance_networks_for_coins()),
        "bybit": format_tokens(get_bybit_data(), get_bybit_networks_for_coins()),
        "okx": format_tokens(get_okx_data(), get_okx_networks_for_coins()),
        "kucoin": format_tokens(get_kucoin_data(), get_kucoin_networks_for_coins()),
        "gateio": format_tokens(get_gateio_data(), get_gateio_networks_for_coins()),
        "huobi": format_tokens(get_huobi_data(), get_huobi_networks_for_coins()),
        "cryptocom": format_tokens(get_cryptocom_data(), get_cryptocom_networks_for_coins()),
        "mexc": format_tokens(get_mexc_data(), get_mexc_networks_for_coins()),
        "bitget": format_tokens(get_bitget_data(), get_bitget_networks_for_coins())
    }
    return render_template('tokens.html', exchanges=exchanges_data)

def format_tokens(exchange_data, networks_data):
    tokens = []
    for symbol, data in exchange_data.items():
        base_token = get_base_token(symbol)
        token_networks = []

        if base_token in networks_data:
            for net in networks_data[base_token]:
                fee = net.get('fee', '0')
                label = f"{net['name']} ({fee})"
                if net['name'] != "DGB" and fee != "0":
                    label = f"{net['name']} ({fee} USDT)"

                token_networks.append({
                    'name': net['name'],
                    'label': label
                })

        # Розрахунок внутрішнього спреду на біржі
        spread = ((data['bid'] - data['ask']) / data['ask']) * 100 if data['ask'] > 0 else 0

        tokens.append({
            'symbol': symbol,
            'bid': data['bid'],
            'ask': data['ask'],
            'last': data.get('last', 0),
            'volume': data.get('volume', 0) if 'volume' in data else 0,
            'spread': spread,
            'networks': token_networks
        })

    return sorted(tokens, key=lambda x: x['symbol'])

@app.template_filter('humanize')
def humanize_filter(value):
    try:
        value = float(value)
        if value >= 1_000_000:
            return f"{value/1_000_000:.2f}M"
        elif value >= 1_000:
            return f"{value/1_000:.1f}K"
        return f"{value:.2f}"
    except Exception:
        return value

@app.route('/api/tokens-data')
def api_tokens_data():
    exchanges = {
        "binance": format_tokens(get_binance_data(), get_binance_networks_for_coins()),
        "bybit": format_tokens(get_bybit_data(), get_bybit_networks_for_coins()),
        "okx": format_tokens(get_okx_data(), get_okx_networks_for_coins()),
        "kucoin": format_tokens(get_kucoin_data(), get_kucoin_networks_for_coins()),
        "gateio": format_tokens(get_gateio_data(), get_gateio_networks_for_coins()),
        "huobi": format_tokens(get_huobi_data(), get_huobi_networks_for_coins()),
        "cryptocom": format_tokens(get_cryptocom_data(), get_cryptocom_networks_for_coins()),
        "mexc": format_tokens(get_mexc_data(), get_mexc_networks_for_coins()),
        "bitget": format_tokens(get_bitget_data(), get_bitget_networks_for_coins())
    }
    return render_template('tokens_table_body.html', exchanges=exchanges)

@app.route('/api/tokens/<exchange_id>')
def api_tokens_by_exchange(exchange_id):
    exchanges = {
        "binance": (get_binance_data, get_binance_networks_for_coins),
        "bybit": (get_bybit_data, get_bybit_networks_for_coins),
        "okx": (get_okx_data, get_okx_networks_for_coins),
        "kucoin": (get_kucoin_data, get_kucoin_networks_for_coins),
        "gateio": (get_gateio_data, get_gateio_networks_for_coins),
        "huobi": (get_huobi_data, get_huobi_networks_for_coins),
        "cryptocom": (get_cryptocom_data, get_cryptocom_networks_for_coins),
        "mexc": (get_mexc_data, get_mexc_networks_for_coins),
        "bitget": (get_bitget_data, get_bitget_networks_for_coins)
    }

    if exchange_id not in exchanges:
        return "Exchange not found", 404

    data_func, networks_func = exchanges[exchange_id]

    try:
        data = data_func()
        networks = networks_func()

        if not data or not networks:
            return "Data not available", 500

        tokens = format_tokens(data, networks)
    except Exception as e:
        app.logger.error(f"Error processing {exchange_id}: {str(e)}")
        return "Internal Server Error", 500

    return render_template('tokens_table_body.html', tokens=tokens)

@app.route('/arbitrage')
def arbitrage():
    exchange_data = get_all_exchanges_data()
    opportunities = find_arbitrage_opportunities(exchange_data)
    return render_template('arbitrage.html', opportunities=opportunities)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
