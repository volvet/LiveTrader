import backtrader as bt

class RelativeMomentumAccelStrategy(bt.Strategy):
    params = (
        ('kama_period', 30),
        ('fast_ema_period', 7),
        ('thrust_bb_period', 7),
        ('thrust_bb_devfactor', 1),
        ('atr_period', 7),
        ('atr_stop_multiplier', 3),
    )

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()} - {txt}')

    def __init__(self):
        self.kama = bt.indicators.KAMA(self.data.close, period=self.params.kama_period)
        self.fast_ema = bt.indicators.ExponentialMovingAverage(self.data_close, period=self.params.fast_ema_period)
        self.thrust_osc = (self.fast_ema - self.kama) / (self.kama + 1e-6)
        self.thrust_bb = bt.indicators.BollingerBands(self.thrust_osc, period=self.params.thrust_bb_period, devfactor=self.params.thrust_bb_devfactor)
        self.atr = bt.indicators.AverageTrueRange(self.data, period=self.params.atr_period)
        self.order = None
        self.stop_price = None
        self.highest_price_since_entry = None
        self.lowest_price_since_entry = None

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status in [order.Completed]:
            #if order.isbuy():
            #    self.log(f'BUY EXECUTED, Price: {order.executed.price:.2f}, Cost: {order.executed.value:.2f}, Comm: {order.executed.comm:.2f}')
            #elif order.issell():
            #    self.log(f'SELL EXECUTED, Price: {order.executed.price:.2f}, Cost: {order.executed.value:.2f}, Comm: {order.executed.comm:.2f}')
            if self.position and self.stop_price is None:
                if order.isbuy():
                    self.highest_price_since_entry = self.data.high[0]
                    self.stop_price = self.highest_price_since_entry - self.atr[0] * self.params.atr_stop_multiplier
                elif order.issell():
                    self.lowest_price_since_entry = self.data.low[0]
                    self.stop_price = self.lowest_price_since_entry + self.atr[0] * self.params.atr_stop_multiplier
            elif not self.position:
                self.stop_price = None
                self.highest_price_since_entry = None
                self.lowest_price_since_entry = None
        self.order = None

    def notify_trade(self, trade):
        if trade.isclosed:
            self.log(f'TRADE PROFIT, GROSS: {trade.pnl:.2f}, NET: {trade.pnlcomm:.2f}')

    def next(self):
        if self.order:
            return

        #self.log(self.position)
        if not self.position:
            #self.log(f'Bar: {len(self)}, Close: {self.data.close[0]:.2f}, KAMA: {self.kama[0]:.2f}, Fast EMA: {self.fast_ema[0]:.2f}, Thrust Osc: {self.thrust_osc[0]:.4f}, Thrust BB Top: {self.thrust_bb.lines.top[0]:.4f}, Thrust BB Bot: {self.thrust_bb.lines.bot[0]:.4f}')
            if self.thrust_osc[0] > self.thrust_bb.lines.top[0]:
                cash = self.broker.getcash()
                size = int(cash * 0.95 / self.data.close[0])
                #self.log(f'BUY SIGNAL: Thrust Osc: {self.thrust_osc[0]:.4f} > Thrust BB Top: {self.thrust_bb.lines.top[0]:.4f}, size = {size}')
                self.order = self.buy(size=size, exectype=bt.Order.Market)
        else:
            if self.thrust_osc[0] < self.thrust_bb.lines.bot[0]:
                if self.position.size > 0:
                    #self.log(f'SELL SIGNAL: Thrust Osc: {self.thrust_osc[0]:.4f} < Thrust BB Bot: {self.thrust_bb.lines.bot[0]:.4f}, size = {self.position.size}')
                    self.order = self.sell(size = self.position.size, exectype=bt.Order.Market)

            #if self.position.size > 0:
            #    if self.data.high[0] > self.highest_price_since_entry:
            #        self.highest_price_since_entry = self.data.high[0]
            #        self.stop_price = self.highest_price_since_entry - self.atr[0] * self.params.atr_stop_multiplier
            #    elif self.data.close[0] < self.stop_price:
            #        self.order = self.close()



