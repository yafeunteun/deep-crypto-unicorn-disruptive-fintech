#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# References
# https://docs.gdax.com/?python

# Include required libs
import os, json, requests, time, datetime
import talib, pandas, numpy as np
from coinbase import CoinbaseExchangeAuth
from simulator import PortfolioSimulator

def print_json(jayson):
    print(json.dumps(jayson, indent=4))

# Read secrets from env
#API_KEY = os.environ['GDAX_API_KEY']
#API_SECRET = os.environ['GDAX_API_SECRET']
#API_PASS = os.environ['GDAX_API_PASS']

# VIEW ONLY PUBLIC KEY
API_KEY = "ca554f4040cd56adb1b625d63eaab096"
API_SECRET = "kILvSj7TAsLfOHlhAo/0eoYJg7AGQ2U8RHmu4splW+Eb+Lgo20yhHPB2i4729N2zBIJiMJcXq3tXCTEICHbCyw=="
API_PASS = "v2qdfkysrdf"

# Params
DEBUG = True
product = 'BTC-USD'
investment = 1000.0
reinvest_rate = 0.5

api_url = 'https://api.gdax.com/' # <----- REAL MONEY $$$
# api_url = 'https://api-public.sandbox.gdax.com/'

# Get an auth token from coinbase
auth = CoinbaseExchangeAuth(API_KEY, API_SECRET, API_PASS)

# Setup simulator
simulator = PortfolioSimulator(investment, reinvest_rate)
simulator.set_balance('BTC', 0)
simulator.set_balance('USD', investment)

while True:
    ## Get historic rates
    dtime_now = datetime.datetime.utcnow()
    dtime_past = dtime_now - datetime.timedelta(minutes=15)
    params = {
        'start': dtime_past.isoformat(),
        'end': dtime_now.isoformat(),
        'granularity': 60,
    }
    r = requests.get(api_url + 'products/{}/candles'.format(product), params=params, auth=auth)
    rates_sorted = sorted(r.json(), key=lambda x: x[0])
    close_prices = np.array([x[4] for x in rates_sorted])

    if DEBUG:
        print(close_prices)
    
    ## Apply strategy 
    upper, middle, lower = talib.BBANDS(
        close_prices,
        timeperiod=10,
        # number of non-biased standard deviations from the mean
        nbdevup=2,
        nbdevdn=2,
        # Moving average type: simple moving average here
        matype=0)
        
    if DEBUG:
        print "Last close price: {}".format(close_prices[-1])
        print "Upper / Middle / Lower bands: {} / {} / {}".format(upper[-1], middle[-1], lower[-1])
        print "BTC balance: {} BTC".format(simulator.balance('BTC'))
        print "BTC balance: {} USD (at last close price)".format(simulator.balance('BTC') * close_prices[-1])
        print "USD balance: {} USD".format(simulator.balance('USD'))
        # print "Portfolio value: {}".format(capital_under_management + stock_btc * close_prices[-1])
    	print "Profit: {}".format(simulator.balance('profit'))


    # If the last close price is under the lower band
    # and we have USD to buy BTC
    if close_prices[-1] <= lower[-1] and simulator.balance('USD') > 0:
        if DEBUG:
            print ">>> BUY SIGNAL"

        ## Buy all the BTC we can
        btc_qty = simulator.balance('USD') / close_prices[-1]
        simulator.buy(product, btc_qty, close_prices[-1])

    # If close_prices is above the recent upper band and we have
    # no short positions then invest the entire
    # portfolio value to short BTC
    elif close_prices[-1] >= upper[-1] and simulator.balance('BTC') > 0:
        if DEBUG:
            print ">>> SELL SIGNAL"

        ## Sell all the BTC we have
        btc_qty = simulator.balance('BTC')
        simulator.sell(product, btc_qty, close_prices[-1])

    else:
        # Do Nothing
        if DEBUG:
            print "... do nothing"
        pass
            
    time.sleep(30)
    ## END LOOP ##    
