from datetime import datetime
import pandas as pd
import numpy as np
from .data_fetcher import DataFetcher
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def single_stock(ticker: str, start: datetime, end: datetime) -> dict:
    """
    Fetch historical data for a single stock.
    """
    if start >= end:
        raise ValueError("Start date must be earlier than end date.")
    data = DataFetcher.single_stock_data(ticker, start, end)
    return {
        "ticker": ticker,
        "data": data.to_dict(orient="records")
    }

def multiple_stocks(tickers: list[str], start: datetime, end: datetime) -> list:
    """
    Fetch historical closing prices for multiple stocks.
    """
    if start >= end:
        raise ValueError("Start date must be earlier than end date.")
    data = DataFetcher.multiple_stocks_data(tickers, start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'))
    return data.to_dict(orient="records")

def today_performance(ticker: str) -> dict:
    """
    Fetch today's performance metrics for a stock.
    """
    return DataFetcher.today_performance(ticker)

def fixed_period_performance(ticker: str, period: str) -> dict:
    """
    Fetch performance metrics for a stock over a fixed period.
    """
    data = DataFetcher.stock_period_data(ticker, period)
    if data.empty:
        return {"error": f"No data available for {ticker} in period {period}"}
    data['Return'] = data['Close'].pct_change()
    open_price = data['Open'].iloc[0]
    close_price = data['Close'].iloc[-1]
    high = data['High'].max()
    low = data['Low'].min()
    total_return = ((close_price - open_price) / open_price) * 100
    result = {
        'Ticker': ticker,
        'Period': period,
        'Open': round(open_price, 2),
        'Close': round(close_price, 2),
        'High': round(high, 2),
        'Low': round(low, 2),
        'Return (%)': round(total_return, 2)
    }
    if len(data) > 2:
        volatility = data['Return'].std() * 100
        win_rate = (data['Return'] > 0).mean() * 100
        result['Volatility (%)'] = round(volatility, 2)
        result['Win Rate (%)'] = round(win_rate, 2)
    return result

def basic_stock_info(ticker: str) -> dict:
    """
    Fetch basic stock information for a single ticker.
    """
    return DataFetcher.basic_stock_info(ticker)

# ... other imports and functions remain unchanged ...
# ... other imports and functions remain unchanged ...

def get_stock_performance_metrics(ticker: str, start: datetime, end: datetime) -> dict:
    """
    Fetch performance metrics for a stock over a date range.
    """
    if start >= end:
        raise ValueError("Start date must be earlier than end date.")
    
    # Cap end date at today to avoid future dates
    end = min(end, datetime.now())
    
    logger.debug(f"Fetching performance metrics for {ticker} from {start} to {end}")
    
    # Fetch stock and benchmark data
    stock_data = DataFetcher.single_stock_data(ticker, start, end)
    benchmark_data = DataFetcher.benchmark_data('^GSPC', start, end)
    
    if stock_data.empty or benchmark_data.empty:
        raise ValueError(f"No data available for {ticker} or benchmark")
    
    # Convert to DataFrame with date as index
    stock_df = pd.DataFrame(stock_data).set_index('Date')
    benchmark_df = pd.DataFrame(benchmark_data).set_index('Date')
    
    logger.debug(f"Stock data columns: {stock_df.columns.tolist()}")
    logger.debug(f"Benchmark data columns: {benchmark_df.columns.tolist()}")
    
    # Verify 'Close' column exists
    if 'Close' not in stock_df.columns or 'Close' not in benchmark_df.columns:
        logger.error(f"Missing 'Close' column. Stock columns: {stock_df.columns.tolist()}, Benchmark columns: {benchmark_df.columns.tolist()}")
        raise KeyError("Close column missing in stock or benchmark data")
    
    # Calculate daily returns
    # stock_df['Return'] = stock_df['Close'].pct_change()
    # benchmark_df['Return'] = benchmark_df['Close'].pct_change()
    
    # # Rename columns before merging to ensure correct names
    # stock_df = stock_df[['Return']].rename(columns={'Return': 'Return_stock'})
    # benchmark_df = benchmark_df[['Return']].rename(columns={'Return': 'Return_benchmark'})
    
    # # Merge data for aligned dates
    # merged_df = pd.merge(
    #     stock_df,
    #     benchmark_df,
    #     left_index=True,
    #     right_index=True
    # ).dropna()
    stock_returns = stock_df['Close'].pct_change().rename('Return_stock')
    benchmark_returns = benchmark_df['Close'].pct_change().rename('Return_benchmark')
    merged_df = pd.concat([stock_returns, benchmark_returns], axis=1).dropna()
    
    logger.debug(f"Merged DataFrame columns: {merged_df.columns.tolist()}")
    logger.debug(f"Merged DataFrame shape: {merged_df.shape}")
    
    if merged_df.empty:
        raise ValueError(f"No overlapping data for {ticker} and benchmark")
    
    # Calculate metrics
    start_price = stock_df['Close'].iloc[0]
    end_price = stock_df['Close'].iloc[-1]
    returns = ((end_price - start_price) / start_price) * 100
    
    volatility = merged_df['Return_stock'].std() * np.sqrt(252) * 100  # Annualized
    win_rate = (merged_df['Return_stock'] > 0).mean() * 100
    
    # Max Drawdown
    rolling_max = stock_df['Close'].cummax()
    drawdowns = (stock_df['Close'] - rolling_max) / rolling_max
    max_drawdown = drawdowns.min() * 100
    
    # Alpha and Beta
    cov_matrix = merged_df[['Return_stock', 'Return_benchmark']].cov() * 252
    logger.debug(f"Covariance matrix:\n{cov_matrix}")
    beta = cov_matrix.loc['Return_stock', 'Return_benchmark'] / cov_matrix.loc['Return_benchmark', 'Return_benchmark']
    benchmark_return = ((benchmark_df['Close'].iloc[-1] - benchmark_df['Close'].iloc[0]) / 
                      benchmark_df['Close'].iloc[0]) * 100
    alpha = returns - (beta * benchmark_return)
    
    # Sharpe Ratio (assume 2% risk-free rate, annualized)
    risk_free_rate = 2.0
    excess_return = returns - risk_free_rate
    sharpe_ratio = excess_return / volatility if volatility != 0 else 0
    
    return {
        'returns': round(returns, 2),
        'alpha': round(alpha, 2),
        'beta': round(beta, 2),
        'sharpeRatio': round(sharpe_ratio, 2),
        'volatility': round(volatility, 2),
        'maxDrawdown': round(max_drawdown, 2),
        'winRate': round(win_rate, 2)
    }

def get_price_history(ticker: str, start: datetime, end: datetime) -> list:
    """
    Fetch historical closing prices for a stock.
    """
    if start >= end:
        raise ValueError("Start date must be earlier than end date.")
    end = min(end, datetime.now())  # Cap end date at today
    data = DataFetcher.single_stock_data(ticker, start, end)
    return [{'date': row['Date'], 'close': round(row['Close'], 2)} for _, row in data.iterrows()]

def get_volume_history(ticker: str, start: datetime, end: datetime) -> list:
    """
    Fetch historical volume data for a stock.
    """
    if start >= end:
        raise ValueError("Start date must be earlier than end date.")
    end = min(end, datetime.now())  # Cap end date at today
    data = DataFetcher.single_stock_data(ticker, start, end)
    return [{'date': row['Date'], 'volume': round(row['Volume'] / 1e6, 2)} for _, row in data.iterrows()]