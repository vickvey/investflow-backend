from datetime import datetime
import pandas as pd
import numpy as np
from .data_fetcher import DataFetcher
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def _process_stock_data(data: pd.DataFrame, ticker: str) -> pd.DataFrame:
    """
    Process raw stock data to ensure consistent format.
    """
    if data.empty:
        raise ValueError(f"No data available for {ticker}")
    
    # Handle MultiIndex columns safely
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = [col[0].title() for col in data.columns]
    else:
        data.columns = [col.title() for col in data.columns]
    
    # Validate required columns
    required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    missing_columns = [col for col in required_columns if col not in data.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns for {ticker}: {missing_columns}")
    
    data = data.reset_index()
    if 'Date' not in data.columns:
        raise ValueError("Date column missing from fetched data")
    
    data['Date'] = data['Date'].astype(str)
    logger.debug(f"Processed data columns for {ticker}: {data.columns.tolist()}")
    return data

def single_stock(ticker: str, start: datetime, end: datetime) -> dict:
    """
    Fetch and process historical data for a single stock.
    """
    if start >= end:
        raise ValueError("Start date must be earlier than end date.")
    raw_data = DataFetcher.single_stock_data(ticker, start, end)
    data = _process_stock_data(raw_data, ticker)
    return {
        "ticker": ticker,
        "data": data.to_dict(orient="records")
    }

def multiple_stocks(tickers: list[str], start: datetime, end: datetime) -> list:
    """
    Fetch and process historical closing prices for multiple stocks.
    """
    if start >= end:
        raise ValueError("Start date must be earlier than end date.")
    raw_data = DataFetcher.multiple_stocks_data(tickers, start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'))
    if raw_data.empty:
        raise ValueError(f"No data available for {tickers}")
    
    # Handle MultiIndex for multiple tickers
    if isinstance(raw_data.columns, pd.MultiIndex):
        raw_data.columns = [col[1] for col in raw_data.columns]
    
    logger.debug(f"Processed multiple stocks data columns: {raw_data.columns.tolist()}")
    return raw_data.to_dict(orient="records")

def today_performance(ticker: str) -> dict:
    """
    Fetch and process today's performance metrics for a stock.
    """
    raw_data = DataFetcher.stock_period_data(ticker, period='5d')
    if raw_data.empty:
        raise ValueError(f"No data available for {ticker} for period 5d")
    
    # Process raw data
    if isinstance(raw_data.columns, pd.MultiIndex):
        raw_data.columns = [col[0].title() for col in raw_data.columns]
    else:
        raw_data.columns = [col.title() for col in raw_data.columns]
    
    required_columns = ['Open', 'High', 'Low', 'Close']
    missing_columns = [col for col in required_columns if col not in raw_data.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns for {ticker}: {missing_columns}")

    today_str = datetime.today().strftime('%Y-%m-%d')
    if today_str in raw_data.index.strftime('%Y-%m-%d'):
        todays_data = raw_data.loc[raw_data.index.strftime('%Y-%m-%d') == today_str].iloc[0]
    else:
        todays_data = raw_data.iloc[-1]
        today_str = todays_data.name.strftime('%Y-%m-%d')

    open_price = todays_data['Open']
    close_price = todays_data['Close']
    daily_return = ((close_price - open_price) / open_price) * 100 if open_price != 0 else 0

    return {
        'Date': today_str,
        'Open': round(float(open_price), 2),
        'High': round(float(todays_data['High']), 2),
        'Low': round(float(todays_data['Low']), 2),
        'Close': round(float(close_price), 2),
        'Return (%)': round(float(daily_return), 2)
    }

def fixed_period_performance(ticker: str, period: str) -> dict:
    """
    Fetch and process performance metrics for a stock over a fixed period.
    """
    raw_data = DataFetcher.stock_period_data(ticker, period)
    data = _process_stock_data(raw_data, ticker)
    
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
    Fetch and process basic stock information for a single ticker.
    """
    raw_data = DataFetcher.basic_stock_info(ticker)
    info = raw_data['info']
    history = raw_data['history']
    
    if history.empty:
        raise ValueError(f"No historical data available for {ticker}")
    
    # Process history data
    history.columns = [col.title() for col in history.columns]
    required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    missing_columns = [col for col in required_columns if col not in history.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns for {ticker}: {missing_columns}")

    latest_data = history.iloc[-1]
    prev_data = history.iloc[-2] if len(history) > 1 else latest_data

    close_price = float(latest_data['Close'])
    prev_close = float(prev_data['Close'])
    change = close_price - prev_close
    change_percent = (change / prev_close) * 100 if prev_close != 0 else 0

    return {
        'ticker': ticker,
        'name': info.get('longName', 'Unknown'),
        'price': round(close_price, 2),
        'change': round(change, 2),
        'changePercent': round(change_percent, 2),
        'marketCap': info.get('marketCap', 0) / 1e9 if info.get('marketCap') else 'N/A',
        'peRatio': round(info.get('trailingPE', 0), 2) if info.get('trailingPE') else 'N/A',
        'dividend': round(info.get('dividendYield', 0) * 100, 2) if info.get('dividendYield') else 0,
        'volume': round(float(latest_data['Volume']) / 1e6, 2),
        'avgVolume': round(info.get('averageVolume', 0) / 1e6, 2) if info.get('averageVolume') else 'N/A',
        'high': round(float(latest_data['High']), 2),
        'low': round(float(latest_data['Low']), 2),
        'open': round(float(latest_data['Open']), 2),
        'prevClose': round(prev_close, 2)
    }

def get_stock_performance_metrics(ticker: str, start: datetime, end: datetime) -> dict:
    """
    Fetch and process performance metrics for a stock over a date range.
    """
    if start >= end:
        raise ValueError("Start date must be earlier than end date.")
    
    # Cap end date at today to avoid future dates
    end = min(end, datetime.now())
    
    logger.debug(f"Fetching performance metrics for {ticker} from {start} to {end}")
    
    # Fetch and process stock and benchmark data
    raw_stock_data = DataFetcher.single_stock_data(ticker, start, end)
    raw_benchmark_data = DataFetcher.benchmark_data('^GSPC', start, end)
    
    stock_data = _process_stock_data(raw_stock_data, ticker)
    benchmark_data = _process_stock_data(raw_benchmark_data, '^GSPC')
    
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
    Fetch and process historical closing prices for a stock.
    """
    if start >= end:
        raise ValueError("Start date must be earlier than end date.")
    end = min(end, datetime.now())  # Cap end date at today
    raw_data = DataFetcher.single_stock_data(ticker, start, end)
    data = _process_stock_data(raw_data, ticker)
    return [{'date': row['Date'], 'close': round(row['Close'], 2)} for _, row in data.iterrows()]

def get_volume_history(ticker: str, start: datetime, end: datetime) -> list:
    """
    Fetch and process historical volume data for a stock.
    """
    if start >= end:
        raise ValueError("Start date must be earlier than end date.")
    end = min(end, datetime.now())  # Cap end date at today
    raw_data = DataFetcher.single_stock_data(ticker, start, end)
    data = _process_stock_data(raw_data, ticker)
    return [{'date': row['Date'], 'volume': round(row['Volume'] / 1e6, 2)} for _, row in data.iterrows()]