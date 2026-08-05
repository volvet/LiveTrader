
import backtrader as bt
import yfinance as yf
import os
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



TICKERS = ['AAPL', 'BRK-B', 'KO', 'MSFT', 'NVDA', 'TSLA', 'QQQ', 'QQQM', 'VOO']


def main():
    setup_proxy(PROXY)
    backtest(TICKERS[6], RelativeMomentumAccelStrategy, start_date='2018-01-01', end_date='2025-12-31', initial_cash=10000.0, commission=0.001)


if __name__ == "__main__":
    main()
    
