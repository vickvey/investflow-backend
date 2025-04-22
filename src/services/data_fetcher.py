from datetime import datetime
import yfinance as yf
import pandas as pd
import numpy as np
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class DataFetcher:
    @staticmethod
    def single_stock_data(ticker: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """
        Fetch historical OHLCV data for a single stock within a date range.
        """
        if not isinstance(ticker, str) or not ticker:
            raise ValueError("Ticker must be a non-empty string")
        if not isinstance(start_date, datetime) or not isinstance(end_date, datetime):
            raise ValueError("Start and end dates must be datetime objects")
        if start_date >= end_date:
            raise ValueError("Start date must be earlier than end date")

        try:
            data = yf.download(ticker, start=start_date, end=end_date, progress=False)
            if data.empty:
                raise ValueError(f"No data available for {ticker} between {start_date} and {end_date}")
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
            logger.debug(f"Processed single stock data columns for {ticker}: {data.columns.tolist()}")
            return data
        except Exception as e:
            logger.error(f"Failed to fetch data for {ticker}: {str(e)}")
            raise ValueError(f"Failed to fetch data for {ticker}: {str(e)}")

    @staticmethod
    def multiple_stocks_data(tickers: list[str], start_date: str, end_date: str) -> pd.DataFrame:
        """
        Fetch historical closing prices for multiple stocks.
        """
        if not isinstance(tickers, list) or not tickers:
            raise ValueError("Tickers must be a non-empty list")
        if not all(isinstance(t, str) for t in tickers):
            raise ValueError("All tickers must be strings")
        if not isinstance(start_date, str) or not isinstance(end_date, str):
            raise ValueError("Start and end dates must be strings in YYYY-MM-DD format")
        
        try:
            pd.to_datetime(start_date)  # Validate date format
            pd.to_datetime(end_date)
            if pd.to_datetime(start_date) >= pd.to_datetime(end_date):
                raise ValueError("Start date must be earlier than end date")
        except ValueError as e:
            raise ValueError(f"Invalid date format: {str(e)}")

        try:
            data = yf.download(tickers, start=start_date, end=end_date, progress=False)['Close']
            if data.empty:
                raise ValueError(f"No data available for {tickers} between {start_date} and {end_date}")
            # Handle MultiIndex for multiple tickers
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = [col[1] for col in data.columns]
            logger.debug(f"Multiple stocks data columns: {data.columns.tolist()}")
            return data
        except Exception as e:
            logger.error(f"Failed to fetch data for {tickers}: {str(e)}")
            raise ValueError(f"Failed to fetch data for {tickers}: {str(e)}")

    @staticmethod
    def stock_period_data(ticker: str, period: str = '1mo') -> pd.DataFrame:
        """
        Fetch historical OHLCV data for a single stock for a given period.
        """
        if not isinstance(ticker, str) or not ticker:
            raise ValueError("Ticker must be a non-empty string")
        if not isinstance(period, str) or period not in ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']:
            raise ValueError("Period must be a valid string (e.g., '1mo', '1y')")

        try:
            data = yf.download(ticker, period=period, interval='1d', progress=False)
            if data.empty:
                raise ValueError(f"No data available for {ticker} for period {period}")
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
            logger.debug(f"Stock period data columns for {ticker}: {data.columns.tolist()}")
            return data
        except Exception as e:
            logger.error(f"Failed to fetch data for {ticker}: {str(e)}")
            raise ValueError(f"Failed to fetch data for {ticker}: {str(e)}")

    @staticmethod
    def today_performance(ticker: str, period: str = '5d') -> dict:
        """
        Fetch today's performance metrics for a stock.
        """
        if not isinstance(ticker, str) or not ticker:
            raise ValueError("Ticker must be a non-empty string")
        if not isinstance(period, str) or period not in ['1d', '5d', '1mo', '3mo', '6mo', '1y']:
            raise ValueError("Period must be a valid string (e.g., '5d', '1mo')")

        try:
            data = yf.download(ticker, period=period, interval='1d', progress=False)
            if data.empty:
                raise ValueError(f"No data available for {ticker} for period {period}")
            # Handle MultiIndex columns safely
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = [col[0].title() for col in data.columns]
            else:
                data.columns = [col.title() for col in data.columns]
            # Validate required columns
            required_columns = ['Open', 'High', 'Low', 'Close']
            missing_columns = [col for col in required_columns if col not in data.columns]
            if missing_columns:
                raise ValueError(f"Missing required columns for {ticker}: {missing_columns}")

            today_str = datetime.today().strftime('%Y-%m-%d')
            if today_str in data.index.strftime('%Y-%m-%d'):
                todays_data = data.loc[data.index.strftime('%Y-%m-%d') == today_str].iloc[0]
            else:
                todays_data = data.iloc[-1]
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
        except Exception as e:
            logger.error(f"Failed to fetch today's performance for {ticker}: {str(e)}")
            raise ValueError(f"Failed to fetch today's performance for {ticker}: {str(e)}")

    @staticmethod
    def basic_stock_info(ticker: str) -> dict:
        """
        Fetch basic stock information for a single ticker.
        """
        if not isinstance(ticker, str) or not ticker:
            raise ValueError("Ticker must be a non-empty string")

        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            history = stock.history(period="5d")

            if history.empty:
                raise ValueError(f"No historical data available for {ticker}")
            # Handle columns safely (history typically returns simple Index, not MultiIndex)
            history.columns = [col.title() for col in history.columns]
            # Validate required columns
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
        except Exception as e:
            logger.error(f"Failed to fetch stock info for {ticker}: {str(e)}")
            raise ValueError(f"Failed to fetch stock info for {ticker}: {str(e)}")

    @staticmethod
    def benchmark_data(benchmark_ticker: str = '^GSPC', start_date: datetime = None, end_date: datetime = None) -> pd.DataFrame:
        """
        Fetch historical OHLCV data for a benchmark (e.g., S&P 500) within a date range.
        """
        if not isinstance(benchmark_ticker, str) or not benchmark_ticker:
            raise ValueError("Benchmark ticker must be a non-empty string")
        if start_date and not isinstance(start_date, datetime):
            raise ValueError("Start date must be a datetime object")
        if end_date and not isinstance(end_date, datetime):
            raise ValueError("End date must be a datetime object")
        if start_date and end_date and start_date >= end_date:
            raise ValueError("Start date must be earlier than end date")

        try:
            data = yf.download(benchmark_ticker, start=start_date, end=end_date, progress=False)
            if data.empty:
                raise ValueError(f"No data available for benchmark {benchmark_ticker}")
            # Handle MultiIndex columns safely
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = [col[0].title() for col in data.columns]
            else:
                data.columns = [col.title() for col in data.columns]
            # Validate required columns
            required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            missing_columns = [col for col in required_columns if col not in data.columns]
            if missing_columns:
                raise ValueError(f"Missing required columns for {benchmark_ticker}: {missing_columns}")
            data = data.reset_index()
            if 'Date' not in data.columns:
                raise ValueError("Date column missing from benchmark data")
            data['Date'] = data['Date'].astype(str)
            logger.debug(f"Processed benchmark data columns for {benchmark_ticker}: {data.columns.tolist()}")
            return data
        except Exception as e:
            logger.error(f"Failed to fetch benchmark data for {benchmark_ticker}: {str(e)}")
            raise ValueError(f"Failed to fetch benchmark data for {benchmark_ticker}: {str(e)}")