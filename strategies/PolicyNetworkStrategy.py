import sys
from pathlib import Path
import backtrader as bt
import numpy as np

# Ensure imports like "from utils..." work no matter where this script is run from.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
from nn.policy_agent import PolicyAgent, PolicyConfig

class PolicyNetworkStrategy(bt.Strategy):
    params = (
        ('window_size', 30),
    )

    def __init__(self):
        config = PolicyConfig()
        config.input_dim = self.params.window_size
        config.output_dim = 2
        config.resume = True
        self.policy_agent = PolicyAgent(config)
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
                self.log(f'BUY EXECUTED, Price: {order.executed.price:.2f}, Size: {order.executed.size}, Cost: {order.executed.value:.2f}, Comm: {order.executed.comm:.2f}')
            elif order.issell():
                self.log(f'SELL EXECUTED, Price: {order.executed.price:.2f}, Size: {order.executed.size}, Cost: {order.executed.value:.2f}, Comm: {order.executed.comm:.2f}')
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
        state = np.expand_dims(state, axis=0)
        action = self.policy_agent.get_action(state)
        #print(f"Action taken: {action} at price {self.dataclose[0]}")
        ## TODO: Implement the logic to execute buy/sell based on the action returned by the DQN agent.
        #self.log(f"Action taken: {action} at price {self.dataclose[0]}")
        #if action == 0:
        #    if self.position.size != 0:
        #        self.order = self.sell(size=self.position.size, exectype=bt.Order.Market)
        #elif action == 2:
        #    cash = self.broker.getcash()
        #    size = int(cash * 0.95 / self.data.close[0])
        #    if size > 0:
        #        self.order = self.buy(size=size, exectype=bt.Order.Market)
        #elif action == 1:
        #    cash = self.broker.getcash()
        #    stock_value = self.position.size * self.data.close[0]
        #    total_value = cash + stock_value
        #    if stock_value == 0:
        #        size = int(cash * 0.5 * 0.95 / self.data.close[0])
        #        if size > 0:
        #            self.order = self.buy(size=size, exectype=bt.Order.Market)
        #    elif cash < total_value * 0.5:
        #        size = self.position.size / 2
        #        if size > 0:
        #            self.order = self.sell(size=size, exectype=bt.Order.Market)

        if not self.position and action == 1:
            cash = self.broker.getcash()
            size = int(cash * 0.95 / self.data.close[0])
            self.order = self.buy(size=size, exectype=bt.Order.Market)
            self.log(f'BUY CREATE, Price: {self.dataclose[0]:.2f}, Size: {size}')
        elif self.position and action == 0:
            self.order = self.sell(size=self.position.size, exectype=bt.Order.Market)
            self.log(f'SELL CREATE, Price: {self.dataclose[0]:.2f}, Size: {self.position.size}')
        
