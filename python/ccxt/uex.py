# -*- coding: utf-8 -*-

# PLEASE DO NOT EDIT THIS FILE, IT IS GENERATED AND WILL BE OVERWRITTEN:
# https://github.com/ccxt/ccxt/blob/master/CONTRIBUTING.md#how-to-contribute-code

from ccxt.base.exchange import Exchange

# -----------------------------------------------------------------------------

try:
    basestring  # Python 3
except NameError:
    basestring = str  # Python 2
import json
from ccxt.base.errors import ExchangeError
from ccxt.base.errors import AuthenticationError
from ccxt.base.errors import PermissionDenied
from ccxt.base.errors import InsufficientFunds
from ccxt.base.errors import InvalidOrder
from ccxt.base.errors import OrderNotFound
from ccxt.base.errors import ExchangeNotAvailable


class bittrex (Exchange):

    def describe(self):
        return self.deep_extend(super(bittrex, self).describe(), {
            'id': 'uex',
            'name': 'UEX',
            'countries': ['SG', 'US'],
            'version': 'v1.0.3',
            'rateLimit': 1500,
            'certified': True,
            # new metainfo interface
            'has': {
                'CORS': False,
                'fetchMyTrades': True,
                'fetchOHLCV': True,
                'fetchOrder': True,
                'fetchOpenOrders': True,
                'fetchClosedOrders': True,
            },
            'timeframes': {
                '1m': '1',
                '5m': '5',
                '15m': '15',
                '30m': '30',
                '1h': '60',
                '2h': '120',
                '3h': '180',
                '4h': '240',
                '6h': '360',
                '12h': '720',
                '1d': '1440',
            },
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/43788872-4251c80c-9a77-11e8-8ab4-dca9723cd7be.jpg',
                'api': 'https://open-api.uex.com/open/api',
                'www': 'https://www.uex.com',
                'doc': 'https://download.uex.com/doc/UEX-API-English-1.0.3.pdf',
                'fees': 'https://www.uex.com/footer/ufees.html',
                'referral': 'https://www.uex.com/signup.html?code=VAGQLL',
            },
            'api': {
                'public': {
                    'get': [
                        'common/symbols',
                        'get_records',  # ohlcvs
                        'get_ticker',
                        'get_trades',
                        'market_dept',  # dept here is not a typo... they mean depth
                    ],
                },
                'private': {
                    'get': [
                        'user/account',
                        'market',  # an assoc array of market ids to corresponding prices traded most recently(prices of last trades per market)
                        'order_info',
                        'new_order',  # open orders
                        'all_order',
                        'all_trade',
                    ],
                    'post': [
                        'create_order',
                        'cancel_order',
                    ],
                },
            },
            'fees': {
                'trading': {
                    'tierBased': False,
                    'percentage': True,
                    'maker': 0.0025,
                    'taker': 0.0025,
                },
            },
            'exceptions': {
                # descriptions from ↓ exchange
                # '0': 'no error',  # succeed
                '4': InsufficientFunds,  # {"code":"4","msg":"余额不足:0E-16","data":null}
                '5': InvalidOrder,  # fail to order {"code":"5","msg":"Price fluctuates more than1000.0%","data":null}
                '6': InvalidOrder,  # the quantity value less than the minimum one {"code":"6","msg":"数量小于最小值:0.001","data":null}
                '7': InvalidOrder,  # the quantity value more than the maximum one {"code":"7","msg":"数量大于最大值:10000","data":null}
                '8': InvalidOrder,  # fail to cancel order
                '9': ExchangeError,  # transaction be frozen
                '13': ExchangeError,  # Sorry, the program made an error, please contact with the manager.
                '19': InsufficientFunds,  # Available balance is insufficient.
                '22': OrderNotFound,  # The order does not exist. {"code":"22","msg":"not exist order","data":null}
                '23': InvalidOrder,  # Lack of parameters of numbers of transaction
                '24': InvalidOrder,  # Lack of parameters of transaction price
                '100001': ExchangeError,  # System is abnormal
                '100002': ExchangeNotAvailable,  # Update System
                '100004': ExchangeError,  # {"code":"100004","msg":"request parameter illegal","data":null}
                '100005': AuthenticationError,  # {"code":"100005","msg":"request sign illegal","data":null}
                '100007': PermissionDenied,  # illegal IP
                '110002': ExchangeError,  # unknown currency code
                '110003': AuthenticationError,  # fund password error
                '110004': AuthenticationError,  # fund password error
                '110005': InsufficientFunds,  # Available balance is insufficient.
                '110020': AuthenticationError,  # Username does not exist.
                '110023': AuthenticationError,  # Phone number is registered.
                '110024': AuthenticationError,  # Email box is registered.
                '110025': PermissionDenied,  # Account is locked by background manager
                '110032': PermissionDenied,  # The user has no authority to do self operation.
                '110033': ExchangeError,  # fail to recharge
                '110034': ExchangeError,  # fail to withdraw
                '-100': ExchangeError,  # {"code":"-100","msg":"Your request path is not exist or you can try method GET/POST.","data":null}
            },
            'requiredCredentials': {
                'apiKey': True,
                'secret': True,
                'password': True,
            },
            'options': {
                'createMarketBuyOrderRequiresPrice': True,
            },
        })

    def fetch_markets(self):
        response = self.publicGetCommonSymbols()
        #
        #     {code:   "0",
        #        msg:   "suc",
        #       data: [{          symbol: "btcusdt",
        #                       count_coin: "usdt",
        #                 amount_precision:  3,
        #                        base_coin: "btc",
        #                  price_precision:  2         },
        #               {          symbol: "ethusdt",
        #                       count_coin: "usdt",
        #                 amount_precision:  3,
        #                        base_coin: "eth",
        #                  price_precision:  2         },
        #               {          symbol: "ethbtc",
        #                       count_coin: "btc",
        #                 amount_precision:  3,
        #                        base_coin: "eth",
        #                  price_precision:  6        },
        #
        result = []
        markets = response['data']
        for i in range(0, len(markets)):
            market = markets[i]
            id = market['symbol']
            baseId = market['base_coin']
            quoteId = market['count_coin']
            base = baseId.upper()
            quote = quoteId.upper()
            base = self.common_currency_code(base)
            quote = self.common_currency_code(quote)
            symbol = base + '/' + quote
            precision = {
                'amount': market['amount_precision'],
                'price': market['price_precision'],
            }
            active = True
            result.append({
                'id': id,
                'symbol': symbol,
                'base': base,
                'quote': quote,
                'baseId': baseId,
                'quoteId': quoteId,
                'active': active,
                'info': market,
                'precision': precision,
                'limits': {
                    'amount': {
                        'min': None,
                        'max': None,
                    },
                    'price': {
                        'min': None,
                        'max': None,
                    },
                    'cost': {
                        'min': None,
                        'max': None,
                    },
                },
            })
        return result

    def fetch_balance(self, params={}):
        self.load_markets()
        response = self.privateGetUserAccount(params)
        #
        #     {code:   "0",
        #        msg:   "suc",
        #       data: {total_asset:   "0.00000000",
        #                 coin_list: [{     normal: "0.00000000",
        #                                btcValuatin: "0.00000000",
        #                                     locked: "0.00000000",
        #                                       coin: "usdt"        },
        #                              {     normal: "0.00000000",
        #                                btcValuatin: "0.00000000",
        #                                     locked: "0.00000000",
        #                                       coin: "btc"         },
        #                              {     normal: "0.00000000",
        #                                btcValuatin: "0.00000000",
        #                                     locked: "0.00000000",
        #                                       coin: "eth"         },
        #                              {     normal: "0.00000000",
        #                                btcValuatin: "0.00000000",
        #                                     locked: "0.00000000",
        #                                       coin: "ren"         },
        #
        balances = response['data']['coin_list']
        result = {'info': balances}
        for i in range(0, len(balances)):
            balance = balances[i]
            currencyId = balance['coin']
            code = currencyId.upper()
            if currencyId in self.currencies_by_id:
                code = self.currencies_by_id[currencyId]['code']
            else:
                code = self.common_currency_code(code)
            account = self.account()
            free = float(balance['normal'])
            used = float(balance['locked'])
            total = self.sum(free, used)
            account['free'] = free
            account['used'] = used
            account['total'] = total
            result[code] = account
        return self.parse_balance(result)

    def fetch_order_book(self, symbol, limit=None, params={}):
        self.load_markets()
        response = self.publicGetMarketDept(self.extend({
            'symbol': self.market_id(symbol),
            'type': 'step0',  # step1, step2 from most detailed to least detailed
        }, params))
        #
        #     {code:   "0",
        #        msg:   "suc",
        #       data: {tick: {asks: [["0.05824200", 9.77],
        #                               ["0.05830000", 7.81],
        #                               ["0.05832900", 8.59],
        #                               ["0.10000000", 0.001]  ],
        #                       bids: [["0.05780000", 8.25],
        #                               ["0.05775000", 8.12],
        #                               ["0.05773200", 8.57],
        #                               ["0.00010000", 0.79]   ],
        #                       time:    1533412622463            }} }
        #
        return self.parse_order_book(response['data']['tick'], response['data']['time'])

    def parse_ticker(self, ticker, market=None):
        #
        #     {code:   "0",
        #        msg:   "suc",
        #       data: {symbol: "ETHBTC",
        #                 high:  0.058426,
        #                  vol:  19055.875,
        #                 last:  0.058019,
        #                  low:  0.055802,
        #               change:  0.03437271,
        #                  buy: "0.05780000",
        #                 sell: "0.05824200",
        #                 time:  1533413083184} }
        #
        timestamp = self.safe_integer(ticker, 'time')
        symbol = None
        if market is None:
            marketId = self.safe_string(ticker, 'symbol')
            marketId = marketId.lower()
            if marketId in self.markets_by_id:
                market = self.markets_by_id[marketId]
        if market is not None:
            symbol = market['symbol']
        last = self.safe_float(ticker, 'last')
        change = self.safe_float(ticker, 'change')
        percentage = change * 100
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
            'percentage': percentage,
            'average': None,
            'baseVolume': self.safe_float(ticker, 'vol'),
            'quoteVolume': None,
            'info': ticker,
        }

    def fetch_ticker(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        response = self.publicGetGetTicker(self.extend({
            'symbol': market['id'],
        }, params))
        #
        #     {code:   "0",
        #        msg:   "suc",
        #       data: {symbol: "ETHBTC",
        #                 high:  0.058426,
        #                  vol:  19055.875,
        #                 last:  0.058019,
        #                  low:  0.055802,
        #               change:  0.03437271,
        #                  buy: "0.05780000",
        #                 sell: "0.05824200",
        #                 time:  1533413083184} }
        #
        return self.parse_ticker(response['data'], market)

    def parse_trade(self, trade, market=None):
        #
        # public fetchTrades
        #
        #   {     amount:  0.88,
        #     create_time:  1533414358000,
        #           price:  0.058019,
        #              id:  406531,
        #            type: "sell"          },
        #
        # private fetchMyTrades, fetchOrder, fetchOpenOrders, fetchClosedOrders
        #
        #   {    volume: "0.010",
        #           side: "SELL",
        #        feeCoin: "BTC",
        #          price: "0.05816200",
        #            fee: "0.00000029",
        #          ctime:  1533616674000,
        #     deal_price: "0.00058162",
        #             id:  415779,
        #           type: "卖出",
        #         bid_id:  3669539,  # only in fetchMyTrades
        #         ask_id:  3669583,  # only in fetchMyTrades
        #   }
        #
        timestamp = self.safe_integer_2(trade, 'create_time', 'ctime')
        if timestamp is None:
            timestring = self.safe_string(trade, 'created_at')
            if timestring is not None:
                timestamp = self.parse8601('2018-' + timestring + ':00Z')
        side = self.safe_string_2(trade, 'side', 'type')
        if side is not None:
            side = side.lower()
        id = self.safe_string(trade, 'id')
        symbol = None
        if market is not None:
            symbol = market['symbol']
        price = self.safe_float_2(trade, 'deal_price', 'price')
        amount = self.safe_float_2(trade, 'volume', 'amount')
        cost = None
        if amount is not None:
            if price is not None:
                cost = amount * price
        fee = None
        feeCost = self.safe_float_2(trade, 'fee', 'deal_fee')
        if feeCost is not None:
            feeCurrency = self.safe_string(trade, 'feeCoin')
            if feeCurrency is not None:
                currencyId = feeCurrency.lower()
                if currencyId in self.currencies_by_id:
                    feeCurrency = self.currencies_by_id[currencyId]['code']
            fee = {
                'cost': feeCost,
                'currency': feeCurrency,
            }
        orderIdField = 'ask_id' if (side == 'sell') else 'bid_id'
        orderId = self.safe_string(trade, orderIdField)
        return {
            'id': id,
            'info': trade,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': symbol,
            'order': orderId,
            'type': None,
            'side': side,
            'price': price,
            'amount': amount,
            'cost': cost,
            'fee': fee,
        }

    def fetch_trades(self, symbol, since=None, limit=None, params={}):
        self.load_markets()
        market = self.market(symbol)
        response = self.publicGetGetTrades(self.extend({
            'symbol': market['id'],
        }, params))
        #
        #     {code:   "0",
        #        msg:   "suc",
        #       data: [{     amount:  0.88,
        #                 create_time:  1533414358000,
        #                       price:  0.058019,
        #                          id:  406531,
        #                        type: "sell"          },
        #               {     amount:  4.88,
        #                 create_time:  1533414331000,
        #                       price:  0.058019,
        #                          id:  406530,
        #                        type: "buy"           },
        #               {     amount:  0.5,
        #                 create_time:  1533414311000,
        #                       price:  0.058019,
        #                          id:  406529,
        #                        type: "sell"          },
        #
        return self.parse_trades(response['data'], market, since, limit)

    def parse_ohlcv(self, ohlcv, market=None, timeframe='1d', since=None, limit=None):
        return [
            ohlcv[0] * 1000,  # timestamp
            ohlcv[1],  # open
            ohlcv[2],  # high
            ohlcv[3],  # low
            ohlcv[4],  # close
            ohlcv[5],  # volume
        ]

    def fetch_ohlcv(self, symbol, timeframe='1m', since=None, limit=None, params={}):
        self.load_markets()
        market = self.market(symbol)
        request = {
            'symbol': market['id'],
            'period': self.timeframes[timeframe],  # in minutes
        }
        response = self.publicGetGetRecords(self.extend(request, params))
        #
        #     {code: '0',
        #        msg: 'suc',
        #       data:
        #        [[1533402420, 0.057833, 0.057833, 0.057833, 0.057833, 18.1],
        #          [1533402480, 0.057833, 0.057833, 0.057833, 0.057833, 29.88],
        #          [1533402540, 0.057833, 0.057833, 0.057833, 0.057833, 29.06],
        #
        return self.parse_ohlcvs(response['data'], market, timeframe, since, limit)

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        if type == 'market':
            # for market buy it requires the amount of quote currency to spend
            if side == 'buy':
                if self.options['createMarketBuyOrderRequiresPrice']:
                    if price is None:
                        raise InvalidOrder(self.id + " createOrder() requires the price argument with market buy orders to calculate total order cost(amount to spend), where cost = amount * price. Supply a price argument to createOrder() call if you want the cost to be calculated for you from price and amount, or, alternatively, add .options['createMarketBuyOrderRequiresPrice'] = False to supply the cost in the amount argument(the exchange-specific behaviour)")
                    else:
                        amount = amount * price
        self.load_markets()
        market = self.market(symbol)
        orderType = '1' if (type == 'limit') else '2'
        orderSide = side.upper()
        amountToPrecision = self.amount_to_precision(symbol, amount)
        request = {
            'side': orderSide,
            'type': orderType,
            'symbol': market['id'],
            'volume': amountToPrecision,
            # An excerpt from their docs:
            # side required Trading Direction
            # type required pending order types，1:Limit-price Delegation 2:Market- price Delegation
            # volume required
            #     Purchase Quantity（polysemy，multiplex field）
            #     type=1: Quantity of buying and selling
            #     type=2: Buying represents gross price, and selling represents total number
            #     Trading restriction user/me-user information
            # price optional Delegation Price：type=2：self parameter is no use.
            # fee_is_user_exchange_coin optional
            #     0，when making transactions with all platform currencies,
            #     self parameter represents whether to use them to pay
            #     fees or not and 0 is no, 1 is yes.
        }
        priceToPrecision = None
        if type == 'limit':
            priceToPrecision = self.price_to_precision(symbol, price)
            request['price'] = priceToPrecision
            priceToPrecision = float(priceToPrecision)
        response = self.privatePostCreateOrder(self.extend(request, params))
        #
        #     {code: '0',
        #        msg: 'suc',
        #       data: {'order_id' : 34343} }
        #
        result = self.parse_order(response['data'], market)
        return self.extend(result, {
            'info': response,
            'symbol': symbol,
            'type': type,
            'side': side,
            'status': 'open',
            'price': priceToPrecision,
            'amount': float(amountToPrecision),
        })

    def cancel_order(self, id, symbol=None, params={}):
        self.load_markets()
        market = self.market(symbol)
        request = {
            'order_id': id,
            'symbol': market['id'],
        }
        response = self.privatePostCancelOrder(self.extend(request, params))
        return self.extend(self.parse_order(response), {
            'status': 'canceled',
        })

    def parse_order_status(self, status):
        statuses = {
            '0': 'open',  # INIT(0,"primary order，untraded and not enter the market"),
            '1': 'open',  # NEW_(1,"new order，untraded and enter the market "),
            '2': 'closed',  # FILLED(2,"complete deal"),
            '3': 'open',  # PART_FILLED(3,"partial deal"),
            '4': 'canceled',  # CANCELED(4,"already withdrawn"),
            '5': 'canceled',  # PENDING_CANCEL(5,"pending withdrawak"),
            '6': 'canceled',  # EXPIRED(6,"abnormal orders")
        }
        if status in statuses:
            return statuses[status]
        return status

    def parse_order(self, order, market=None):
        #
        # createOrder
        #
        #     {"order_id":34343}
        #
        # fetchOrder, fetchOpenOrders, fetchClosedOrders
        #
        #     {         side:   "BUY",
        #         total_price:   "0.10000000",
        #          created_at:    1510993841000,
        #           avg_price:   "0.10000000",
        #           countCoin:   "btc",
        #              source:    1,
        #                type:    1,
        #            side_msg:   "买入",
        #              volume:   "1.000",
        #               price:   "0.10000000",
        #          source_msg:   "WEB",
        #          status_msg:   "完全成交",
        #         deal_volume:   "1.00000000",
        #                  id:    424,
        #       remain_volume:   "0.00000000",
        #            baseCoin:   "eth",
        #           tradeList: [{    volume: "1.000",
        #                             feeCoin: "YLB",
        #                               price: "0.10000000",
        #                                 fee: "0.16431104",
        #                               ctime:  1510996571195,
        #                          deal_price: "0.10000000",
        #                                  id:  306,
        #                                type: "买入"            }],
        #              status:    2                                 }
        #
        # fetchOrder
        #
        #      {trade_list: [{    volume: "0.010",
        #                           feeCoin: "BTC",
        #                             price: "0.05816200",
        #                               fee: "0.00000029",
        #                             ctime:  1533616674000,
        #                        deal_price: "0.00058162",
        #                                id:  415779,
        #                              type: "卖出"            }],
        #        order_info: {         side:   "SELL",
        #                        total_price:   "0.010",
        #                         created_at:    1533616673000,
        #                          avg_price:   "0.05816200",
        #                          countCoin:   "btc",
        #                             source:    3,
        #                               type:    2,
        #                           side_msg:   "卖出",
        #                             volume:   "0.010",
        #                              price:   "0.00000000",
        #                         source_msg:   "API",
        #                         status_msg:   "完全成交",
        #                        deal_volume:   "0.01000000",
        #                                 id:    3669583,
        #                      remain_volume:   "0.00000000",
        #                           baseCoin:   "eth",
        #                          tradeList: [{    volume: "0.010",
        #                                            feeCoin: "BTC",
        #                                              price: "0.05816200",
        #                                                fee: "0.00000029",
        #                                              ctime:  1533616674000,
        #                                         deal_price: "0.00058162",
        #                                                 id:  415779,
        #                                               type: "卖出"            }],
        #                             status:    2                                 }}
        #
        side = self.safe_string(order, 'side')
        if side is not None:
            side = side.lower()
        status = self.parse_order_status(self.safe_string(order, 'status'))
        symbol = None
        if market is None:
            baseId = self.safe_string(order, 'baseCoin')
            quoteId = self.safe_string(order, 'countCoin')
            marketId = baseId + quoteId
            if marketId in self.markets_by_id:
                market = self.markets_by_id[marketId]
            else:
                base = baseId.upper()
                quote = quoteId.upper()
                base = self.common_currency_code(base)
                quote = self.common_currency_code(quote)
                symbol = base + '/' + quote
        if market is not None:
            symbol = market['symbol']
        timestamp = self.safe_integer(order, 'created_at')
        if timestamp is None:
            timestring = self.safe_string(order, 'created_at')
            if timestring is not None:
                timestamp = self.parse8601('2018-' + timestring + ':00Z')
        lastTradeTimestamp = None
        fee = None
        average = self.safe_float(order, 'avg_price')
        price = self.safe_float(order, 'price')
        if price == 0:
            price = average
        amount = self.safe_float(order, 'volume')
        filled = self.safe_float(order, 'deal_volume')
        remaining = self.safe_float(order, 'remain_volume')
        cost = self.safe_float(order, 'total_price')
        id = self.safe_string_2(order, 'id', 'order_id')
        trades = None
        tradeList = self.safe_value(order, 'tradeList', [])
        feeCurrencies = {}
        feeCost = None
        for i in range(0, len(tradeList)):
            trade = self.parse_trade(tradeList[i], market)
            if feeCost is None:
                feeCost = 0
            feeCost = feeCost + trade['fee']['cost']
            tradeFeeCurrency = trade['fee']['currency']
            feeCurrencies[tradeFeeCurrency] = trade['fee']['cost']
            if trades is None:
                trades = []
            lastTradeTimestamp = trade['timestamp']
            trades.append(self.extend(trade, {
                'order': id,
            }))
        if feeCost is not None:
            feeCurrency = None
            keys = list(feeCurrencies.keys())
            numCurrencies = len(keys)
            if numCurrencies == 1:
                feeCurrency = keys[0]
            fee = {
                'cost': feeCost,
                'currency': feeCurrency,
            }
        result = {
            'info': order,
            'id': id,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'lastTradeTimestamp': lastTradeTimestamp,
            'symbol': symbol,
            'type': 'limit',
            'side': side,
            'price': price,
            'cost': cost,
            'average': average,
            'amount': amount,
            'filled': filled,
            'remaining': remaining,
            'status': status,
            'fee': fee,
            'trades': trades,
        }
        return result

    def fetch_orders_with_method(self, method, symbol=None, since=None, limit=None, params={}):
        if symbol is None:
            raise ExchangeError(self.id + ' fetchOrdersWithMethod() requires a symbol argument')
        self.load_markets()
        market = self.market(symbol)
        request = {
            # pageSize optional page size
            # page optional page number
            'symbol': market['id'],
        }
        if limit is not None:
            request['pageSize'] = limit
        response = getattr(self, method)(self.extend(request, params))
        #
        #     {code:   "0",
        #        msg:   "suc",
        #       data: {    count:    1,
        #               orderList: [{         side:   "SELL",
        #                                total_price:   "0.010",
        #                                 created_at:    1533616673000,
        #                                  avg_price:   "0.05816200",
        #                                  countCoin:   "btc",
        #                                     source:    3,
        #                                       type:    2,
        #                                   side_msg:   "卖出",
        #                                     volume:   "0.010",
        #                                      price:   "0.00000000",
        #                                 source_msg:   "API",
        #                                 status_msg:   "完全成交",
        #                                deal_volume:   "0.01000000",
        #                                         id:    3669583,
        #                              remain_volume:   "0.00000000",
        #                                   baseCoin:   "eth",
        #                                  tradeList: [{    volume: "0.010",
        #                                                    feeCoin: "BTC",
        #                                                      price: "0.05816200",
        #                                                        fee: "0.00000029",
        #                                                      ctime:  1533616674000,
        #                                                 deal_price: "0.00058162",
        #                                                         id:  415779,
        #                                                       type: "卖出"            }],
        #                                     status:    2                                 }]} }
        #
        # privateGetNewOrder returns resultList, privateGetAllOrder returns orderList
        orders = self.safe_value_2(response['data'], 'orderList', 'resultList', [])
        return self.parse_orders(orders, market, since, limit)

    def fetch_open_orders(self, symbol=None, since=None, limit=None, params={}):
        return self.fetch_orders_with_method('privateGetNewOrder', symbol, since, limit, params)

    def fetch_closed_orders(self, symbol=None, since=None, limit=None, params={}):
        return self.fetch_orders_with_method('privateGetAllOrder', symbol, since, limit, params)

    def fetch_order(self, id, symbol=None, params={}):
        self.load_markets()
        market = self.market(symbol)
        request = {
            'order_id': id,
            'symbol': market['id'],
        }
        response = self.privateGetOrderInfo(self.extend(request, params))
        #
        #     {code:   "0",
        #        msg:   "suc",
        #       data: {trade_list: [{    volume: "0.010",
        #                                  feeCoin: "BTC",
        #                                    price: "0.05816200",
        #                                      fee: "0.00000029",
        #                                    ctime:  1533616674000,
        #                               deal_price: "0.00058162",
        #                                       id:  415779,
        #                                     type: "卖出"            }],
        #               order_info: {         side:   "SELL",
        #                               total_price:   "0.010",
        #                                created_at:    1533616673000,
        #                                 avg_price:   "0.05816200",
        #                                 countCoin:   "btc",
        #                                    source:    3,
        #                                      type:    2,
        #                                  side_msg:   "卖出",
        #                                    volume:   "0.010",
        #                                     price:   "0.00000000",
        #                                source_msg:   "API",
        #                                status_msg:   "完全成交",
        #                               deal_volume:   "0.01000000",
        #                                        id:    3669583,
        #                             remain_volume:   "0.00000000",
        #                                  baseCoin:   "eth",
        #                                 tradeList: [{    volume: "0.010",
        #                                                   feeCoin: "BTC",
        #                                                     price: "0.05816200",
        #                                                       fee: "0.00000029",
        #                                                     ctime:  1533616674000,
        #                                                deal_price: "0.00058162",
        #                                                        id:  415779,
        #                                                      type: "卖出"            }],
        #                                    status:    2                                 }} }
        #
        return self.parse_order(response['data']['order_info'], market)

    def fetch_my_trades(self, symbol=None, since=None, limit=None, params={}):
        if symbol is None:
            raise ExchangeError(self.id + ' fetchMyTrades requires a symbol argument')
        self.load_markets()
        market = self.market(symbol)
        request = {
            # pageSize optional page size
            # page optional page number
            'symbol': market['id'],
        }
        if limit is not None:
            request['pageSize'] = limit
        response = self.privateGetAllTrade(self.extend(request, params))
        #
        #     {code:   "0",
        #        msg:   "suc",
        #       data: {     count:    1,
        #               resultList: [{    volume: "0.010",
        #                                     side: "SELL",
        #                                  feeCoin: "BTC",
        #                                    price: "0.05816200",
        #                                      fee: "0.00000029",
        #                                    ctime:  1533616674000,
        #                               deal_price: "0.00058162",
        #                                       id:  415779,
        #                                     type: "卖出",
        #                                   bid_id:  3669539,
        #                                   ask_id:  3669583        }]} }
        #
        trades = self.safe_value(response['data'], 'resultList', [])
        return self.parse_trades(trades, market, since, limit)

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'] + '/' + self.implode_params(path, params)
        if api == 'public':
            if params:
                url += '?' + self.urlencode(params)
        else:
            self.check_required_credentials()
            timestamp = str(self.seconds())
            auth = ''
            query = self.keysort(self.extend(params, {
                'api_key': self.apiKey,
                'time': timestamp,
            }))
            keys = list(query.keys())
            for i in range(0, len(keys)):
                key = keys[i]
                auth += key
                auth += str(query[key])
            signature = self.hash(self.encode(auth + self.secret))
            if query:
                if method == 'GET':
                    url += '?' + self.urlencode(query) + '&sign=' + signature
                else:
                    body = self.urlencode(query) + '&sign=' + signature
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
            }
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def handle_errors(self, httpCode, reason, url, method, headers, body):
        if not isinstance(body, basestring):
            return  # fallback to default error handler
        if len(body) < 2:
            return  # fallback to default error handler
        if (body[0] == '{') or (body[0] == '['):
            response = json.loads(body)
            #
            # {"code":"0","msg":"suc","data":[{"
            #
            code = self.safe_string(response, 'code')
            # message = self.safe_string(response, 'msg')
            feedback = self.id + ' ' + self.json(response)
            exceptions = self.exceptions
            if code != '0':
                if code in exceptions:
                    raise exceptions[code](feedback)
                else:
                    raise ExchangeError(feedback)
