
import backtrader as bt
import yfinance as yf
import os
import random
import pandas as pd
import datetime

from strategies.ChainStrategy import ChainStrategy
from strategies.MultilineIndicatorStrategy import MultilineIndicatorStrategy
from strategies.AdxStrategy import AdxStrategy
from strategies.BollingerBandsStrategy import BBandsMeansReversionStrategy
from strategies.RegimeFilteredTrendStrategy import RegimeFilteredTrendStrategy
from strategies.RelativeMomentumAccelStrategy import RelativeMomentumAccelStrategy
from utils.net import setup_proxy, PROXY
from backtest.backtest import backtest



TICKERS = ['AAPL', 
           'BRK-B', 
           'KO', 
           'MSFT', 
           'NVDA', 
           'TSLA', 
           'QQQ', 
           'QQQM', 
           'VOO', 
           'SPY',
           'BABA', 
           'AMD', 
           'WMT', 
           'META',
           'COST',
           'HOOD',
           'TSM',
           'INTC',
           'PDD',
           'SMCI',
           'MU',
           'QCOM',
           'MCD',
           'NKE',
           'GE',
           'BND',
           'ALLW',
           'DGRO',
           'SGOV',
           'DIA',
           'QQQI',
           'IVW',
           'XLA',
           'CSCO',
           'GOOG',
           'LTBR',
           'CCJ',
           'NGR',
           'VST',
           'SMH',
           'MAGS',
           'D',
           'AVGO',
           'SMCI',
           'ORCL',
           'BIDU',
           'AMZN',
           ]


def main():
    setup_proxy(PROXY)
    ret_sum = 0.0
    testset = random.sample(TICKERS, 1)
    for ticker in testset:
        ret = backtest(ticker, RelativeMomentumAccelStrategy, start_date='2018-01-01', end_date='2025-12-31', initial_cash=10000.0, commission=0.001)
        ret_sum += ret
    avg_ret = ret_sum / len(testset)
    print(f"Average return across tickers: {avg_ret:.2f}%")


if __name__ == "__main__":
    main()

