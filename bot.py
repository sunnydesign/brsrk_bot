#! /usr/bin/env python
# -*- coding: utf-8 -*-

import settings
import requests
import telebot
import time
from datetime import datetime

#import uuid
#from decimal import *

class Client(object):
    def __init__(self, url, public_key, secret):
        self.url = url + "/api/2"
        self.session = requests.session()
        self.session.auth = (public_key, secret)

    def get_symbol(self, symbol_code):
        """Get symbol."""
        return self.session.get("%s/public/symbol/%s" % (self.url, symbol_code)).json()

    def get_trades(self, symbol_code):
        """Get trades."""
        return self.session.get("%s/public/trades/%s" % (self.url, symbol_code)).json()

    def get_orderbook(self, symbol_code):
        """Get orderbook. """
        return self.session.get("%s/public/orderbook/%s" % (self.url, symbol_code)).json()

    def get_address(self, currency_code):
        """Get address for deposit."""
        return self.session.get("%s/account/crypto/address/%s" % (self.url, currency_code)).json()

    def get_account_balance(self):
        """Get main balance."""
        return self.session.get("%s/account/balance" % self.url).json()

    def get_trading_balance(self):
        """Get trading balance."""
        return self.session.get("%s/trading/balance" % self.url).json()

    def transfer(self, currency_code, amount, to_exchange):
        return self.session.post("%s/account/transfer" % self.url, data={
                'currency': currency_code, 'amount': amount,
                'type': 'bankToExchange' if to_exchange else 'exchangeToBank'
            }).json()

    def new_order(self, client_order_id, symbol_code, side, quantity, price=None):
        """Place an order."""
        data = {'symbol': symbol_code, 'side': side, 'quantity': quantity}

        if price is not None:
            data['price'] = price

        return self.session.put("%s/order/%s" % (self.url, client_order_id), data=data).json()

    def get_order(self, client_order_id, wait=None):
        """Get order info."""
        data = {'wait': wait} if wait is not None else {}

        return self.session.get("%s/order/%s" % (self.url, client_order_id), params=data).json()

    def cancel_order(self, client_order_id):
        """Cancel order."""
        return self.session.delete("%s/order/%s" % (self.url, client_order_id)).json()

    def withdraw(self, currency_code, amount, address, network_fee=None):
        """Withdraw."""
        data = {'currency': currency_code, 'amount': amount, 'address': address}

        if network_fee is not None:
            data['networkfee'] = network_fee

        return self.session.post("%s/account/crypto/withdraw" % self.url, data=data).json()

    def get_transaction(self, transaction_id):
        """Get transaction info."""
        return self.session.get("%s/account/transactions/%s" % (self.url, transaction_id)).json()

