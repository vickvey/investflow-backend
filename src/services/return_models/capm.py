from datetime import datetime
import pandas as pd
import numpy as np
from data_fetcher import DataFetcher
import logging
from stock_service import _process_stock_data


def get_capm_expected_return(
    ticker: str,
    start: datetime,
    end: datetime,
    
    benchmark_ticker: str = '^GSPC',
    risk_free_rate: float = 2.0,
    expected_market_return: float = 8.0
) -> dict:
    """
    Estimate expected return using CAPM model.

    Parameters:
        ticker (str): The stock ticker.
        start (datetime): Start date for historical data.
        end (datetime): End date for historical data.
        benchmark_ticker (str): Benchmark index (default: S&P 500).
        risk_free_rate (float): Annualized risk-free rate in percent.
        expected_market_return (float): Expected annual market return in percent.

    Returns:
        dict: CAPM expected return, beta, and underlying components.
    """
    if start >= end:
        raise ValueError("Start date must be earlier than end date.")
    
    # Cap the end date
    end = min(end, datetime.now())

    # Fetch stock and benchmark data
    stock_data = _process_stock_data(DataFetcher.single_stock_data(ticker, start, end), ticker)
    benchmark_data = _process_stock_data(DataFetcher.benchmark_data(benchmark_ticker, start, end), benchmark_ticker)
    
    # Set index for both
    stock_df = pd.DataFrame(stock_data).set_index('Date')
    benchmark_df = pd.DataFrame(benchmark_data).set_index('Date')

    # Calculate returns
    stock_df['Return_stock'] = stock_df['Close'].pct_change()
    benchmark_df['Return_benchmark'] = benchmark_df['Close'].pct_change()

    # Merge returns
    merged_df = pd.merge(
        stock_df[['Return_stock']],
        benchmark_df[['Return_benchmark']],
        left_index=True, right_index=True, how='inner'
    ).dropna()

    if merged_df.empty:
        raise ValueError("No overlapping return data for CAPM computation.")

    # Calculate beta
    cov_matrix = merged_df.cov() * 252  # Annualized
    beta = cov_matrix.loc['Return_stock', 'Return_benchmark'] / cov_matrix.loc['Return_benchmark', 'Return_benchmark']

    # Calculate expected return using CAPM
    capm_return = risk_free_rate + beta * (expected_market_return - risk_free_rate)

    return {
        'ticker': ticker,
        'benchmark': benchmark_ticker,
        'start': start.strftime('%Y-%m-%d'),
        'end': end.strftime('%Y-%m-%d'),
        'beta': round(beta, 4),
        'riskFreeRate (%)': round(risk_free_rate, 2),
        'expectedMarketReturn (%)': round(expected_market_return, 2),
        'expectedReturnCAPM (%)': round(capm_return, 2)
    }
