from datetime import datetime
import pandas as pd
from .data_fetcher import DataFetcher

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

def multiple_stocks(tickers: list[str], start: datetime, end: datetime) -> pd.DataFrame:
    """
    Fetch historical closing prices for multiple stocks.
    """
    if start >= end:
        raise ValueError("Start date must be earlier than end date.")

    data = DataFetcher.multiple_stocks_data(tickers, start=start.strftime('%Y-%m-%d'), end=end.strftime('%Y-%m-%d'))
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


# from .data_fetcher import DataFetcher
# from datetime import datetime
# import yfinance as yf

# #ticker for plural and ticker for singular


# def single_stock(ticker: str, start: datetime, end: datetime):
#     if start >= end:
#         raise ValueError("Start date must be earlier than end date.")
    
#     data = DataFetcher.single_stock_data(ticker, start, end)

#     # Reset index to make date column explicit (if index is datetime)
#     data = data.reset_index()
    
#     # Check for missing or problematic data
#     print(data.head())

#     return {
#         "ticker": ticker,
#         "data": data.to_dict(orient="records")  # Try this again to see if the issue resolves
#     }

# def multiple_stock(tickers, start:datetime, end:datetime):
#     if start >= end:
#         raise ValueError("Start date must be earlier than end date.")
#     else:
#         data = DataFetcher.multiple_stocks_data(tickers, start, end)
#         return data

# def today_performance(ticker):
#     return DataFetcher.today_performance(ticker)


# def fixed_period_performance(ticker: str, period: str):
#     data = DataFetcher.stock_period_data(ticker, period)

#     if data.empty:
#         return {"error": f"No data available for {ticker} in period {period}"}

#     # Compute metrics
#     data['Return'] = data['Close'].pct_change()
#     open_price = data['Open'].iloc[0]
#     close_price = data['Close'].iloc[-1]
#     high = data['High'].max()
#     low = data['Low'].min()
#     total_return = ((close_price - open_price) / open_price) * 100

#     result = {
#         'Ticker': ticker,
#         'Period': period,
#         'Open': round(open_price, 2),
#         'Close': round(close_price, 2),
#         'High': round(high, 2),
#         'Low': round(low, 2),
#         'Return (%)': round(total_return, 2)
#     }

#     # Only calculate volatility/win rate if we have enough data
#     if len(data) > 2:
#         volatility = data['Return'].std() * 100
#         win_rate = (data['Return'] > 0).mean() * 100
#         result['Volatility (%)'] = round(volatility, 2)
#         result['Win Rate (%)'] = round(win_rate, 2)

#     return result


# # def main():
# #     print(fixed_period_performance("AAPL", "1mo"))
# # main()

# def top_performer():
#     #shows nifty 50 top performers.
#     pass


# """
# 1. get_basic_stock_info(ticker)

# Returns:

#     Latest Close, Open, Volume

#     High, Low, Previous Close

#     Computed: Daily % change ((Close - Prev Close) / Prev Close)

# 2. get_stock_performance_metrics(ticker, start, end)

# Returns:

#     Returns ((EndPrice - StartPrice)/StartPrice)

#     Volatility (std deviation of returns)

#     Max Drawdown

#     Sharpe Ratio (assume risk-free rate = 0.02 if needed)

#     Win Rate (days with positive return / total days)

# 3. compare_stocks(ticker1, ticker2, start, end)

# Returns:

#     Comparative Returns

#     Volatility

#     P/E Ratio (skip if not in data)

#     Market Cap (skip if not in data)

# 4. get_price_history(ticker, start, end)

# Returns:

#     Time series of Close prices

#     Useful for plotting in frontend

# 5. get_volume_history(ticker, start, end)

# Returns:

#     Time series of Volume

# 6. get_top_performers(tickers, start, end, N=10)

# Returns:

#     Top N stocks with highest returns in the period
# """

