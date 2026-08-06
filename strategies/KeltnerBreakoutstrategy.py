import backtrader as bt

class KeltnerChannel(bt.Indicator):
    lines = ('mid', 'top', 'bot')
    params = (
        ('ema_peroid', 30),
        ('atr_period', 14),
        ('atr_multiplier', 1),
    )

    def __init__(self):
        self.lines.mid = bt.indicators.ExponentialMovingAverage(self.data, period=self.params.ema_peroid)
        atr = bt.indicators.AverageTrueRange(self.data, period=self.params.atr_period)
        self.lines.top = self.lines.mid + (atr * self.params.atr_multiplier)
        self.lines.bot = self.lines.mid - (atr * self.params.atr_multiplier)

class KeltnerBreakoutStrategy(bt.Strategy):
    params = (
        ('ema_period', 30),
        ('atr_period', 14),
        ('atr_multiplier', 1),
    )

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()} - {txt}')

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.dataopen = self.datas[0].open
        self.keltner = KeltnerChannel(self.data,
                                      ema_peroid=self.params.ema_period, 
                                      atr_period=self.params.atr_period, 
                                      atr_multiplier=self.params.atr_multiplier)
        self.order = None
        self.buyprice = None
        self.buycomm = None
        self.keltner.plotinfo.subplot = False
        self.keltner.plotlines.mid._plotskip = False
        self.keltner.plotlines.top._plotskip = False
        self.keltner.plotlines.bot._plotskip = False

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED, Price: {order.executed.price:.2f}, Cost: {order.executed.value:.2f}, Comm: {order.executed.comm:.2f}')
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            elif order.issell():
                self.log(f'SELL EXECUTED, Price: {order.executed.price:.2f}, Cost: {order.executed.value:.2f}, Comm: {order.executed.comm:.2f}')
            self.bar_executed = len(self)
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
        self.order = None

    def notify_trade(self, trade):
        if trade.isclosed:
            self.log(f'TRADE PROFIT, GROSS: {trade.pnl:.2f}, NET: {trade.pnlcomm:.2f}')

    def next(self):
        if self.order:
            return

        prev_close = self.dataclose[-1]
        prev_top = self.keltner.lines.top[-1]
        prev_bot = self.keltner.lines.bot[-1]
        current_ema = self.keltner.lines.mid[0]
        current_close = self.dataclose[0]

        if not self.position:
            if prev_close > prev_top:
                cash = self.broker.getcash()
                size = int(cash * 0.95 / self.data.close[0])
                self.order = self.buy(size=size, exectype=bt.Order.Market)
                self.log(f'BUY CREATE, Price: {self.dataclose[0]:.2f}, Size: {size}')
        else:
            if prev_close < prev_bot:
                self.order = self.sell(size=self.position.size, exectype=bt.Order.Market)
                self.log(f'SELL CREATE, Price: {self.dataclose[0]:.2f}, Size: {self.position.size}')
            elif current_close < current_ema:
                self.order = self.sell(size=self.position.size, exectype=bt.Order.Market)
                self.log(f'SELL CREATE (EMA), Price: {self.dataclose[0]:.2f}, Size: {self.position.size}')

        