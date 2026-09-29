import sys
from pathlib import Path
import backtrader as bt
import numpy as np

# Ensure imports like "from utils..." work no matter where this script is run from.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
from nn.dqn_agent import DQNAgent, DQNConfig

class DQNStrategy(bt.Strategy):
    params = (
        ('window_size', 30),
    )

    def __init__(self):
        config = DQNConfig()
        config.input_dim = self.params.window_size
        config.output_dim = 2
        config.resume = True
        self.dqn_agent = DQNAgent(config)
        self.dataclose = self.datas[0].close
        self.order = None

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()} - {txt}')

    def notify_order(self, order):
        self.order = None
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED, Price: {order.executed.price:.2f}, Cost: {order.executed.value:.2f}, Comm: {order.executed.comm:.2f}')
            elif order.issell():
                self.log(f'SELL EXECUTED, Price: {order.executed.price:.2f}, Cost: {order.executed.value:.2f}, Comm: {order.executed.comm:.2f}')
            elif order.status in [order.Canceled, order.Margin, order.Rejected]:
                self.log('Order Canceled/Margin/Rejected')

    def notify_trade(self, trade):
        if trade.isclosed:
            self.log(f'TRADE PROFIT, GROSS: {trade.pnl:.2f}, NET: {trade.pnlcomm:.2f}')

    def next(self):
        if self.order:
            return

        if len(self) < self.params.window_size + 1:
            return

        state = []
        for i in range(0, self.params.window_size + 1):
            state.append(self.dataclose[-self.params.window_size - 1 + i])
        state = np.diff(state) / state[:-1]  # Convert to percentage change
        state = np.expand_dims(state.reshape(1, -1), axis=-1)
        action = self.dqn_agent.get_action(state)
        #print(f"Action taken: {action} at price {self.dataclose[0]}")
        ## TODO: Implement the logic to execute buy/sell based on the action returned by the DQN agent.
        if not self.position:
            if action == 1:  # Buy
                cash = self.broker.getcash()
                size = int(cash * 0.95 / self.data.close[0])
                self.order = self.buy(size=size, exectype=bt.Order.Market)
                self.log(f'BUY CREATE, Price: {self.dataclose[0]:.2f}, Size: {size}')
        else:
            if action == 0:  # Sell
                self.order = self.sell(size=self.position.size, exectype=bt.Order.Market)
                self.log(f'SELL CREATE (EMA), Price: {self.dataclose[0]:.2f}, Size: {self.position.size}')
