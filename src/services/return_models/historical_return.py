import pandas as pd

def compute_returns(prices):
    """
    Compute daily percentage returns from price data.
    
    Parameters:
    - prices: pandas DataFrame with dates as index and tickers as columns.
    
    Returns:
    - pandas DataFrame of daily returns.
    """
    returns = prices.pct_change().dropna()
    return returns