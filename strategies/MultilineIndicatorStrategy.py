import backtrader as bt

class MultilineIndicatorStrategy(bt.Strategy):
    params = (
        ('macd_fast_period', 12),
        ('macd_slow_period', 26),
        ('macd_signal_period', 9),
        ('bb_peroid', 20),
        ('bb_devfactor', 2),
    )

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()} - {txt}')

    def __init__(self):
        self.log('Initializing MultilineIndicatorStrategy...')
        self.dataclose = self.datas[0].close
        self.macd = bt.indicators.MACD(self.datas[0], 
                                       period_me1=self.params.macd_fast_period, 
                                       period_me2=self.params.macd_slow_period, 
                                       period_signal=self.params.macd_signal_period)
        self.bb = bt.indicators.BollingerBands(self.datas[0], 
                                               period=self.params.bb_peroid, 
                                               devfactor=self.params.bb_devfactor)
        self.log('MultilineIndicatorStrategy initialized.')

    def next(self):
        macd_line = self.macd.lines.macd[0]
        signal_line = self.macd.lines.signal[0]
        histo_value = macd_line - signal_line
        top_band = self.bb.lines.top[0]
        mid_band = self.bb.lines.mid[0]
        bot_band = self.bb.lines.bot[0]
        current_close = self.dataclose[0]
        if macd_line > signal_line and current_close > top_band:
            self.log(f'Potential breakout signal: MACD: {macd_line:.2f}, Signal: {signal_line:.2f}, Close: {current_close:.2f}, Top Band: {top_band:.2f}')
        elif current_close < bot_band:
            self.log(f'Price below bot_band : Close: {current_close:.2f}, Bottom Band: {bot_band:.2f}')