import pandas as pd
from services.data_fetcher import fetch_real_data, compute_returns

def download_and_preprocess_data(tickers, start_date, end_date):
    """
    Downloads stock data and preprocesses it to extract the 'Close' prices
    for matching dates only.
    
    Parameters:
    - tickers: list of str, stock tickers (e.g., ['ADRO.JK', 'ASII.JK']).
    - start_date: str, start date in YYYY-MM-DD format.
    - end_date: str, end date in YYYY-MM-DD format.
    
    Returns:
    - pandas DataFrame containing 'Close' prices for matching dates only.
    """
    try:
        # Step 1: Download data
        print("Downloading data from Yahoo Finance...")
        prices = fetch_real_data(tickers, start_date, end_date)
        print("Data downloaded successfully.")
        print(prices.head())
        print("\nChecking for missing values in the data:")
        print(prices.isna().sum())
        # Step 2: Extract 'Close' prices
        close_prices = prices # Select only the 'Close' prices
        # print("\nClose Prices (Before Filtering):")
        # print(close_prices.head())
        
        # Step 3: Filter rows with matching dates for all tickers
        # close_prices = close_prices.dropna()  # Drop rows with any missing values
        print("\nClose Prices (Matching Dates Only):")
        print(close_prices.info())

        returns = compute_returns(close_prices)
        print("\nDaily Returns:")
        print(returns.info(),returns.head())
        
        # return returns
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    # Define parameters
    tickers = ["ADRO.JK", "ASII.JK", "MDKA.JK", "EXCL.JK", "PGAS.JK"]
    start_date = "2021-05-12"
    end_date = "2022-05-12"
    
    # Call the function to download and preprocess data
    close_prices = download_and_preprocess_data(tickers, start_date, end_date)
    
    # If data is successfully processed, save it to a CSV file
    if close_prices is not None:
        close_prices.to_csv("close_prices.csv")
        print("\nClose prices saved to 'close_prices.csv'.")