import os
import sys
from pathlib import Path
import gymnasium as gym
import numpy as np
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import gym_trading_env
from gym_trading_env.renderer import Renderer

from trade_env import StocksEnv
from dqn_agent import DQNAgent, DQNConfig

# Ensure imports like "from utils..." work no matter where this script is run from.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
import utils.net


# Create your own reward function with the history object
def reward_function(history):
    return np.log(history["portfolio_valuation", -1] / history["portfolio_valuation", -2]) #log (p_t / p_t-1 )

def train(ticker='AAPL', start_date='2020-01-01', end_date='2021-01-01', epochs = 1):
    data = utils.net.download_data(ticker, start_date, end_date)
    if data is None:
        return
    data.rename(columns={'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close', 'Volume': 'volume'}, inplace=True)
    df = data
    df["feature_close"] = df["close"].pct_change()
    df["feature_open"] = df["open"]/df["close"]
    df["feature_high"] = df["high"]/df["close"]
    df["feature_low"] = df["low"]/df["close"]
    df["feature_volume"] = df["volume"] / df["volume"].rolling(7).max()
    df.dropna(inplace= True)
    length = df.shape[0]

    env = gym.make(
        "TradingEnv",
        name = "TradingEnv-v0",
        df = df,
        windows= 30,
        positions = [0, 0.5, 1], # From -1 (=SHORT), to +1 (=LONG)
        initial_position = 0, #Initial position
        trading_fees = 0.01/100, # 0.01% per stock buy / sell
        borrow_interest_rate= 0.0003/100, #per timestep (= 1h here)
        reward_function = reward_function,
        portfolio_initial_value = 10000, # in FIAT (here, USD)
        max_episode_duration = 'max',
        disable_env_checker= True
    )
    env.add_metric('Position Changes', lambda history : np.sum(np.diff(history['position']) != 0) )
    env.add_metric('Episode Lenght', lambda history : len(history['position']) )
    
    config = DQNConfig()
    config.input_dim = env.observation_space.shape[0]
    config.output_dim = env.action_space.n
    print('DQN Config:', config)
    agent = DQNAgent(config)

    done, truncated = False, False
    observation, info = env.reset()
    observation = np.expand_dims(observation[:,0].squeeze(), axis=0)
    #print(f'observation.shape: {observation.shape}')
    #print(observation)
    for epoch in range(epochs):
        epsilon = 1.0
        while not done and not truncated:
            action = agent.get_action(observation, epsilon)
            next_observation, reward, done, truncated, info = env.step(action)
            next_observation = np.expand_dims(next_observation[:,0].squeeze(), axis=0)
            #print(f'next_observation.shape: {next_observation.shape}')
            #print(next_observation)
            if done or truncated:
                print(f'Eposh {epoch}/{epochs} finished with portfolio value: {env.historical_info[-1]["portfolio_valuation"]}')
                observation, info = env.reset()
                observation = np.expand_dims(observation[:,0].squeeze(), axis=0)
                break
            loss =agent.update(next_observation, 
                         action, 
                         reward,
                         observation, 
                         done)
            
            print(f"{epoch}/{epochs} {env._idx}/{length} Action: {action}, Reward: {reward:.2f}, Truncated: {truncated}, Portfolio: {env.historical_info[-1]['portfolio_valuation']:.2f}, Loss {loss}")
            epsilon = max(0.01, epsilon * 0.995)  # Decay epsilon
            observation = next_observation
            
        # Save the model after each epoch
        agent.save()
        

if __name__ == "__main__":
    utils.net.setup_proxy(utils.net.PROXY)
    #train()
    train()
    




