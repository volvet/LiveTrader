
import backtrader as bt
import yfinance as yf
import os
import pandas as pd
import datetime

from strategies.ChainStrategy import ChainStrategy
from strategies.MultilineIndicatorStrategy import MultilineIndicatorStrategy
from strategies.AdxStrategy import AdxStrategy
from strategies.BollingerBandsStrategy import BBandsMeansReversionStrategy

PROXY = 'http://127.0.0.1:7897'

def setup_proxy(proxy_url):
    os.environ['HTTP_PROXY'] = proxy_url
    os.environ['HTTPS_PROXY'] = proxy_url

def main():
    setup_proxy(PROXY)
    ticker = 'AAPL'
    start_data = '2023-01-01'
    end_data = '2025-12-31'
    print(f"Downloading data for {ticker} from {start_data} to {end_data}...")
    try:
        data_df = yf.download(ticker, start=start_data, end=end_data)
        data_df.columns = data_df.columns.droplevel(1)
        print(f"Data downloaded successfully. Data shape: {data_df.shape}")
        print("Data Frame head:\n", data_df.head())
        print("Data Frame info:\n")
        data_df.info()
    except Exception as e:
        print(f"Error downloading data: {e}")
        return
    
    if not isinstance(data_df.index, pd.DataFrame):
        print("Converting index to datetime...")
        data_df.index = pd.to_datetime(data_df.index)

    data = bt.feeds.PandasData(dataname=data_df)
    print(f"Data feed created: {data}")
    cerebro = bt.Cerebro()
    cerebro.adddata(data)

    initial_cash = 10000.0
    cerebro.broker.setcash(initial_cash)
    commission = 0.001  # 0.1% commission
    cerebro.broker.setcommission(commission=commission)
    cerebro.addstrategy(BBandsMeansReversionStrategy)
    cerebro.run()
    cerebro.plot(style='candlestick', barup='green', bardown='red', volume=True, iplot=False, show=False)
    print(f"Final Portfolio Value: {cerebro.broker.getvalue():.2f}")


if __name__ == "__main__":
    main()
