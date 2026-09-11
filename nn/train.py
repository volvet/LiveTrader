import os
import gymnasium as gym
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

from trade_env import StocksEnv


def train(ticker='AAPL', start_date='2020-01-01', end_date='2023-01-01', retry=3):
    print('Training the agent...')
    for attempt in range(retry):
        data = yf.download(ticker, start=start_date, end=end_date)
        data = data.droplevel(1, axis=1) if isinstance(data.columns, pd.MultiIndex) else data
        if data is None or data.empty:
            print(f"No data found for {ticker} between {start_date} and {end_date}.")
            continue
        else:
            print(f"Data for {ticker} downloaded successfully. Data shape: {data.shape}")
            break
    else:
        print(f"Failed to download data for {ticker} after {retry} attempts.")
        return

    env = StocksEnv(data, window_size=30, render_mode='human', frame_bound=(30, len(data)))
    print(f"Environment created with observation space: {env.observation_space} and action space: {env.action_space}")
    observation, info = env.reset()
    while True:
        action = env.action_space.sample()  # Random action for demonstration
        observation, reward, terminated, truncated, info = env.step(action)
        print(f"Action: {action}, Reward: {reward}, Terminated: {terminated}, Truncated: {truncated}")
        if terminated or truncated:
            observation, info = env.reset()
            break

    #plt.cla()
    #env.unwrapped.render_all()
    #plt.show()

if __name__ == "__main__":
    PROXY = 'http://127.0.0.1:7897'
    os.environ['HTTP_PROXY'] = PROXY
    os.environ['HTTPS_PROXY'] = PROXY
    train()




