# engine/utils.py
import pandas as pd

def compute_mu_S_from_prices(returns):
    """
    Compute expected returns and covariance matrix from price data.
    
    Parameters:
    - prices: pandas DataFrame with dates as index and tickers as columns.
    
    Returns:
    - tuple: (mu, S), where mu is a pandas Series and S is a pandas DataFrame.
    """
    # returns = prices.pct_change().dropna()

    mu = returns.mean()
    S = returns.cov()
    return mu, S


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