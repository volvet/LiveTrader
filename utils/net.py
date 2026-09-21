import os
import yfinance as yf
import pandas as pd

PROXY = 'http://127.0.0.1:7897'

def setup_proxy(proxy_url):
    os.environ['HTTP_PROXY'] = proxy_url
    os.environ['HTTPS_PROXY'] = proxy_url
    
def download_data(ticker, start_date, end_date, retry=3):
    for attempt in range(retry):
        data = yf.download(ticker, start=start_date, end=end_date)
        data = data.droplevel(1, axis=1) if isinstance(data.columns, pd.MultiIndex) else data
        if data is None or data.empty:
            print(f"No data found for {ticker} between {start_date} and {end_date}.")
            continue
        else:
            print(f"Data for {ticker} downloaded successfully. Data shape: {data.shape}")
            return data
    print(f"Failed to download data for {ticker} after {retry} attempts.")
    return None
