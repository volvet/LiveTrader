import yfinance as yf
import backtrader as bt
import pandas as pd

def backtest(ticker,
             strategy_class,
             start_data='2023-01-01',
             end_data='2025-12-31',
             initial_cash = 10000.0,
             commission = 0.001
             ):
    try:
        data = yf.download(ticker, start_data=start_data, end=end_data)
        data = data.droplevel(1, axis=1) if isinstance(data.columns, pd.MultiIndex) else data
    except Exception as e:
        print(f"Error downloading data for {ticker}: {e}")
        return
    
    data_feed = bt.feeds.PandasData(dataname=data)
    cerebro = bt.Cerebro()
    cerebro.adddata(data_feed)
    cerebro.broker.setcash(initial_cash)
    cerebro.broker.setcommission(commission=commission)
    
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe_ratio', timeframe=bt.TimeFrame.Days, riskfreerate=0.0)
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.Returns, _name="returns")
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trade_analyzer')
    
    cerebro.addstrategy(strategy_class)
    start_value = cerebro.broker.getvalue()
    strats = cerebro.run()
    final_value = cerebro.broker.getvalue()
    ret = (final_value - start_value) / start_value * 100.0
    print(f'Backtest completed for {ticker} using {strategy_class.__name__}')
    print(f'Initial {start_value}, Final {final_value}, Return: {ret:.2f}%')
    
    sh = strats[0].analyzers.sharpe_ratio.get_analysis()
    dd = strats[0].analyzers.drawdown.get_analysis()
    rets = strats[0].analyzers.returns.get_analysis()
    tr = strats[0].analyzers.trade_analyzer.get_analysis()
    
    print(f"Sharpe: {sh}")
    print(f"Max DD: {dd.get('max', {}).get('drawdown', 0):.2f}%  Len: {dd.get('max', {}).get('len', 0)}")
    print(f"CAGR:   {rets.get('rnorm100', 0):.2f}%  Total: {rets.get('rtot', 0)*100:.2f}%")
    print(f"Trades: {tr.get('total', {}).get('total', 0)}  Won: {tr.get('won', {}).get('total', 0)}  Lost: {tr.get('lost', {}).get('total', 0)}")    

    #plt.rcParams['figure.figsize'] = [10, 6]
    #plt.rcParams['font.size'] = 10
    cerebro.plot(iplot=False)
    return
    
    
    
    

