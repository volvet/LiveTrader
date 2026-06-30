import backtrader as bt

class AdxStrategy(bt.Strategy):
    params = (
        ('adx_period', 14),
        ('adx_threshold', 25),  # Threshold for trend strength
    )

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()} - {txt}')  

    def __init__(self):
        self.log('Initializing AdxStrategy...')
        self.dataclose = self.datas[0].close
        self.adx = bt.indicators.ADX(self.datas[0], period=self.params.adx_period)
        self.plus_di = bt.indicators.PlusDI(self.datas[0], period=self.params.adx_period)
        self.minus_di = bt.indicators.MinusDI(self.datas[0], period=self.params.adx_period)
        self.order = None
        self.log('AdxStrategy initialized.')

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
        
        current_adx = self.adx[0]
        current_plus_di = self.plus_di[0]
        current_minus_di = self.minus_di[0]
        current_close = self.dataclose[0]
        previous_plus_di = self.plus_di[-1]
        previous_minus_di = self.minus_di[-1]

        if current_adx > self.params.adx_threshold:
            if current_plus_di > current_minus_di and previous_plus_di <= previous_minus_di:
                self.log(f'BUY SIGNAL: ADX: {current_adx:.2f}, +DI: {current_plus_di:.2f}, -DI: {current_minus_di:.2f}, Close: {current_close:.2f}')
                if not self.position:
                    self.log(f'Placing BUY order at Close: {current_close:.2f}')
                    self.order = self.buy()
            elif current_minus_di > current_plus_di and previous_minus_di <= previous_plus_di:
                self.log(f'SELL SIGNAL: ADX: {current_adx:.2f}, +DI: {current_plus_di:.2f}, -DI: {current_minus_di:.2f}, Close: {current_close:.2f}')
                if self.position.size > 0:
                    self.log(f'Placing SELL order at Close: {current_close:.2f}')
                    self.order = self.sell()
        else:
            pass
            #self.log(f'No strong trend detected: ADX: {current_adx:.2f}, +DI: {current_plus_di:.2f}, -DI: {current_minus_di:.2f}, Close: {current_close:.2f}')