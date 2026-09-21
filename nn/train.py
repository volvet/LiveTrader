import os
import sys
from pathlib import Path
import gymnasium as gym
import numpy as np
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

from trade_env import StocksEnv
from dqn_agent import DQNAgent, DQNConfig

# Ensure imports like "from utils..." work no matter where this script is run from.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
import utils.net


def train(ticker='AAPL', start_date='2020-01-01', end_date='2021-01-01', retry=3):
    print('Training the agent...')
    data = utils.net.download_data(ticker, start_date, end_date, retry)
    if data is None:
        return    

    env = StocksEnv(data, window_size=30, render_mode='human', frame_bound=(30, len(data)))
    print(f"Environment created with observation space: {env.observation_space} and action space: {env.action_space}")
    
    config = DQNConfig()
    config.input_dim = env.observation_space.shape[0]
    config.output_dim = env.action_space.n
    print('DQN Config:', config)
    agent = DQNAgent(config)
    observation, info = env.reset()
    print('Initial observation shape:', observation.shape)
    epsilon = 1.0
    while True:
        #action = env.action_space.sample()  # Random action for demonstration
        action = agent.get_action(np.expand_dims(observation[:,1].squeeze(), axis=0), epsilon)
        next_observation, reward, terminated, truncated, info = env.step(action)
        print(f"{env._current_tick}/{env._end_tick} Action: {action}, Reward: {reward}, Terminated: {terminated}, Truncated: {truncated}, {observation.shape}, Info: {info}")
        if terminated or truncated:
            observation, info = env.reset()
            break
        agent.update(np.expand_dims(observation[:,1].squeeze(), axis=0), 
                     action, 
                     reward, 
                     np.expand_dims(next_observation[:,1].squeeze(), axis=0), 
                     terminated)
        epsilon = max(0.01, epsilon * 0.995)  # Decay epsilon
        next_observation = observation
    #plt.cla()
    #env.unwrapped.render_all()
    #plt.show()
    agent.qnet.save(str(PROJECT_ROOT)+ "/models/model_dqn_v0" + '.keras')

if __name__ == "__main__":
    utils.net.setup_proxy(utils.net.PROXY)
    train()




