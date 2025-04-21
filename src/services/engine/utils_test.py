import pandas as pd
from services.data_fetcher import fetch_real_data, compute_returns
from utils import compute_mu_S_from_prices

def test_compute_mu_S():
    # Define parameters
    tickers = ["ADRO.JK", "ASII.JK", "MDKA.JK", "EXCL.JK", "PGAS.JK"]
    start_date = "2021-05-12"
    end_date = "2022-05-12"
    
    # Step 1: Fetch price data
    print("Fetching price data...")
    prices = fetch_real_data(tickers, start_date, end_date)
    print("\nPrice Data:")
    print(prices.head())
    
    # Step 2: Compute daily returns
    returns = compute_returns(prices)
    print("\nDaily Returns:")
    print(returns.head())
    
    # Step 3: Compute mu and S
    mu, S = compute_mu_S_from_prices(returns)
    print("\nExpected Returns (mu):")
    print(mu)
    print("\nCovariance Matrix (S):")
    print(S)

if __name__ == "__main__":
    test_compute_mu_S()