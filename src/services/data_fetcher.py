from datetime import datetime
import yfinance as yf
import pandas as pd
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class DataFetcher:
    @staticmethod
    def single_stock_data(ticker: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """
        Fetch raw historical OHLCV data for a single stock within a date range.
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
            logger.debug(f"Fetched raw single stock data for {ticker}")
            return data
        except Exception as e:
            logger.error(f"Failed to fetch data for {ticker}: {str(e)}")
            raise ValueError(f"Failed to fetch data for {ticker}: {str(e)}")

    @staticmethod
    def multiple_stocks_data(tickers: list[str], start_date: str, end_date: str) -> pd.DataFrame:
        """
        Fetch raw historical closing prices for multiple stocks.
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
            logger.debug(f"Fetched raw multiple stocks data for {tickers}")
            return data
        except Exception as e:
            logger.error(f"Failed to fetch data for {tickers}: {str(e)}")
            raise ValueError(f"Failed to fetch data for {tickers}: {str(e)}")

    @staticmethod
    def stock_period_data(ticker: str, period: str = '1mo') -> pd.DataFrame:
        """
        Fetch raw historical OHLCV data for a single stock for a given period.
        """
        if not isinstance(ticker, str) or not ticker:
            raise ValueError("Ticker must be a non-empty string")
        if not isinstance(period, str) or period not in ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']:
            raise ValueError("Period must be a valid string (e.g., '1mo', '1y')")

        try:
            data = yf.download(ticker, period=period, interval='1d', progress=False)
            if data.empty:
                raise ValueError(f"No data available for {ticker} for period {period}")
            logger.debug(f"Fetched raw stock period data for {ticker}")
            return data
        except Exception as e:
            logger.error(f"Failed to fetch data for {ticker}: {str(e)}")
            raise ValueError(f"Failed to fetch data for {ticker}: {str(e)}")

    @staticmethod
    def benchmark_data(benchmark_ticker: str = '^GSPC', start_date: datetime = None, end_date: datetime = None) -> pd.DataFrame:
        """
        Fetch raw historical OHLCV data for a benchmark (e.g., S&P 500) within a date range.
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
            logger.debug(f"Fetched raw benchmark data for {benchmark_ticker}")
            return data
        except Exception as e:
            logger.error(f"Failed to fetch benchmark data for {benchmark_ticker}: {str(e)}")
            raise ValueError(f"Failed to fetch benchmark data for {benchmark_ticker}: {str(e)}")

    @staticmethod
    def basic_stock_info(ticker: str) -> dict:
        """
        Fetch raw stock information for a single ticker.
        """
        if not isinstance(ticker, str) or not ticker:
            raise ValueError("Ticker must be a non-empty string")

        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            history = stock.history(period="5d")
            if history.empty:
                raise ValueError(f"No historical data available for {ticker}")
            logger.debug(f"Fetched raw stock info for {ticker}")
            return {"info": info, "history": history}
        except Exception as e:
            logger.error(f"Failed to fetch stock info for {ticker}: {str(e)}")
            raise ValueError(f"Failed to fetch stock info for {ticker}: {str(e)}")