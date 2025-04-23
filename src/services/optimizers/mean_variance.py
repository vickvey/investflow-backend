import numpy as np
import pandas as pd
from datetime import datetime
from scipy.optimize import minimize
from services.data_fetcher import DataFetcher

class MeanVarianceOptimizer:
    """
    Main class for mean-variance portfolio optimization using historical returns.
    """
    def __init__(self, tickers: list[str], start_date: datetime, end_date: datetime, tau: float, return_model: str = 'simple'):
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
        if return_model not in ['simple', 'log']:
            raise ValueError("return_model must be 'simple' or 'log'")
        
        self.tickers = tickers
        self.start_date = start_date
        self.end_date = end_date
        self.tau = tau
        self.return_model = return_model
        self.annualization_factor = 252  # Trading days per year
        self.decimal_precision = 12
        
        # Fetch and process data
        self.prices = self._fetch_data()
        self.returns = self._compute_returns()
        self.mu = self.returns.mean()  # Expected daily returns
        self.S = self.returns.cov()  # Covariance matrix
        
        # Optimize portfolio
        self.weights = self._optimize_portfolio()
        self.expected_return = np.dot(self.weights, self.mu)  # Daily
        self.variance = np.dot(self.weights.T, np.dot(self.S.values, self.weights))  # Daily
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

    def _compute_returns(self) -> pd.DataFrame:
        """
        Compute daily returns for all tickers based on return_model.
        """
        if self.return_model == 'simple':
            returns = self.prices.pct_change().dropna()
        else:  # log
            returns = np.log(self.prices / self.prices.shift(1)).dropna()
        
        if returns.empty:
            raise ValueError("No valid returns data after processing")
        
        # Rename columns for clarity
        returns.columns = [f'{ticker}_DLR' for ticker in self.tickers]
        return returns

    def _compute_downside_deviation(self, returns: pd.Series) -> float:
        """
        Compute downside deviation of portfolio returns (negative returns only).
        """
        negative_returns = returns[returns < 0]
        if len(negative_returns) == 0:
            return 0.0
        return np.sqrt(np.mean(negative_returns ** 2))

    def _compute_max_drawdown(self, prices: pd.Series) -> float:
        """
        Compute maximum drawdown of portfolio prices.
        """
        cumulative = prices.cumsum() if self.return_model == 'simple' else prices.cumprod()
        peak = cumulative.cummax()
        drawdown = (cumulative - peak) / peak
        return abs(drawdown.min()) if not drawdown.empty else 0.0

    def _objective_function(self, w: np.ndarray) -> float:
        """
        Objective function for portfolio optimization: maximize 2*tau*mu_p - w^T*Sigma*w.
        """
        return -(2 * self.tau * np.dot(w, self.mu) - np.dot(w.T, np.dot(self.S.values, w)))

    def _optimize_portfolio(self) -> np.ndarray:
        """
        Optimize portfolio weights using mean-variance optimization.
        """
        n = len(self.tickers)
        
        # Constraints: sum of weights = 1
        constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
        
        # Bounds: non-negative weights
        bounds = [(0, None)] * n
        
        # Initial guess: equal weights
        w0 = np.ones(n) / n
        
        # Run optimization
        result = minimize(
            self._objective_function,
            w0,
            args=(),
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        if not result.success:
            raise ValueError("Optimization failed: " + result.message)
        
        return np.round(result.x, self.decimal_precision)

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
        downside_deviation = self._compute_downside_deviation(self.portfolio_returns)
        annualized_downside_deviation = downside_deviation * np.sqrt(self.annualization_factor)
        sortino_ratio = annualized_excess_return / annualized_downside_deviation if annualized_downside_deviation != 0 else 0
        
        # Max Drawdown
        portfolio_prices = (self.prices @ self.weights).dropna()
        max_drawdown = self._compute_max_drawdown(portfolio_prices)
        
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