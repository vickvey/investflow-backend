# import yfinance as yf
# from datetime import datetime,timedelta

# class DataFetcher:
#     @staticmethod
#     def single_stock_data(ticker='ADRO.JK', start_date=datetime.now() - timedelta(days=365), end_date=datetime.now()):
#         try:
#             # Download the data
#             data = yf.download(ticker, start=start_date, end=end_date, progress=False)
            
#             # Reset index to move Date from index to a column
#             data = data.reset_index()

#             # Convert the 'Date' column to a string for serialization
#             data['Date'] = data['Date'].astype(str)

#             return data
#         except Exception as e:
#             raise ValueError(f"Failed to fetch data: {e}")
        
#     @staticmethod
#     def multiple_stocks_data(tickers, start_date="2021-05-12", end_date="2022-05-12"):
    
#         try:
#             data = yf.download(tickers, start=start_date, end=end_date, progress=False)['Close']
#             # return data.dropna()
#             return data
#         except Exception as e:
#             raise ValueError(f"Failed to fetch data: {e}")
# # Usage
# # data = DataFetcher.single_stock_data()

#     @staticmethod
#     def stock_period_data(ticker,period = '1mo'):
#         """
#         Fetch historical OHLCV data for a single stock for a given period.

#         Args:
#             ticker (str): e.g. 'AAPL'
#             period (str): e.g. '1mo', '3mo', '6mo', etc.

#         Returns:
#             pd.DataFrame: Daily stock data
#         """
#         try:
#             data = yf.download(ticker, period=period, interval='1d', progress=False)
#             return data
#         except Exception as e:
#             raise ValueError(f"Failed to fetch data: {e}")


#     @staticmethod
#     def today_performance(ticker,period='5d'):
#         # show users selected or invested stocker performance for today
#         # give returns and open, close, high and low for today
#         # data = DataFetcher.single_stock_data(tickers, )

#         data = yf.download(ticker, period, interval='1d', progress=False)

#         # Check if data is available
#         if data.empty:
#             return f"No data available for {ticker}."

#         # Get today's date in the format matching the DataFrame index
#         today_str = datetime.today().strftime('%Y-%m-%d')

#         # Attempt to extract today's data
#         if today_str in data.index.strftime('%Y-%m-%d'):
#             todays_data = data.loc[data.index.strftime('%Y-%m-%d') == today_str].iloc[0]
#         else:
#             # If today's data isn't available, use the most recent available data
#             todays_data = data.iloc[-1]
#             today_str = todays_data.name.strftime('%Y-%m-%d')

#         # Calculate return
#         open_price = todays_data['Open']
#         close_price = todays_data['Close']
#         daily_return = ((close_price - open_price) / open_price) * 100

#         return {
#             'Date': today_str,
#             'Open': open_price,
#             'High': todays_data['High'],
#             'Low': todays_data['Low'],
#             'Close': close_price,
#             'Return (%)': round(daily_return, 2)
#         }


# """
#     Fetch historical adjusted close prices from Yahoo Finance.
    
#     Parameters:
#     - tickers: list of str, stock tickers (e.g., ['ADRO.JK', 'ASII.JK']).
#     - start_date: str, start date in YYYY-MM-DD format.
#     - end_date: str, end date in YYYY-MM-DD format.
    
#     Returns:
#     - pandas DataFrame with dates as index and tickers as columns.
# """


# # def generate_synthetic_data(tickers, start_date="2021-05-12", end_date="2022-05-12", base_price=100, volatility=0.01):
# #     """
# #     Generate synthetic price data for testing.
    
# #     Parameters:
# #     - tickers: list of str, stock tickers.
# #     - start_date: str, start date.
# #     - end_date: str, end date.
# #     - base_price: float, starting price for all stocks.
# #     - volatility: float, standard deviation of daily returns.
    
# #     Returns:
# #     - pandas DataFrame with dates as index and tickers as columns.
# #     """
# #     dates = pd.date_range(start=start_date, end=end_date, freq="B")
# #     prices = pd.DataFrame(
# #         np.random.randn(len(dates), len(tickers)) * volatility + base_price,
# #         index=dates,
# #         columns=tickers
# #     ).cumsum()
# #     return prices


from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd

