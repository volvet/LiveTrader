import backtrader as bt

class ChainStrategy(bt.Strategy):
    params = (
        ('sma_period', 20),
        ('rsi_period', 14),
        ('rsi_sma_period', 10),
        ('log_interval', 10),
    )

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()} - {txt}')

    def __init__(self):
        self.log('Initializing ChainStrategy...')
        self.dataclose = self.datas[0].close
        self.sma = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.sma_period)
        self.rsi = bt.indicators.RSI(self.datas[0], period=self.params.rsi_period)
        self.rsi_sma = bt.indicators.SimpleMovingAverage(self.rsi, period=self.params.rsi_sma_period)
        self.log('ChainStrategy initialized.')

    def next(self):
        if len(self) % self.params.log_interval == 0:
            self.log(f'Bar: {len(self)}, Close: {self.dataclose[0]:.2f}, SMA: {self.sma[0]:.2f}, RSI: {self.rsi[0]:.2f}, RSI SMA: {self.rsi_sma[0]:.2f}')