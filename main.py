
import backtrader as bt
import yfinance as yf
import os
import random
import pandas as pd
import datetime
import shutil

from strategies.ChainStrategy import ChainStrategy
from strategies.MultilineIndicatorStrategy import MultilineIndicatorStrategy
from strategies.AdxStrategy import AdxStrategy
from strategies.BollingerBandsStrategy import BBandsMeansReversionStrategy
from strategies.RegimeFilteredTrendStrategy import RegimeFilteredTrendStrategy
from strategies.RelativeMomentumAccelStrategy import RelativeMomentumAccelStrategy
from strategies.KeltnerBreakoutstrategy import KeltnerBreakoutStrategy
from strategies.KeltnerChannelRSIBreakoutStrategy import KeltnerChannelRSIBreakoutStrategy
from strategies.DQNStrategy import DQNStrategy
from strategies.PolicyNetworkStrategy import PolicyNetworkStrategy
from utils.net import setup_proxy, PROXY
from backtest.backtest import backtest
from nn.train import train, train_policy_agent



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
    #ret_sum = 0.0
    #testset =  ['QQQ'] #random.sample(TICKERS, 1)
    #for ticker in testset:
    #    ret = backtest(ticker, DQNStrategy, start_date='2026-01-01', end_date='2026-08-10', initial_cash=10000.0, commission=0.001)
    #    if not ret:
    #        print(f"Backtest failed for {ticker}. Skipping to next ticker.")
    #        continue
    #    ret_sum += ret
    #avg_ret = ret_sum / len(testset)
    #print(f"Average return across tickers: {avg_ret:.2f}%")
    best_reward_ratio = -10000.0
    for i in range(20):
        ticker = random.sample(TICKERS, 1)[0]
        print(f"Train with dataset {ticker}")
        train_policy_agent(ticker, start_date='2020-01-01', end_date='2025-12-31', episode=100, resume=True)
        print(f"Evaluation for dataset {ticker}")
        ratio = train_policy_agent('QQQ', start_date='2026-01-01', end_date='2026-09-30', episode=20, resume=True, eval=True)
        if ratio > best_reward_ratio:
            best_reward_ratio = ratio
            print(f"New best reward ratio: {best_reward_ratio:.2f}")
            # Save the best model
            shutil.copy("models/model_policy_v0.pth", "models/best_policy_agent.pth")

if __name__ == "__main__":
    main()

