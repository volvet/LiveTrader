import backtrader as bt
import numpy as np

class RegimeFilteredTrendStrategy(bt.Strategy):
    params = (
        ('ma_fast', 7), 
        ('ma_slow', 30),
        ('ma_trend_threshold', 0.02),
        ('adx_period', 14),
        ('adx_trending_threshold', 20),
        ('bb_period', 7),
        ('bb_width_threshold', 0.01),
        ('volatility_loopback', 7),
        ('vol_trending_threshold', 0.01),
        ('atr_period', 14),
        ('trail_atr_mult', 3.0),
        ('range_atr_mult', 1.),
        ('max_position_pct', 0.8),
        ('min_position_pct', 0.2),
        ('regime_confirmation', 3),
    )
    
    def __init__(self):
        self.ma_fast = bt.indicators.SMA(period=self.params.ma_fast)
        self.ma_slow = bt.indicators.SMA(period=self.params.ma_slow)
        self.adx = bt.indicators.ADX(period=self.params.adx_period)
        self.bb = bt.indicators.BollingerBands(period=self.params.bb_period)
        self.atr = bt.indicators.ATR(period=self.params.atr_period)
        
        self.order = None
        self.trail_order = None
        self.current_regime = None
        self.regime_history = []
        self.regime_confidence = 0
        self.volatility_history = []
        
    def cancel_trail(self):
        if self.trail_order:
            self.cancel(self.trail_order)
            self.trail_order = None
            
    def calculate_volatility(self):
        if len(self.atr) == 0 or self.dataclose[0] <= 0:
            return 0
        try:
            return self.atr[0] / self.dataclose[0]
        except:
            return 0
        
    def classify_regime(self):
        if len(self.adx) == 0 or len(self.bb) == 0:
            return 'unknown', 0
        
        try:
            trending_signals = 0
            total_signals = 0
            
            # ADX
            total_signals += 1
            if self.adx[0] > self.params.adx_trending_threshold:
                trending_signals += 1
                
            total_signals += 1
            bb_width = (self.bb.lines.top[0] - self.bb.lines.bot[0]) / self.bb.mid[0]
            if bb_width > self.params.bb_width_threshold:
                trending_signals += 1
                
            total_signals += 1
            current_vol = self.volatility_history[-1]
            if self.current_vol > self.params.vol_trending_threshold:
                trending_signals += 1
                
            total_signals += 1
            ma_seperation = abs(self.ma_fast[0] - self.ma_slow[0]) / self.ma_slow[0]
            if ma_seperation > self.params.ma_trend_threshold:
                trending_signals += 1
                
            confidence = total_signals / total_signals
            if confidence >= 0.75:
                regime = 'trending'
            elif confidence <= 0.25:
                regime = 'ranging'
            else:
                regime = 'unknown'
            return regime, confidence
        except:
            return 'unknown', 0
        
    def update_regime_state(self):
        new_regime, confidence = self.classify_regime()
        self.regime_history.append(new_regime)
        if len(self.regime_history) > self.params.regime_confirmation*2:
            self.regime_history = self.regime_history[-self.params.regime_confirmation*2:]
            
        if len(self.regime_history) >= self.params.regime_confirmation:
            recent_regimes = self.regime_history[-self.params.regime_confirmation:]
            if all(r == new_regime for r in recent_regimes):
                if self.current_regime != new_regime:
                    self.current_regime = new_regime
                    self.regime_confidence = confidence
            else:
                self.regime_confidence = confidence
                
    def calculate_regime_position_size(self):
        try:
            base_size = self.params.max_position_pct
            if self.current_regime == 'trending':
                size_factor = 1.0
            elif self.current_regime == 'ranging':
                size_factor = 0.3
            else:
                size_factor = 0.1
            confidence_factor = max(0.5, self.regime_confidence)
            final_size = base_size * size_factor * confidence_factor
            return max(self.params.min_position_pct, min(self.params.max_position_pct, final_size))
        except:
            return self.params.min_position_pct

    def get_adaptive_stop_multiplier(self):
        if self.current_regime == 'trending':
            best_mult = self.params.trail_atr_mult
            if len(self.volatility_history) >= 5:
                current_vol = self.volatility_history[-1]
                avg_vol = np.mean(self.volatility_history[-10:]) if len(self.volatility_history) >= 10 else np.mean(self.volatility_history)
                if current_vol > avg_vol * 1.2:
                    return best_mult * 1.3
                elif current_vol < avg_vol * 0.8:
                    return best_mult * 0.8
            return best_mult
        else:
            return self.params.range_atr_mult

    def should_trade_trend_following(self):
        if self.current_regime == 'trending':
            return True
        elif self.current_regime == 'ranging':
            return False
        else:
            return self.regime_confidence > 0.7
        
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        self.order = None

    def notify_trade(self, trade):
        if trade.isclosed:
            self.log(f'{self.data.datetime.data[0]} Trade PnL: {trade.pnl:.2f}')

    def next(self):
        if self.order:
            return
        
        current_vol = self.calculate_volatility()
        if current_vol > 0:
            self.volatility_history.append(current_vol)
            if len(self.volatility_history) > self.params.volatility_loopback:
                self.volatility_history = self.volatility_history[-self.params.volatility_loopback:]
        self.update_regime_state()
        if self.position:
            stop_multiplier = self.get_adaptive_stop_multiplier()
            if not self.trail_order:
                if self.position.size > 0:
                    self.trail_order = self.sell(
                        exectype=bt.Order.StopTrail,
                        trailamount = self.atr[0] * stop_multiplier,
                        size = self.position.size
                    )
                else:
                    self.trail_order = self.buy(
                        exectype = bt.Order.StopTrail,
                        trailamount = self.atr[0] * stop_multiplier,
                        size = abs(self.position.size)
                    )

            if self.position.size > 0:
                if (self.ma_fast[0] < self.ma_slow[0]) or (self.current_regime == 'trending'):
                    self.cancel_trail()
                    self.order = self.close()
                else:
                    if (self.ma_fast[0] > self.ma_slow[0]) or (self.current_regime == 'trending'):
                        self.cancel_trail()
                        self.order = self.close()
                return
            
        required_bars = max(self.params.ma_slow, self.params.adx_period, self.params.bb_period)
        if len(self) < required_bars:
            return

        if not self.should_trade_trend_following():
            return
        
        



