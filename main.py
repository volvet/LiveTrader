
import backtrader as bt
import yfinance as yf
import os
import pandas as pd
import datetime


PROXY = 'http://127.0.0.1:7897'

# basic simple moving average crossover strategy from tutorial
class SmaCross(bt.Strategy):
    # list of parameters which are configurable for the strategy
    params = (
        ('exitbars', 5),  # number of bars to hold position
    )

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()} - {txt}')

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.log('Initializing strategy...')
        self.order = None

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            self.log(f'Order {order.getstatusname()}')
            return
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED, Price: {order.executed.price:.2f}, Cost: {order.executed.value:.2f}, Comm: {order.executed.comm:.2f}')
            elif order.issell():
                self.log(f'SELL EXECUTED, Price: {order.executed.price:.2f}, Cost: {order.executed.value:.2f}, Comm: {order.executed.comm:.2f}')
            self.bar_executed = len(self)
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log(f'Order {order.getstatusname()}')
            self.order = None

    def next(self):
        if len(self) == 1:
            if not self.position:
                self.log(f'BUY CREATE {self.dataclose[0]:.2f}')
                self.order = self.buy()
        elif len(self) >= (self.bar_executed + self.params.exitbars):
            if self.position:
                self.log(f'SELL CREATE {self.dataclose[0]:.2f}')
                self.order = self.sell()
            


def setup_proxy(proxy_url):
    os.environ['HTTP_PROXY'] = proxy_url
    os.environ['HTTPS_PROXY'] = proxy_url

def main():
    setup_proxy(PROXY)
    ticker = 'AAPL'
    start_data = '2025-01-01'
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
    cerebro.addstrategy(SmaCross)
    cerebro.run()
    cerebro.plot()


if __name__ == "__main__":
    main()
