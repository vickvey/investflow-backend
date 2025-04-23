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
        list of dict: A list where each dictionary contains two keys:
            - 'date': The date of the return (datetime object).
            - 'return': The computed return (either log or simple return), rounded to 6 decimal places (float).
    
    Example:
        [{'date': '2021-01-01', 'return': 0.001234}, {'date': '2021-01-04', 'return': -0.002456}, ...]
    
    Raises:
        ValueError: If start date is not earlier than end date, or if 'Close' column is missing.
        ValueError: If an invalid return type is provided.
    """
    if start >= end:
        raise ValueError("Start date must be earlier than end date.")
    
    # Fetch raw stock data
    raw_data = DataFetcher.single_stock_data(ticker, start, end)
    
    # Process the raw data (ensure the correct format and structure)
    data = _process_stock_data(raw_data, ticker)
    
    # Ensure 'Close' column exists
    if 'Close' not in data.columns:
        raise ValueError("'Close' column missing in data")

    # Compute returns
    if return_type == 'log':
        data['Return'] = np.log(data['Close'] / data['Close'].shift(1))
    elif return_type == 'simple':
        data['Return'] = data['Close'].pct_change()
    else:
        raise ValueError("Invalid return_type. Choose 'log' or 'simple'.")

    # Drop missing values and convert to list of dicts
    return_data = data.dropna(subset=['Return'])
    
    # Vectorized approach to convert DataFrame to list of dictionaries
    return return_data[['Date', 'Return']].apply(
        lambda row: {'date': row['Date'], 'return': round(row['Return'], 6)}, axis=1
    ).tolist()

def compute_historical_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """
    Compute daily percentage returns from price data for multiple tickers.
    
    Parameters:
        prices (pd.DataFrame): DataFrame with dates as index and tickers as columns containing closing prices.
    
    Returns:
        pd.DataFrame: Daily returns for each ticker. Each column represents a ticker, and the index is the date.
    
    Raises:
        ValueError: If the prices DataFrame does not have the correct format (e.g., missing 'Close' prices).
    """
    # Ensure that the 'prices' DataFrame has dates as index and contains no missing data
    if not isinstance(prices.index, pd.DatetimeIndex):
        raise ValueError("The index of the 'prices' DataFrame must be a DatetimeIndex.")
    
    if prices.isnull().any().any():
        raise ValueError("Price data contains missing values.")
    
    # Compute daily percentage returns and drop missing values
    returns = prices.pct_change().dropna()
    
    # Return daily returns DataFrame
    return returns
