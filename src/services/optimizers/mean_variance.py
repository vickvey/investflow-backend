import numpy as np
import pandas as pd
from datetime import datetime
from services.data_fetcher import DataFetcher
from services.return_models.historical_return import compute_historical_returns
from services.risk_calculator import compute_covariance_matrix, compute_downside_deviation, compute_max_drawdown

class Mean_variance_optimizer:
    """
    A class to perform Markowitz portfolio optimization as per Sirait et al.
    """
    
    def __init__(self, mu, S):
        self.mu = mu.values if isinstance(mu, pd.Series) else mu
        self.S = S.values if isinstance(S, pd.DataFrame) else S
        self.tickers = mu.index if isinstance(mu, pd.Series) else None
        self.N = len(self.mu)
        self.e = np.ones(self.N)
        try:
            self.S_inv = np.linalg.inv(self.S)
        except np.linalg.LinAlgError:
            raise ValueError("Covariance matrix is not invertible.")
        
        self.A = self.S_inv @ self.e
        self.B = self.S_inv @ self.mu
        self.a = self.e @ self.A
        self.b = self.e @ self.B
    
    def compute_portfolio(self, tau):
        if tau < 0:
            raise ValueError("Risk tolerance tau must be non-negative.")
        
        w = (1 / self.a) * self.A + tau * (self.B - (self.b / self.a) * self.A)
        if self.tickers is not None:
            w = pd.Series(w, index=self.tickers)
        mu_p = w @ self.mu
        sigma_p2 = w @ self.S @ w
        ratio = mu_p / sigma_p2 if sigma_p2 != 0 else np.inf
        return w, mu_p, sigma_p2, ratio
    
    def find_optimal_portfolio(self, tau_range=(0, 2), num_points=100, enforce_positive_weights=False):
        if tau_range[0] < 0 or tau_range[1] < tau_range[0]:
            raise ValueError("tau_range must contain non-negative values with min <= max.")
        
        taus = np.linspace(tau_range[0], tau_range[1], num_points)
        results = [self.compute_portfolio(tau) for tau in taus]
        
        for tau, (w, mu_p, sigma_p2, ratio) in zip(taus, results):
            print(f"tau={tau:.2f}, weights={w.round(4)}, ratio={ratio:.2f}")
        
        if enforce_positive_weights:
            valid_indices = [i for i, result in enumerate(results) if all(result[0] >= 0)]
            if not valid_indices:
                print("Warning: No positive-weight portfolio found. Using best without constraint.")
                ratios = [result[3] for result in results]
                optimal_idx = np.argmax(ratios)
            else:
                ratios = [results[i][3] for i in valid_indices]
                optimal_idx = valid_indices[np.argmax(ratios)]
        else:
            ratios = [result[3] for result in results]
            optimal_idx = np.argmax(ratios)
        
        optimal_tau = taus[optimal_idx]
        optimal_w, optimal_mu_p, optimal_sigma_p2, optimal_ratio = results[optimal_idx]
        
        return {
            'tau': optimal_tau,
            'weights': optimal_w,
            'expected_return': optimal_mu_p,
            'variance': optimal_sigma_p2,
            'ratio': optimal_ratio
        }

class MeanVarianceOptimizer:
    """
    Main class for mean-variance portfolio optimization using historical returns.
    """
    def __init__(self, tickers: list[str], start_date: datetime, end_date: datetime, tau: float, return_model: str = 'historical_returns'):
        if not isinstance(tickers, list) or not tickers:
            raise ValueError("Tickers must be a non-empty list")
        if not all(isinstance(t, str) for t in tickers):
            raise ValueError("All tickers must be strings")
        if not isinstance(start_date, datetime) or not isinstance(end_date, datetime):
            raise ValueError("Start and end dates must be datetime objects")
        if start_date >= end_date:
            raise ValueError("Start date must be earlier than end date")
        if tau < 0:
            raise ValueError("Risk tolerance tau must be non-negative")
        if return_model != 'historical_returns':
            raise ValueError("Only 'historical_returns' is supported for now")
        
        self.tickers = tickers
        self.start_date = start_date
        self.end_date = end_date
        self.tau = tau
        self.return_model = return_model
        self.annualization_factor = 252  # Trading days per year
        
        # Fetch data once
        self.prices = self._fetch_data()
        self.returns = compute_historical_returns(self.prices)
        self.mu = self.returns.mean()  # Expected returns
        self.S = compute_covariance_matrix(self.returns)  # Covariance matrix
        
        # Perform optimization
        self.optimizer = Mean_variance_optimizer(self.mu, self.S)
        self.optimal_portfolio = self.optimizer.compute_portfolio(self.tau)
        self.weights = self.optimal_portfolio[0]
        self.expected_return = self.optimal_portfolio[1]  # Daily
        self.variance = self.optimal_portfolio[2]  # Daily
        self.portfolio_returns = (self.returns @ self.weights).dropna()

    def _fetch_data(self) -> pd.DataFrame:
        """
        Fetch historical closing prices for all tickers.
        """
        try:
            data = DataFetcher.multiple_stocks_data(
                self.tickers,
                self.start_date.strftime('%Y-%m-%d'),
                self.end_date.strftime('%Y-%m-%d')
            )
            if data.empty:
                raise ValueError("No data fetched for the given tickers and date range")
            return data
        except Exception as e:
            raise ValueError(f"Data fetching failed: {str(e)}")

    def generate_report(self) -> dict:
        """
        Generate a report with optimal weights and performance metrics.
        
        Returns:
            dict: Portfolio weights and metrics formatted for the frontend.
        """
        # Annualize metrics
        annualized_return = self.expected_return * self.annualization_factor
        annualized_volatility = np.sqrt(self.variance * self.annualization_factor)
        
        # Risk-free rate assumption
        risk_free_rate = 0.02  # 2% annual
        annualized_excess_return = annualized_return - risk_free_rate
        
        # Sharpe Ratio
        sharpe_ratio = annualized_excess_return / annualized_volatility if annualized_volatility != 0 else 0
        
        # Sortino Ratio
        downside_deviation = compute_downside_deviation(self.portfolio_returns)
        annualized_downside_deviation = downside_deviation * np.sqrt(self.annualization_factor)
        sortino_ratio = annualized_excess_return / annualized_downside_deviation if annualized_downside_deviation != 0 else 0
        
        # Max Drawdown
        portfolio_prices = (self.prices @ self.weights).dropna()
        max_drawdown = compute_max_drawdown(portfolio_prices)
        
        # Format weights as percentages
        weights_dict = {ticker: round(weight * 100, 2) for ticker, weight in zip(self.tickers, self.weights)}
        
        return {
            'weights': weights_dict,
            'metrics': {
                'expectedReturn': round(annualized_return * 100, 2),  # Percentage
                'risk': round(annualized_volatility * 100, 2),  # Percentage
                'sharpeRatio': round(sharpe_ratio, 2),
                'sortinoRatio': round(sortino_ratio, 2),
                'maxDrawdown': round(max_drawdown * 100, 2),  # Percentage
            }
        }