import backtrader as bt

class KeltnerChannelRSIBreakoutStrategy(bt.Strategy):
    params = (
        ('ema_period', 30),
        ('atr_period', 7),
        ('atr_multiplier', 1.0),
        ('rsi_period', 14),
        ('rsi_low', 30),
        ('rsi_high', 70),
        ('trailing_stop_atr', 1.0)
    )

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()} - {txt}')

    def __init__(self):
        self.ema = bt.indicators.ExponentialMovingAverage(self.data, period=self.params.ema_period)
        self.atr = bt.indicators.AverageTrueRange(self.data, period=self.params.atr_period)
        self.rsi = bt.indicators.RelativeStrengthIndex(self.data, period=self.params.rsi_period)
        self.order = None
        self.trailing_stop_price = None
        self.upper_band = self.ema + (self.atr * self.params.atr_multiplier)
        self.lower_band = self.ema - (self.atr * self.params.atr_multiplier)
        self.dataclose = self.datas[0].close

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED, Price: {order.executed.price:.2f}, Cost: {order.executed.value:.2f}, Comm: {order.executed.comm:.2f}')
            elif order.issell():
                self.log(f'SELL EXECUTED, Price: {order.executed.price:.2f}, Cost: {order.executed.value:.2f}, Comm: {order.executed.comm:.2f}')
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
        self.order = None
    
    def notify_trade(self, trade):
        if trade.isclosed:
            self.log(f'TRADE PROFIT, GROSS: {trade.pnl:.2f}, NET: {trade.pnlcomm:.2f}')

    def next(self):
        if self.order:
            return

        if not self.position:
            if self.data.close[0] > self.upper_band[0] and self.rsi[0] > self.params.rsi_low:
                cash = self.broker.getcash()
                size = int(cash * 0.95 / self.data.close[0])
                self.order = self.buy(size=size, exectype=bt.Order.Market)
                self.log(f'BUY CREATE, Price: {self.dataclose[0]:.2f}, Size: {size}')
        else:
            if self.position.size > 0:
                new_stop = self.data.close[0] - (self.atr[0] * self.params.trailing_stop_atr)
                if self.trailing_stop_price is None or new_stop > self.trailing_stop_price:
                    self.trailing_stop_price = new_stop

                if self.data.close[0] < self.trailing_stop_price:
                    self.order = self.close()
                    self.log(f'SELL CREATE, Price: {self.dataclose[0]:.2f}, Trailing Stop Price: {self.trailing_stop_price:.2f}')
                    self.trailing_stop_price = None