if __name__ == "__main__":
    client = Client("https://api.hitbtc.com", settings.hitbtc_public, settings.hitbtc_secret)
    bot = telebot.TeleBot(settings.telegram_token)

    """ UTILS """
    def deg_to_compass(num):
        val = int((num / 22.5) + .5)
        #arr = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
        arr = ["С", "ССВ", "СВ", "ВСВ", "В", "ВЮВ", "ЮВ", "ЮЮВ", "Ю", "ЮЮЗ", "ЮЗ", "ЗЮЗ", "З", "ЗСЗ", "СЗ", "ССЗ"]
        return arr[(val % 16)]

    def get_weather():
        url = "http://api.openweathermap.org/data/2.5/weather"
        city_id = settings.city_id
        token = settings.openweathermap_token
        response = requests.session().get('%s?id=%s&units=metric&appid=%s' % (url, city_id, token)).json()

        if(response['cod'] == 200):
            t = str(response['main']['temp'])
            wind_deg = response['wind']['deg']
            wind_speed = str(response['wind']['speed'])
            text = '\U0001f326 В Перми %s °C\n\U0001f32c %s %sм/с\n' % (t, deg_to_compass(wind_deg), wind_speed)

            return text
        else:
            return False

    """ START """
    @bot.message_handler(commands=['start', 'Start'])
    def send_welcome(message):
        bot.send_message(message.chat.id, 'Привет')


    """ HELP """
    @bot.message_handler(commands=['help', 'Help'])
    def send_help(message):
        bot.send_message(message.chat.id, 'Допустимые команды:\n'
                                          '/start\n'
                                          '/help\n'
                                          '/datetime\n'
                                          '/weather\n'
                                          '/btc')

    """ TIME """
    @bot.message_handler(commands=['datetime', 'Datetime'])
    def send_time(message):
        text = datetime.strftime(datetime.now(), "%d.%m.%Y %H:%M")

        output = bot.send_message(message.chat.id, text)
        print(output, text)

    """ WEATHER """
    @bot.message_handler(commands=['weather', 'Weather'])
    def send_weather(message):
        text = get_weather()

        if text:
            bot.send_message(message.chat.id, text)

    """ BTC """
    @bot.message_handler(commands=['btc', 'Btc'])
    def send_btc_rate(message):
        btc_usd = client.get_trades('BTCUSD')
        text = '💰 BTC/USD: ' + btc_usd[0]['price']
        bot.send_message(message.chat.id, text)

    """ INFORMER KILO """
    @bot.message_handler(commands=['inform', 'Inform'])
    def send_weather_to_chat(message):
        text = get_weather()

        if text:
            bot.send_message(settings.kilo_chat_id, text)

    """ SORRY """
    @bot.message_handler(func=lambda message: True)
    def echo_all(message):
        bot.reply_to(message, 'Извини, я тебя не понимаю. Попробуй ввести\n/start или /help')

    bot.polling()

    # while True:
    #     t = datetime.strftime(datetime.now(), "%H:%M")
    #
    #     if t == '9:00':
    #         print(t)
    #         send_weather_to_chat()
    #
    #         time.sleep(60)

    #for item in btc_usd:
    #    print(item['price'])

    # https://api.hitbtc.com/api/2/public/trades/BTCUSD

    #print('ETH deposit address: "%s"' % address)

    # # transfer all deposited eths from account to trading balance
    # balances = client.get_account_balance()
    # for balance in balances:
    #     if balance['currency'] == 'ETH' and float(balance['available']) > float(eth_btc['quantityIncrement']):
    #         client.transfer('ETH', balance['available'], True)
    #         print('ETH Account balance: %s'% balance['available'])
    #         time.sleep(1)   # wait till transfer completed
    #
    # # get eth trading balance
    # eth_balance = 0.0
    # balances = client.get_trading_balance()
    # for balance in balances:
    #     if balance['currency'] == 'ETH':
    #         eth_balance = float(balance['available'])
    #
    # print('Current ETH balance: %s' % eth_balance)
    #
    # # sell eth at the best price
    # if eth_balance >= float(eth_btc['quantityIncrement']):
    #     client_order_id = uuid.uuid4().hex
    #     orderbook = client.get_orderbook('ETHBTC')
    #     # set price a little high
    #     best_price = Decimal(orderbook['bid'][0]['price']) + Decimal(eth_btc['tickSize'])
    #
    #     print("Selling at %s" % best_price)
    #
    #     order = client.new_order(client_order_id, 'ETHBTC', 'sell', eth_balance, best_price)
    #     if 'error' not in order:
    #         if order['status'] == 'filled':
    #             print("Order filled", order)
    #         elif order['status'] == 'new' or order['status'] == 'partiallyFilled':
    #             print("Waiting order...")
    #             for k in range(0, 3):
    #                 order = client.get_order(client_order_id, 20000)
    #                 print(order)
    #
    #                 if 'error' in order or ('status' in order and order['status'] == 'filled'):
    #                     break
    #
    #             # cancel order if it isn't filled
    #             if 'status' in order and order['status'] != 'filled':
    #                 cancel = client.cancel_order(client_order_id)
    #                 print('Cancel order result', cancel)
    #     else:
    #         print(order['error'])
    #
    # # transfer all available BTC after trading to account balance
    # balances = client.get_trading_balance()
    # for balance in balances:
    #     if balance['currency'] == 'BTC':
    #         transfer = client.transfer('BTC', balance['available'], False)
    #         print('Transfer', transfer)
    #         time.sleep(1)
    #
    # # get account balance and withdraw BTC
    # balances = client.get_account_balance()
    # for balance in balances:
    #     if balance['currency'] == 'BTC' and float(balance['available']) > 0.101:
    #         payout = client.withdraw('BTC', '0.1', btc_address, '0.0005')
    #
    #         if 'error' not in payout:
    #             transaction_id = payout['id']
    #             print("Transaction ID: %s" % transaction_id)
    #             for k in range(0, 5):
    #                 time.sleep(20)
    #                 transaction = client.get_transaction(transaction_id)
    #                 print("Payout info", transaction)
    #         else:
    #             print(payout['error'])