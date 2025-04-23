from datetime import datetime
import pandas as pd
import numpy as np
from data_fetcher import DataFetcher
import logging





def get_equal_weighted_return(tickers: list[str], start: datetime, end: datetime) -> dict:
    """
    Compute equal-weighted portfolio return for a list of stocks over a date range.

    Parameters:
        tickers (list of str): List of stock tickers.
        start (datetime): Start date.
        end (datetime): End date.

    Returns:
        dict: Portfolio return and daily return time series.
    """
    if start >= end:
        raise ValueError("Start date must be earlier than end date.")
    if not tickers or not isinstance(tickers, list) or len(tickers) < 2:
        raise ValueError("Provide a list of at least two stock tickers.")

    import numpy as np

    # Fetch close prices for multiple tickers
    raw_data = DataFetcher.multiple_stocks_data(tickers, start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'))
    if raw_data.empty:
        raise ValueError("No data returned for the given tickers and date range.")

    # Ensure it's a DataFrame and drop rows with any NaNs
    df = pd.DataFrame(raw_data).dropna(how='any')

    # Calculate daily percentage returns
    daily_returns = df.pct_change().dropna()

    # Equal-weighted portfolio return: average of daily returns
    daily_returns['EqualWeightedReturn'] = daily_returns.mean(axis=1)
    cumulative_return = ((1 + daily_returns['EqualWeightedReturn']).prod() - 1) * 100

    return {
        'tickers': tickers,
        'start': start.strftime('%Y-%m-%d'),
        'end': end.strftime('%Y-%m-%d'),
        'equalWeightedCumulativeReturn (%)': round(cumulative_return, 2),
        'dailyReturns': [
            {'date': idx.strftime('%Y-%m-%d'), 'return': round(ret, 6)}
            for idx, ret in daily_returns['EqualWeightedReturn'].items()
        ]
    }
