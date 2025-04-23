from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from .data_fetcher import DataFetcher
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Mock lists of tickers for NIFTY and SENSEX (replace with actual data source in production)
NIFTY_TICKERS = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "HINDUNILVR.NS",
    "ICICIBANK.NS", "KOTAKBANK.NS", "SBIN.NS", "BAJFINANCE.NS", "BHARTIARTL.NS",
    "ASIANPAINT.NS", "ITC.NS", "AXISBANK.NS", "LT.NS", "MARUTI.NS"
]
SENSEX_TICKERS = [
    "RELIANCE.BO", "HDFCBANK.BO", "INFY.BO", "ICICIBANK.BO", "TCS.BO",
    "HINDUNILVR.BO", "KOTAKBANK.BO", "SBIN.BO", "BAJFINANCE.BO", "BHARTIARTL.BO",
    "ASIANPAINT.BO", "ITC.BO", "AXISBANK.BO", "LT.BO", "MARUTI.BO"
]

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
    
    end = min(end, datetime.now())  # Cap end date to today
    
    logger.debug(f"Fetching performance metrics for {ticker} from {start} to {end}")
    
    # Fetch raw data
    raw_stock_data = DataFetcher.single_stock_data(ticker, start, end)
    raw_benchmark_data = DataFetcher.benchmark_data('^GSPC', start, end)
    
    # Process and clean
    stock_data = _process_stock_data(raw_stock_data, ticker)
    benchmark_data = _process_stock_data(raw_benchmark_data, '^GSPC')
    
    if stock_data.empty or benchmark_data.empty:
        raise ValueError(f"No data available for {ticker} or benchmark")

    # Convert to DataFrame
    stock_df = pd.DataFrame(stock_data)
    benchmark_df = pd.DataFrame(benchmark_data)

    # Normalize 'Date' to remove time & tz
    stock_df['Date'] = pd.to_datetime(stock_df['Date']).dt.date
    benchmark_df['Date'] = pd.to_datetime(benchmark_df['Date']).dt.date

    # Set index
    stock_df = stock_df.set_index('Date')
    benchmark_df = benchmark_df.set_index('Date')

    # Drop duplicate columns
    stock_df = stock_df.loc[:, ~stock_df.columns.duplicated()]
    benchmark_df = benchmark_df.loc[:, ~benchmark_df.columns.duplicated()]

    logger.debug(f"Stock data columns after dedup: {stock_df.columns.tolist()}")
    logger.debug(f"Benchmark data columns after dedup: {benchmark_df.columns.tolist()}")

    if 'Close' not in stock_df.columns or 'Close' not in benchmark_df.columns:
        logger.error(f"Missing 'Close' column. Stock columns: {stock_df.columns.tolist()}, Benchmark columns: {benchmark_df.columns.tolist()}")
        raise KeyError("Close column missing in stock or benchmark data")

    # Compute returns
    stock_returns = stock_df['Close'].pct_change(fill_method=None).rename('Return_stock')
    benchmark_returns = benchmark_df['Close'].pct_change(fill_method=None).rename('Return_benchmark')
    merged_df = pd.concat([stock_returns, benchmark_returns], axis=1).dropna()

    logger.debug(f"Merged DataFrame columns: {merged_df.columns.tolist()}")
    logger.debug(f"Merged DataFrame shape: {merged_df.shape}")

    if merged_df.empty:
        raise ValueError(f"No overlapping data for {ticker} and benchmark")

    # Metrics calculation
    start_price = stock_df['Close'].iloc[0]
    end_price = stock_df['Close'].iloc[-1]
    returns = ((end_price - start_price) / start_price) * 100

    volatility = merged_df['Return_stock'].std() * np.sqrt(252) * 100
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

# New Added
def compare_stocks(stock1: str, stock2: str) -> dict:
    """
    Compare two stocks over the last 12 months, returning key metrics and price history.
    """
    if not stock1 or not stock2:
        raise ValueError("Both stock tickers must be non-empty strings")
    if stock1 == stock2:
        raise ValueError("Cannot compare the same stock")

    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)  # Last 12 months

    try:
        # Fetch performance metrics
        metrics1 = get_stock_performance_metrics(stock1, start_date, end_date)
        metrics2 = get_stock_performance_metrics(stock2, start_date, end_date)

        # Fetch basic info for P/E ratio and market cap
        info1 = basic_stock_info(stock1)
        info2 = basic_stock_info(stock2)

        # Fetch price history for charts
        price_history1 = get_price_history(stock1, start_date, end_date)
        price_history2 = get_price_history(stock2, start_date, end_date)

        return {
            "stock1": {
                "ticker": stock1,
                "metrics": {
                    "returns": float(metrics1["returns"]),  # Convert np.float64 to float
                    "volatility": float(metrics1["volatility"]),  # Convert np.float64 to float
                    "peRatio": info1["peRatio"] if info1["peRatio"] != "N/A" else 0,
                    "marketCap": info1["marketCap"] / 1000 if info1["marketCap"] != "N/A" else 0,  # Convert to trillions
                },
            },
            "stock2": {
                "ticker": stock2,
                "metrics": {
                    "returns": float(metrics2["returns"]),  # Convert np.float64 to float
                    "volatility": float(metrics2["volatility"]),  # Convert np.float64 to float
                    "peRatio": info2["peRatio"] if info2["peRatio"] != "N/A" else 0,
                    "marketCap": info2["marketCap"] / 1000 if info2["marketCap"] != "N/A" else 0,  # Convert to trillions
                },
            },
            "priceHistory": {
                "stock1": price_history1,
                "stock2": price_history2,
            },
        }
    except Exception as e:
        logger.error(f"Error comparing stocks {stock1} and {stock2}: {str(e)}")
        raise ValueError(f"Failed to compare stocks: {str(e)}")
    
def get_stock_ohlc(ticker: str, start: datetime, end: datetime) -> list:
    """
    Fetch and process OHLC data for candlestick charts.
    """
    if start >= end:
        raise ValueError("Start date must be earlier than end date.")
    end = min(end, datetime.now())  # Cap end date at today
    
    raw_data = DataFetcher.single_stock_data(ticker, start, end)
    data = _process_stock_data(raw_data, ticker)
    
    return [{
        'date': row['Date'],
        'open': round(row['Open'], 2),
        'high': round(row['High'], 2),
        'low': round(row['Low'], 2),
        'close': round(row['Close'], 2)
    } for _, row in data.iterrows()]
    
def get_top_performers(index: str) -> list:
    """
    Fetch top 10 performing stocks for the specified index over the last 12 months.
    """
    if index not in ["NIFTY", "SENSEX"]:
        raise ValueError("Index must be either NIFTY or SENSEX")
    
    tickers = NIFTY_TICKERS if index == "NIFTY" else SENSEX_TICKERS
    performers = []
    
    for ticker in tickers:
        try:
            # Fetch performance over the last 12 months
            perf = fixed_period_performance(ticker, "1y")
            if "error" not in perf:
                info = basic_stock_info(ticker)
                performers.append({
                    "symbol": ticker.split('.')[0],  # Remove .NS or .BO suffix
                    "name": info["name"],
                    "change": perf["Close"] - perf["Open"],
                    "changePercent": perf["Return (%)"]
                })
        except Exception as e:
            logger.warning(f"Skipping {ticker} due to error: {str(e)}")
            continue
    
    # Sort by changePercent in descending order and take top 10
    performers.sort(key=lambda x: x["changePercent"], reverse=True)
    return performers[:10]