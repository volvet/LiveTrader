import backtrader as bt

class BBandsMeansReversionStrategy(bt.Strategy):
    params = (
        ('bb_period', 20),
        ('bb_devfactor', 2),
    )

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()} - {txt}')

    def __init__(self):
        self.log('Initializing BBandsMeansReversionStrategy...')
        self.dataclose = self.datas[0].close
        self.bb = bt.indicators.BollingerBands(self.datas[0], 
                                               period=self.params.bb_period, 
                                               devfactor=self.params.bb_devfactor)
        self.order = None
        self.log('BBandsMeansReversionStrategy initialized.')

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            self.log(f'Order {order.getstatusname()} Ref: {order.ref}')
            return
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED, Price: {order.executed.price:.2f}, Cost: {order.executed.value:.2f}, Comm: {order.executed.comm:.2f}')
            elif order.issell():
                self.log(f'SELL EXECUTED, Price: {order.executed.price:.2f}, Cost: {order.executed.value:.2f}, Comm: {order.executed.comm:.2f}')
            self.bar_executed = len(self)
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log(f'Order {order.getstatusname()} Ref: {order.ref}')
        self.order = None

    def notify_trade(self, trade):
        if trade.isclosed:
            self.log(f'TRADE PROFIT, REF: {trade.ref}, GROSS: {trade.pnl:.2f}, NET: {trade.pnlcomm:.2f}')

    def next(self):
        if self.order:
            return  # Skip if there's a pending order
        
        current_close = self.dataclose[0]
        top_band = self.bb.lines.top[0]
        mid_band = self.bb.lines.mid[0]
        bot_band = self.bb.lines.bot[0]

        if not self.position: # Not in the market
            if current_close < bot_band:
                self.log(f'Bar: {len(self)}, BUY SIGNAL: Close: {current_close:.2f}, Bottom Band: {bot_band:.2f}')
                self.order = self.buy()
        else:
            if current_close > mid_band:
                self.log(f'Bar: {len(self)}, SELL SIGNAL: Close: {current_close:.2f}, Mid Band: {mid_band:.2f}')
                self.order = self.sell()
                self.order = self.close()