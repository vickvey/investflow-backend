from datetime import datetime
import pandas as pd
import numpy as np
from services.data_fetcher import DataFetcher
from services.stock_service import _process_stock_data

def get_historical_returns(ticker: str, start: datetime, end: datetime, return_type: str = 'log') -> list:
    """
    Fetch and compute historical returns for a stock over a given date range.
    
    Parameters:
        ticker (str): Stock ticker symbol.
        start (datetime): Start date.
        end (datetime): End date.
        return_type (str): Type of return - 'log' or 'simple'.

    Returns:
        list of dict: Each dict contains 'date' and 'return' keys.
    """
    if start >= end:
        raise ValueError("Start date must be earlier than end date.")
    
    raw_data = DataFetcher.single_stock_data(ticker, start, end)
    data = _process_stock_data(raw_data, ticker)
    
    if 'Close' not in data.columns:
        raise ValueError("'Close' column missing in data")
    
    if return_type == 'log':
        data['Return'] = np.log(data['Close'] / data['Close'].shift(1))
    elif return_type == 'simple':
        data['Return'] = data['Close'].pct_change()
    else:
        raise ValueError("Invalid return_type. Choose 'log' or 'simple'.")

    return_data = data.dropna(subset=['Return'])
    return [
        {
            'date': row['Date'],
            'return': round(row['Return'], 6)
        }
        for _, row in return_data.iterrows()
    ]

def compute_historical_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """
    Compute daily percentage returns from price data for multiple tickers.
    
    Parameters:
        prices (pd.DataFrame): DataFrame with dates as index and tickers as columns containing closing prices.
    
    Returns:
        pd.DataFrame: Daily returns for each ticker.
    """
    returns = prices.pct_change().dropna()
    return returns