class DataFetcher:
    @staticmethod
    def single_stock_data(ticker: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """
        Fetch historical OHLCV data for a single stock within a date range.
        """
        try:
            data = yf.download(ticker, start=start_date, end=end_date, progress=False)
            if data.empty:
                raise ValueError(f"No data available for {ticker}")
            data = data.reset_index()
            data['Date'] = data['Date'].astype(str)
            return data
        except Exception as e:
            raise ValueError(f"Failed to fetch data for {ticker}: {str(e)}")

    @staticmethod
    def multiple_stocks_data(tickers: list[str], start_date: str, end_date: str) -> pd.DataFrame:
        """
        Fetch historical closing prices for multiple stocks.
        """
        try:
            data = yf.download(tickers, start=start_date, end=end_date, progress=False)['Close']
            if data.empty:
                raise ValueError(f"No data available for {tickers}")
            return data
        except Exception as e:
            raise ValueError(f"Failed to fetch data: {str(e)}")

    @staticmethod
    def stock_period_data(ticker: str, period: str = '1mo') -> pd.DataFrame:
        """
        Fetch historical OHLCV data for a single stock for a given period.
        """
        try:
            data = yf.download(ticker, period=period, interval='1d', progress=False)
            if data.empty:
                raise ValueError(f"No data available for {ticker}")
            return data
        except Exception as e:
            raise ValueError(f"Failed to fetch data for {ticker}: {str(e)}")

    @staticmethod
    def today_performance(ticker: str, period: str = '5d') -> dict:
        """
        Fetch today's performance metrics for a stock.
        """
        try:
            data = yf.download(ticker, period=period, interval='1d', progress=False)
            if data.empty:
                raise ValueError(f"No data available for {ticker}")

            today_str = datetime.today().strftime('%Y-%m-%d')
            if today_str in data.index.strftime('%Y-%m-%d'):
                todays_data = data.loc[data.index.strftime('%Y-%m-%d') == today_str].iloc[0]
            else:
                todays_data = data.iloc[-1]
                today_str = todays_data.name.strftime('%Y-%m-%d')

            open_price = todays_data['Open']
            close_price = todays_data['Close']
            daily_return = ((close_price - open_price) / open_price) * 100

            return {
                'Date': today_str,
                'Open': round(open_price, 2),
                'High': round(todays_data['High'], 2),
                'Low': round(todays_data['Low'], 2),
                'Close': round(close_price, 2),
                'Return (%)': round(daily_return, 2)
            }
        except Exception as e:
            raise ValueError(f"Failed to fetch today's performance for {ticker}: {str(e)}")

    @staticmethod
    def basic_stock_info(ticker: str) -> dict:
        """
        Fetch basic stock information for a single ticker.
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            history = stock.history(period="5d")

            if history.empty:
                raise ValueError(f"No historical data available for {ticker}")

            latest_data = history.iloc[-1]
            prev_data = history.iloc[-2] if len(history) > 1 else latest_data

            # Calculate change and change percent
            close_price = latest_data['Close']
            prev_close = prev_data['Close']
            change = close_price - prev_close
            change_percent = (change / prev_close) * 100 if prev_close != 0 else 0

            return {
                'ticker': ticker,
                'name': info.get('longName', 'Unknown'),
                'price': round(close_price, 2),
                'change': round(change, 2),
                'changePercent': round(change_percent, 2),
                'marketCap': info.get('marketCap', 0) / 1e9 if info.get('marketCap') else 'N/A',  # In billions
                'peRatio': round(info.get('trailingPE', 0), 2) if info.get('trailingPE') else 'N/A',
                'dividend': round(info.get('dividendYield', 0) * 100, 2) if info.get('dividendYield') else 0,
                'volume': round(latest_data['Volume'] / 1e6, 2),  # In millions
                'avgVolume': round(info.get('averageVolume', 0) / 1e6, 2) if info.get('averageVolume') else 'N/A',
                'high': round(latest_data['High'], 2),
                'low': round(latest_data['Low'], 2),
                'open': round(latest_data['Open'], 2),
                'prevClose': round(prev_close, 2)
            }
        except Exception as e:
            raise ValueError(f"Failed to fetch stock info for {ticker}: {str(e)}")