#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import argparse
import datetime as dt
import pandas as pd
from lib.simulator import PortfolioSimulator

parser = argparse.ArgumentParser()
parser.add_argument('stock_path', metavar='STOCK', help='path to the stock rates dataset')
parser.add_argument('actions_path', metavar='ACTIONS', help='path to the timestep to action mapping generated by the strategy')
parser.add_argument('--investment', metavar='AMOUNT', type=float, default='1000', help='initial investment (default: 1000)')
parser.add_argument('--reinvest-rate', metavar='RATE', type=float, default='0.5', help='reinvest rate (default: 0.5)')

args = parser.parse_args()

# Parse UTC timestamp and use time col as index
def set_time_index(df):
    df['time'] = pd.to_datetime(df['time'], unit='s', origin='unix')
    df = df.set_index('time')
    return df

print('Loading stock rates from {} ...'.format(args.stock_path))
stock_df = pd.read_csv(args.stock_path)
stock_df = set_time_index(stock_df)
print(stock_df.head())

print('\nLoading actions from {} ...'.format(args.actions_path))
actions_df = pd.read_csv(args.actions_path)
actions_df = set_time_index(actions_df)
print(actions_df.head())

print('\nMerging dataframes ...')
simulation_df = pd.concat([stock_df, actions_df], axis=1)
print(simulation_df.head())

print('Simulating ...')
portfolio = PortfolioSimulator(args.investment, args.reinvest_rate)
portfolio.set_balance('BTC', 0)
portfolio.set_balance('USD', args.investment)

for row in simulation_df.itertuples():
    print('{} closing at {} -> {}'.format(row[0], row.close, row.action))

    if row.action == 'BUY':
        btc_qty = portfolio.balance('USD') / row.close
        portfolio.buy('BTC-USD', btc_qty, row.close)

    elif row.action == 'SELL':
        btc_qty = portfolio.balance('BTC')
        portfolio.sell('BTC-USD', btc_qty, row.close)

print('Simulation done')
print('Initial BTC balance: {}'.format(0))
print('Initial USD balance: {}'.format(args.investment))
print('Final BTC balance: {}'.format(portfolio.balance('BTC')))
print('Final USD balance: {}'.format(portfolio.balance('USD')))
print('Profit: {}'.format(portfolio.balance('profit')))
