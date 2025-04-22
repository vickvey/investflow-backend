import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime,timedelta

class DataFetcher:
    @staticmethod
    def single_stock_data(ticker='ADRO.JK', start_date=datetime.now() - timedelta(days=365), end_date=datetime.now()):
        try:
            # Download the data
            data = yf.download(ticker, start=start_date, end=end_date, progress=False)
            
            # Reset index to move Date from index to a column
            data = data.reset_index()

            # Convert the 'Date' column to a string for serialization
            data['Date'] = data['Date'].astype(str)

            return data
        except Exception as e:
            raise ValueError(f"Failed to fetch data: {e}")
        
    @staticmethod
    def multiple_stocks_data(tickers, start_date="2021-05-12", end_date="2022-05-12"):
    
        try:
            data = yf.download(tickers, start=start_date, end=end_date, progress=False)['Close']
            # return data.dropna()
            return data
        except Exception as e:
            raise ValueError(f"Failed to fetch data: {e}")
# Usage
# data = DataFetcher.single_stock_data()

    @staticmethod
    def stock_period_data(ticker,period = '1mo'):
        """
        Fetch historical OHLCV data for a single stock for a given period.

        Args:
            ticker (str): e.g. 'AAPL'
            period (str): e.g. '1mo', '3mo', '6mo', etc.

        Returns:
            pd.DataFrame: Daily stock data
        """
        try:
            data = yf.download(ticker, period=period, interval='1d', progress=False)
            return data
        except Exception as e:
            raise ValueError(f"Failed to fetch data: {e}")


    @staticmethod
    def today_performance(ticker,period='5d'):
        # show users selected or invested stocker performance for today
        # give returns and open, close, high and low for today
        # data = DataFetcher.single_stock_data(tickers, )

        data = yf.download(ticker, period, interval='1d', progress=False)

        # Check if data is available
        if data.empty:
            return f"No data available for {ticker}."

        # Get today's date in the format matching the DataFrame index
        today_str = datetime.today().strftime('%Y-%m-%d')

        # Attempt to extract today's data
        if today_str in data.index.strftime('%Y-%m-%d'):
            todays_data = data.loc[data.index.strftime('%Y-%m-%d') == today_str].iloc[0]
        else:
            # If today's data isn't available, use the most recent available data
            todays_data = data.iloc[-1]
            today_str = todays_data.name.strftime('%Y-%m-%d')

        # Calculate return
        open_price = todays_data['Open']
        close_price = todays_data['Close']
        daily_return = ((close_price - open_price) / open_price) * 100

        return {
            'Date': today_str,
            'Open': open_price,
            'High': todays_data['High'],
            'Low': todays_data['Low'],
            'Close': close_price,
            'Return (%)': round(daily_return, 2)
        }


"""
    Fetch historical adjusted close prices from Yahoo Finance.
    
    Parameters:
    - tickers: list of str, stock tickers (e.g., ['ADRO.JK', 'ASII.JK']).
    - start_date: str, start date in YYYY-MM-DD format.
    - end_date: str, end date in YYYY-MM-DD format.
    
    Returns:
    - pandas DataFrame with dates as index and tickers as columns.
"""


# def generate_synthetic_data(tickers, start_date="2021-05-12", end_date="2022-05-12", base_price=100, volatility=0.01):
#     """
#     Generate synthetic price data for testing.
    
#     Parameters:
#     - tickers: list of str, stock tickers.
#     - start_date: str, start date.
#     - end_date: str, end date.
#     - base_price: float, starting price for all stocks.
#     - volatility: float, standard deviation of daily returns.
    
#     Returns:
#     - pandas DataFrame with dates as index and tickers as columns.
#     """
#     dates = pd.date_range(start=start_date, end=end_date, freq="B")
#     prices = pd.DataFrame(
#         np.random.randn(len(dates), len(tickers)) * volatility + base_price,
#         index=dates,
#         columns=tickers
#     ).cumsum()
#     return prices