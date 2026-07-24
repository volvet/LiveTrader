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
            return self.params.max_position_pct
        except:
            return self.params.min_position_pct
        
        
        
        
    def next(self):
        if not self.position and self.cross > 0:
            self.buy()
        elif self.position and self.cross < 0:
            self.close()




