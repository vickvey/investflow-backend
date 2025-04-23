from datetime import datetime
import pandas as pd
import numpy as np
from data_fetcher import DataFetcher
import logging
from stock_service import _process_stock_data



def get_factor_model_return(
    ticker: str,
    start: datetime,
    end: datetime,
    factor_data_path: str,
    frequency: str = 'D'
) -> dict:
    """
    Estimate return using Fama-French 3-factor model.

    Parameters:
        ticker (str): Stock ticker.
        start (datetime): Start date.
        end (datetime): End date.
        factor_data_path (str): CSV file path to Fama-French factors (must include Mkt-RF, SMB, HML, RF).
        frequency (str): 'D' for daily or 'M' for monthly.

    Returns:
        dict: Factor model alpha, betas, and R-squared.
    """
    if start >= end:
        raise ValueError("Start date must be earlier than end date.")

    import statsmodels.api as sm

    # Fetch and process stock data
    stock_data = _process_stock_data(DataFetcher.single_stock_data(ticker, start, end), ticker)
    stock_df = pd.DataFrame(stock_data).set_index('Date')
    stock_df.index = pd.to_datetime(stock_df.index)
    stock_df['Return'] = stock_df['Close'].pct_change() * 100
    stock_df = stock_df.dropna()

    # Read factor data
    factor_df = pd.read_csv(factor_data_path)
    factor_df.columns = [col.strip() for col in factor_df.columns]
    factor_df['Date'] = pd.to_datetime(factor_df['Date'])
    factor_df = factor_df.set_index('Date')

    # Match frequency
    if frequency.upper() == 'M':
        stock_df = stock_df.resample('M').last()
        stock_df['Return'] = stock_df['Close'].pct_change() * 100
        stock_df = stock_df.dropna()
        factor_df = factor_df.resample('M').mean()

    # Merge returns and factors
    merged = stock_df[['Return']].join(factor_df[['Mkt-RF', 'SMB', 'HML', 'RF']], how='inner')
    merged['Excess Return'] = merged['Return'] - merged['RF']

    # Regression
    X = merged[['Mkt-RF', 'SMB', 'HML']]
    X = sm.add_constant(X)
    y = merged['Excess Return']

    model = sm.OLS(y, X).fit()

    return {
        'ticker': ticker,
        'alpha': round(model.params['const'], 4),
        'beta_MKT-RF': round(model.params['Mkt-RF'], 4),
        'beta_SMB': round(model.params['SMB'], 4),
        'beta_HML': round(model.params['HML'], 4),
        'r_squared': round(model.rsquared, 4)
    }
