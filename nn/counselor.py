import os
import sys
import torch
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
import yfinance as yf
from rich.console import Console
from rich.table import Table

# Ensure imports like "from utils..." work no matter where this script is run from.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
from nn.policy_agent import PolicyAgent, PolicyConfig
from utils.net import setup_proxy, PROXY
import utils.net


if __name__ == "__main__":
    tickers = ['QQQ', 'QQQI', 'VOO', 'SPYI', 'NVDA', 'TSLA', 'AAPL', 'GOOG']
    model_path = str(PROJECT_ROOT)  + "/models/best_policy_agent.pth"
    setup_proxy(PROXY)

    today = datetime.today()
    day_beginning = today - timedelta(days=365)
    print(f"Today's date: {today}, One year ago: {day_beginning}")

    table = Table(title="Stock Predictions")
    table.add_column('Ticker', style="cyan")
    table.add_column('Price', style="green")
    table.add_column('SELL', style="red")
    table.add_column('BUY', style="yellow")

    for ticker in tickers:
        print(f"Processing ticker: {ticker}")
        data = utils.net.download_data(ticker, day_beginning, today)
        if data is None:
            continue
        data.rename(columns={'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close', 'Volume': 'volume'}, inplace=True)
        df = data
        df["feature_close"] = df["close"].pct_change()
        df["feature_open"] = df["open"]/df["close"]
        df["feature_high"] = df["high"]/df["close"]
        df["feature_low"] = df["low"]/df["close"]
        df["feature_volume"] = df["volume"] / df["volume"].rolling(7).max()
        df.dropna(inplace= True)
        length = df.shape[0]
        #print(df.tail(10))
        
        config = PolicyConfig()
        config.resume = True
        agent = PolicyAgent(config)
        # You can now use the agent to make predictions or evaluations for the current ticker.
        for i in range(length - config.input_dim):
            observation = df["feature_close"].iloc[i:i+config.input_dim].values
            observation = np.expand_dims(observation.squeeze(), axis=0)
            probs = agent.get_probs(observation)[0]
            if i == length - config.input_dim - 1:
                price = df.loc[df.index[i + config.input_dim], "close"].values[0]
                #print(f'Date: {df.index[i + config.input_dim]}, Price:{price:.2f} SELL/BUY: {probs}')

        table.add_row(ticker, f"{price:.2f}", f"{probs[0]:.2f}", f"{probs[1]:.2f}")

    console = Console()
    console.print(table)