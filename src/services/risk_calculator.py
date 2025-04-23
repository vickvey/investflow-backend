import numpy as np
import pandas as pd

def compute_covariance_matrix(returns: pd.DataFrame) -> pd.DataFrame:
    """
    Compute the covariance matrix from returns data.
    
    Parameters:
        returns (pd.DataFrame): DataFrame of daily returns with tickers as columns.
    
    Returns:
        pd.DataFrame: Covariance matrix.
    """
    return returns.cov()

def compute_downside_deviation(returns: pd.Series, target: float = 0) -> float:
    """
    Compute the downside deviation of returns below a target.
    
    Parameters:
        returns (pd.Series): Series of portfolio returns.
        target (float): Target return, default is 0.
    
    Returns:
        float: Downside deviation.
    """
    downside_returns = returns[returns < target]
    if len(downside_returns) == 0:
        return 0
    return np.sqrt(np.mean(downside_returns**2))

def compute_max_drawdown(prices: pd.Series) -> float:
    """
    Compute the maximum drawdown from a series of prices.
    
    Parameters:
        prices (pd.Series): Series of portfolio prices.
    
    Returns:
        float: Maximum drawdown as a negative fraction.
    """
    rolling_max = prices.cummax()
    drawdowns = (prices - rolling_max) / rolling_max
    return drawdowns.min()