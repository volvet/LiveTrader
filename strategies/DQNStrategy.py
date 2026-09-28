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
        ('window_size', 60),
    )

    def __init__(self):
        config = DQNConfig()
        config.input_dim = self.params.window_size
        config.output_dim = 2
        config.resume = True
        self.dqn_agent = DQNAgent(config)
        self.dataclose = self.datas[0].close
        self.order = None

    def notify_order(self, order):
        self.order = None

    def next(self):
        if self.order:
            return

        if len(self) < self.params.window_size + 1:
            return

        state = []
        for i in range(0, self.params.window_size + 1):
            state.append(self.dataclose[-self.params.window_size - 1 + i])
        state = np.diff(state) / state[:-1]  # Convert to percentage change
        state = state.reshape(1, -1)
        action = self.dqn_agent.get_action(state)
        print(f"Action taken: {action} at price {self.dataclose[0]}")
        ## TODO: Implement the logic to execute buy/sell based on the action returned by the DQN agent.
