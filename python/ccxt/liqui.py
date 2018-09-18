# -*- coding: utf-8 -*-

# PLEASE DO NOT EDIT THIS FILE, IT IS GENERATED AND WILL BE OVERWRITTEN:
# https://github.com/ccxt/ccxt/blob/master/CONTRIBUTING.md#how-to-contribute-code

from ccxt.base.exchange import Exchange

# -----------------------------------------------------------------------------

try:
    basestring  # Python 3
except NameError:
    basestring = str  # Python 2
import hashlib
import json
from ccxt.base.errors import ExchangeError
from ccxt.base.errors import AuthenticationError
from ccxt.base.errors import InsufficientFunds
from ccxt.base.errors import InvalidOrder
from ccxt.base.errors import OrderNotFound
from ccxt.base.errors import DDoSProtection
from ccxt.base.errors import ExchangeNotAvailable


class liqui (Exchange):

    def describe(self):
        return self.deep_extend(super(liqui, self).describe(), {
            'id': 'liqui',
            'name': 'Liqui',
            'countries': ['UA'],
            'rateLimit': 3000,
            'version': '3',
            'userAgent': self.userAgents['chrome'],
            'has': {
                'CORS': False,
                'createMarketOrder': False,
                'fetchOrderBooks': True,
                'fetchOrder': True,
                'fetchOrders': 'emulated',
                'fetchOpenOrders': True,
                'fetchClosedOrders': 'emulated',
                'fetchTickers': True,
                'fetchMyTrades': True,
                'withdraw': True,
            },
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27982022-75aea828-63a0-11e7-9511-ca584a8edd74.jpg',
                'api': {
                    'public': 'https://api.liqui.io/api',
                    'private': 'https://api.liqui.io/tapi',
                },
                'www': 'https://liqui.io',
                'doc': 'https://liqui.io/api',
                'fees': 'https://liqui.io/fee',
            },
            'api': {
                'public': {
                    'get': [
                        'info',
                        'ticker/{pair}',
                        'depth/{pair}',
                        'trades/{pair}',
                    ],
                },
                'private': {
                    'post': [
                        'getInfo',
                        'Trade',
                        'ActiveOrders',
                        'OrderInfo',
                        'CancelOrder',
                        'TradeHistory',
                        'CoinDepositAddress',
                        'WithdrawCoin',
                        'CreateCoupon',
                        'RedeemCoupon',
                    ],
                },
            },
            'fees': {
                'trading': {
                    'maker': 0.001,
                    'taker': 0.0025,
                },
                'funding': {
                    'tierBased': False,
                    'percentage': False,
                    'withdraw': {},
                    'deposit': {},
                },
            },
            'commonCurrencies': {
                'DSH': 'DASH',
            },
            'exceptions': {
                '803': InvalidOrder,  # "Count could not be less than 0.001."(selling below minAmount)
                '804': InvalidOrder,  # "Count could not be more than 10000."(buying above maxAmount)
                '805': InvalidOrder,  # "price could not be less than X."(minPrice violation on buy & sell)
                '806': InvalidOrder,  # "price could not be more than X."(maxPrice violation on buy & sell)
                '807': InvalidOrder,  # "cost could not be less than X."(minCost violation on buy & sell)
                '831': InsufficientFunds,  # "Not enougth X to create buy order."(buying with balance.quote < order.cost)
                '832': InsufficientFunds,  # "Not enougth X to create sell order."(selling with balance.base < order.amount)
                '833': OrderNotFound,  # "Order with id X was not found."(cancelling non-existent, closed and cancelled order)
            },
        })

    def calculate_fee(self, symbol, type, side, amount, price, takerOrMaker='taker', params={}):
        market = self.markets[symbol]
        key = 'quote'
        rate = market[takerOrMaker]
        cost = float(self.cost_to_precision(symbol, amount * rate))
        if side == 'sell':
            cost *= price
        else:
            key = 'base'
        return {
            'type': takerOrMaker,
            'currency': market[key],
            'rate': rate,
            'cost': cost,
        }

    def get_base_quote_from_market_id(self, id):
        uppercase = id.upper()
        base, quote = uppercase.split('_')
        base = self.common_currency_code(base)
        quote = self.common_currency_code(quote)
        return [base, quote]

    def fetch_markets(self):
        response = self.publicGetInfo()
        markets = response['pairs']
        keys = list(markets.keys())
        result = []
        for i in range(0, len(keys)):
            id = keys[i]
            market = markets[id]
            base, quote = self.get_base_quote_from_market_id(id)
            symbol = base + '/' + quote
            precision = {
                'amount': self.safe_integer(market, 'decimal_places'),
                'price': self.safe_integer(market, 'decimal_places'),
            }
            amountLimits = {
                'min': self.safe_float(market, 'min_amount'),
                'max': self.safe_float(market, 'max_amount'),
            }
            priceLimits = {
                'min': self.safe_float(market, 'min_price'),
                'max': self.safe_float(market, 'max_price'),
            }
            costLimits = {
                'min': self.safe_float(market, 'min_total'),
            }
            limits = {
                'amount': amountLimits,
                'price': priceLimits,
                'cost': costLimits,
            }
            hidden = self.safe_integer(market, 'hidden')
            active = (hidden == 0)
            result.append({
                'id': id,
                'symbol': symbol,
                'base': base,
                'quote': quote,
                'active': active,
                'taker': market['fee'] / 100,
                'precision': precision,
                'limits': limits,
                'info': market,
            })
        return result

    def fetch_balance(self, params={}):
        self.load_markets()
        response = self.privatePostGetInfo()
        balances = response['return']
        result = {'info': balances}
        funds = balances['funds']
        currencies = list(funds.keys())
        for c in range(0, len(currencies)):
            currency = currencies[c]
            uppercase = currency.upper()
            uppercase = self.common_currency_code(uppercase)
            total = None
            used = None
            if balances['open_orders'] == 0:
                total = funds[currency]
                used = 0.0
            account = {
                'free': funds[currency],
                'used': used,
                'total': total,
            }
            result[uppercase] = account
        return self.parse_balance(result)

    def fetch_order_book(self, symbol, limit=None, params={}):
        self.load_markets()
        market = self.market(symbol)
        request = {
            'pair': market['id'],
        }
        if limit is not None:
            request['limit'] = limit  # default = 150, max = 2000
        response = self.publicGetDepthPair(self.extend(request, params))
        market_id_in_reponse = (market['id'] in list(response.keys()))
        if not market_id_in_reponse:
            raise ExchangeError(self.id + ' ' + market['symbol'] + ' order book is empty or not available')
        orderbook = response[market['id']]
        return self.parse_order_book(orderbook)

    def fetch_order_books(self, symbols=None, params={}):
        self.load_markets()
        ids = None
        if symbols is None:
            ids = '-'.join(self.ids)
            # max URL length is 2083 symbols, including http schema, hostname, tld, etc...
            if len(ids) > 2048:
                numIds = len(self.ids)
                raise ExchangeError(self.id + ' has ' + str(numIds) + ' symbols exceeding max URL length, you are required to specify a list of symbols in the first argument to fetchOrderBooks')
        else:
            ids = self.market_ids(symbols)
            ids = '-'.join(ids)
        response = self.publicGetDepthPair(self.extend({
            'pair': ids,
        }, params))
        result = {}
        ids = list(response.keys())
        for i in range(0, len(ids)):
            id = ids[i]
            symbol = id
            if id in self.markets_by_id:
                market = self.markets_by_id[id]
                symbol = market['symbol']
            result[symbol] = self.parse_order_book(response[id])
        return result

    def parse_ticker(self, ticker, market=None):
        timestamp = ticker['updated'] * 1000
        symbol = None
        if market is not None:
            symbol = market['symbol']
        last = self.safe_float(ticker, 'last')
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': self.safe_float(ticker, 'high'),
            'low': self.safe_float(ticker, 'low'),
            'bid': self.safe_float(ticker, 'buy'),
            'bidVolume': None,
            'ask': self.safe_float(ticker, 'sell'),
            'askVolume': None,
            'vwap': None,
            'open': None,
            'close': last,
            'last': last,
            'previousClose': None,
            'change': None,
            'percentage': None,
            'average': self.safe_float(ticker, 'avg'),
            'baseVolume': self.safe_float(ticker, 'vol_cur'),
            'quoteVolume': self.safe_float(ticker, 'vol'),
            'info': ticker,
        }

    def fetch_tickers(self, symbols=None, params={}):
        self.load_markets()
        ids = None
        if symbols is None:
            ids = '-'.join(self.ids)
            # max URL length is 2083 symbols, including http schema, hostname, tld, etc...
            if len(ids) > 2048:
                numIds = len(self.ids)
                raise ExchangeError(self.id + ' has ' + str(numIds) + ' symbols exceeding max URL length, you are required to specify a list of symbols in the first argument to fetchTickers')
        else:
            ids = self.market_ids(symbols)
            ids = '-'.join(ids)
        tickers = self.publicGetTickerPair(self.extend({
            'pair': ids,
        }, params))
        result = {}
        keys = list(tickers.keys())
        for k in range(0, len(keys)):
            id = keys[k]
            ticker = tickers[id]
            symbol = id
            market = None
            if id in self.markets_by_id:
                market = self.markets_by_id[id]
                symbol = market['symbol']
            result[symbol] = self.parse_ticker(ticker, market)
        return result

    def fetch_ticker(self, symbol, params={}):
        tickers = self.fetch_tickers([symbol], params)
        return tickers[symbol]

    def parse_trade(self, trade, market=None):
        timestamp = int(trade['timestamp']) * 1000
        side = trade['type']
        if side == 'ask':
            side = 'sell'
        if side == 'bid':
            side = 'buy'
        price = self.safe_float(trade, 'price')
        if 'rate' in trade:
            price = self.safe_float(trade, 'rate')
        id = self.safe_string(trade, 'tid')
        if 'trade_id' in trade:
            id = self.safe_string(trade, 'trade_id')
        order = self.safe_string(trade, self.get_order_id_key())
        if 'pair' in trade:
            marketId = trade['pair']
            market = self.markets_by_id[marketId]
        symbol = None
        if market is not None:
            symbol = market['symbol']
        amount = trade['amount']
        type = 'limit'  # all trades are still limit trades
        isYourOrder = self.safe_value(trade, 'is_your_order')
        takerOrMaker = 'taker'
        if isYourOrder is not None:
            if isYourOrder:
                takerOrMaker = 'maker'
        fee = self.calculate_fee(symbol, type, side, amount, price, takerOrMaker)
        return {
            'id': id,
            'order': order,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': symbol,
            'type': type,
            'side': side,
            'price': price,
            'amount': amount,
            'fee': fee,
            'info': trade,
        }

    def fetch_trades(self, symbol, since=None, limit=None, params={}):
        self.load_markets()
        market = self.market(symbol)
        request = {
            'pair': market['id'],
        }
        if limit is not None:
            request['limit'] = limit
        response = self.publicGetTradesPair(self.extend(request, params))
        if isinstance(response, list):
            numElements = len(response)
            if numElements == 0:
                return []
        return self.parse_trades(response[market['id']], market, since, limit)

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        if type == 'market':
            raise ExchangeError(self.id + ' allows limit orders only')
        self.load_markets()
        market = self.market(symbol)
        request = {
            'pair': market['id'],
            'type': side,
            'amount': self.amount_to_precision(symbol, amount),
            'rate': self.price_to_precision(symbol, price),
        }
        price = float(price)
        amount = float(amount)
        response = self.privatePostTrade(self.extend(request, params))
        id = None
        status = 'open'
        filled = 0.0
        remaining = amount
        if 'return' in response:
            id = self.safe_string(response['return'], self.get_order_id_key())
            if id == '0':
                id = self.safe_string(response['return'], 'init_order_id')
                status = 'closed'
            filled = self.safe_float(response['return'], 'received', 0.0)
            remaining = self.safe_float(response['return'], 'remains', amount)
        timestamp = self.milliseconds()
        order = {
            'id': id,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'lastTradeTimestamp': None,
            'status': status,
            'symbol': symbol,
            'type': type,
            'side': side,
            'price': price,
            'cost': price * filled,
            'amount': amount,
            'remaining': remaining,
            'filled': filled,
            'fee': None,
            # 'trades': self.parse_trades(order['trades'], market),
        }
        self.orders[id] = order
        return self.extend({'info': response}, order)

    def get_order_id_key(self):
        return 'order_id'

    def cancel_order(self, id, symbol=None, params={}):
        self.load_markets()
        request = {}
        idKey = self.get_order_id_key()
        request[idKey] = id
        response = self.privatePostCancelOrder(self.extend(request, params))
        if id in self.orders:
            self.orders[id]['status'] = 'canceled'
        return response

    def parse_order_status(self, status):
        statuses = {
            '0': 'open',
            '1': 'closed',
            '2': 'canceled',
            '3': 'canceled',  # or partially-filled and still open? https://github.com/ccxt/ccxt/issues/1594
        }
        if status in statuses:
            return statuses[status]
        return status

    def parse_order(self, order, market=None):
        id = str(order['id'])
        status = self.parse_order_status(self.safe_string(order, 'status'))
        timestamp = int(order['timestamp_created']) * 1000
        symbol = None
        if market is None:
            market = self.markets_by_id[order['pair']]
        if market is not None:
            symbol = market['symbol']
        remaining = None
        amount = None
        price = self.safe_float(order, 'rate')
        filled = None
        cost = None
        if 'start_amount' in order:
            amount = self.safe_float(order, 'start_amount')
            remaining = self.safe_float(order, 'amount')
        else:
            remaining = self.safe_float(order, 'amount')
            if id in self.orders:
                amount = self.orders[id]['amount']
        if amount is not None:
            if remaining is not None:
                filled = amount - remaining
                cost = price * filled
        fee = None
        result = {
            'info': order,
            'id': id,
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'lastTradeTimestamp': None,
            'type': 'limit',
            'side': order['type'],
            'price': price,
            'cost': cost,
            'amount': amount,
            'remaining': remaining,
            'filled': filled,
            'status': status,
            'fee': fee,
        }
        return result

    def parse_orders(self, orders, market=None, since=None, limit=None):
        ids = list(orders.keys())
        result = []
        for i in range(0, len(ids)):
            id = ids[i]
            order = orders[id]
            extended = self.extend(order, {'id': id})
            result.append(self.parse_order(extended, market))
        return self.filter_by_since_limit(result, since, limit)

    def fetch_order(self, id, symbol=None, params={}):
        self.load_markets()
        response = self.privatePostOrderInfo(self.extend({
            'order_id': int(id),
        }, params))
        id = str(id)
        newOrder = self.parse_order(self.extend({'id': id}, response['return'][id]))
        oldOrder = self.orders[id] if (id in list(self.orders.keys())) else {}
        self.orders[id] = self.extend(oldOrder, newOrder)
        return self.orders[id]

    def update_cached_orders(self, openOrders, symbol):
        # update local cache with open orders
        # self will add unseen orders and overwrite existing ones
        for j in range(0, len(openOrders)):
            id = openOrders[j]['id']
            self.orders[id] = openOrders[j]
        openOrdersIndexedById = self.index_by(openOrders, 'id')
        cachedOrderIds = list(self.orders.keys())
        for k in range(0, len(cachedOrderIds)):
            # match each cached order to an order in the open orders array
            # possible reasons why a cached order may be missing in the open orders array:
            # - order was closed or canceled -> update cache
            # - symbol mismatch(e.g. cached BTC/USDT, fetched ETH/USDT) -> skip
            cachedOrderId = cachedOrderIds[k]
            cachedOrder = self.orders[cachedOrderId]
            if not(cachedOrderId in list(openOrdersIndexedById.keys())):
                # cached order is not in open orders array
                # if we fetched orders by symbol and it doesn't match the cached order -> won't update the cached order
                if symbol is not None and symbol != cachedOrder['symbol']:
                    continue
                # cached order is absent from the list of open orders -> mark the cached order as closed
                if cachedOrder['status'] == 'open':
                    cachedOrder = self.extend(cachedOrder, {
                        'status': 'closed',  # likewise it might have been canceled externally(unnoticed by "us")
                        'cost': None,
                        'filled': cachedOrder['amount'],
                        'remaining': 0.0,
                    })
                    if cachedOrder['cost'] is None:
                        if cachedOrder['filled'] is not None:
                            cachedOrder['cost'] = cachedOrder['filled'] * cachedOrder['price']
                    self.orders[cachedOrderId] = cachedOrder
        return self.to_array(self.orders)

    def fetch_orders(self, symbol=None, since=None, limit=None, params={}):
        if 'fetchOrdersRequiresSymbol' in self.options:
            if self.options['fetchOrdersRequiresSymbol']:
                if symbol is None:
                    raise ExchangeError(self.id + ' fetchOrders requires a symbol argument')
        self.load_markets()
        request = {}
        market = None
        if symbol is not None:
            market = self.market(symbol)
            request['pair'] = market['id']
        response = self.privatePostActiveOrders(self.extend(request, params))
        # liqui etc can only return 'open' orders(i.e. no way to fetch 'closed' orders)
        openOrders = []
        if 'return' in response:
            openOrders = self.parse_orders(response['return'], market)
        allOrders = self.update_cached_orders(openOrders, symbol)
        result = self.filter_by_symbol(allOrders, symbol)
        return self.filter_by_since_limit(result, since, limit)

    def fetch_open_orders(self, symbol=None, since=None, limit=None, params={}):
        orders = self.fetch_orders(symbol, since, limit, params)
        return self.filter_by(orders, 'status', 'open')

    def fetch_closed_orders(self, symbol=None, since=None, limit=None, params={}):
        orders = self.fetch_orders(symbol, since, limit, params)
        return self.filter_by(orders, 'status', 'closed')

    def fetch_my_trades(self, symbol=None, since=None, limit=None, params={}):
        self.load_markets()
        market = None
        request = {
            # 'from': 123456789,  # trade ID, from which the display starts numerical 0(test result: liqui ignores self field)
            # 'count': 1000,  # the number of trades for display numerical, default = 1000
            # 'from_id': trade ID, from which the display starts numerical 0
            # 'end_id': trade ID on which the display ends numerical ∞
            # 'order': 'ASC',  # sorting, default = DESC(test result: liqui ignores self field, most recent trade always goes last)
            # 'since': 1234567890,  # UTC start time, default = 0(test result: liqui ignores self field)
            # 'end': 1234567890,  # UTC end time, default = ∞(test result: liqui ignores self field)
            # 'pair': 'eth_btc',  # default = all markets
        }
        if symbol is not None:
            market = self.market(symbol)
            request['pair'] = market['id']
        if limit is not None:
            request['count'] = int(limit)
        if since is not None:
            request['since'] = int(since / 1000)
        response = self.privatePostTradeHistory(self.extend(request, params))
        trades = []
        if 'return' in response:
            trades = response['return']
        return self.parse_trades(trades, market, since, limit)

    def withdraw(self, currency, amount, address, tag=None, params={}):
        self.check_address(address)
        self.load_markets()
        response = self.privatePostWithdrawCoin(self.extend({
            'coinName': currency,
            'amount': float(amount),
            'address': address,
        }, params))
        return {
            'info': response,
            'id': response['return']['tId'],
        }

    def sign_body_with_secret(self, body):
        return self.hmac(self.encode(body), self.encode(self.secret), hashlib.sha512)

    def get_version_string(self):
        return '/' + self.version

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'][api]
        query = self.omit(params, self.extract_params(path))
        if api == 'private':
            self.check_required_credentials()
            nonce = self.nonce()
            body = self.urlencode(self.extend({
                'nonce': nonce,
                'method': path,
            }, query))
            signature = self.sign_body_with_secret(body)
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Key': self.apiKey,
                'Sign': signature,
            }
        elif api == 'public':
            url += self.get_version_string() + '/' + self.implode_params(path, params)
            if query:
                url += '?' + self.urlencode(query)
        else:
            url += '/' + self.implode_params(path, params)
            if method == 'GET':
                if query:
                    url += '?' + self.urlencode(query)
            else:
                if query:
                    body = self.json(query)
                    headers = {
                        'Content-Type': 'application/json',
                    }
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def handle_errors(self, httpCode, reason, url, method, headers, body):
        if not isinstance(body, basestring):
            return  # fallback to default error handler
        if len(body) < 2:
            return  # fallback to default error handler
        if (body[0] == '{') or (body[0] == '['):
            response = json.loads(body)
            if 'success' in response:
                #
                # 1 - Liqui only returns the integer 'success' key from their private API
                #
                #     {"success": 1, ...} httpCode == 200
                #     {"success": 0, ...} httpCode == 200
                #
                # 2 - However, exchanges derived from Liqui, can return non-integers
                #
                #     It can be a numeric string
                #     {"sucesss": "1", ...}
                #     {"sucesss": "0", ...}, httpCode >= 200(can be 403, 502, etc)
                #
                #     Or just a string
                #     {"success": "true", ...}
                #     {"success": "false", ...}, httpCode >= 200
                #
                #     Or a boolean
                #     {"success": True, ...}
                #     {"success": False, ...}, httpCode >= 200
                #
                # 3 - Oversimplified, Python PEP8 forbids comparison operator(==) of different types
                #
                # 4 - We do not want to copy-paste and duplicate the code of self handler to other exchanges derived from Liqui
                #
                # To cover points 1, 2, 3 and 4 combined self handler should work like self:
                #
                success = self.safe_value(response, 'success', False)
                if isinstance(success, basestring):
                    if (success == 'true') or (success == '1'):
                        success = True
                    else:
                        success = False
                if not success:
                    code = self.safe_string(response, 'code')
                    message = self.safe_string(response, 'error')
                    feedback = self.id + ' ' + self.json(response)
                    exceptions = self.exceptions
                    if code in exceptions:
                        raise exceptions[code](feedback)
                    # need a second error map for these messages, apparently...
                    # in fact, we can use the same .exceptions with string-keys to save some loc here
                    if message == 'invalid api key':
                        raise AuthenticationError(feedback)
                    elif message == 'invalid sign':
                        raise AuthenticationError(feedback)
                    elif message == 'api key dont have trade permission':
                        raise AuthenticationError(feedback)
                    elif message.find('invalid parameter') >= 0:  # errorCode 0, returned on buy(symbol, 0, 0)
                        raise InvalidOrder(feedback)
                    elif message == 'invalid order':
                        raise InvalidOrder(feedback)
                    elif message == 'Requests too often':
                        raise DDoSProtection(feedback)
                    elif message == 'not available':
                        raise ExchangeNotAvailable(feedback)
                    elif message == 'data unavailable':
                        raise ExchangeNotAvailable(feedback)
                    elif message == 'external service unavailable':
                        raise ExchangeNotAvailable(feedback)
                    else:
                        raise ExchangeError(feedback)
