# engine/optimizer.py (continued)
import numpy as np
import pandas as pd
from scipy.optimize import minimize

class MaximumSharpeRatioOptimizer:
    """
    A class to compute the Maximum Sharpe Ratio Portfolio.
    The goal is to maximize the Sharpe ratio, defined as (expected return - risk-free rate) / portfolio volatility.
    """

    def __init__(self, mu, S, rf=0, tickers=None):
        """
        :param mu: Expected returns of the assets (as pd.Series or np.ndarray)
        :param S: Covariance matrix of asset returns (as pd.DataFrame or np.ndarray)
        :param rf: Risk-free rate, default is 0
        :param tickers: Optional list or index for asset names
        """
        self.mu = mu.values if isinstance(mu, pd.Series) else mu
        self.S = S.values if isinstance(S, pd.DataFrame) else S
        self.rf = rf
        self.N = len(self.mu)
        self.tickers = tickers if tickers is not None else (
            list(mu.index) if isinstance(mu, pd.Series) else [f"Asset {i+1}" for i in range(self.N)]
        )

    def compute_portfolio(self):
        """
        Compute the Maximum Sharpe Ratio portfolio.
        :return: weights, expected return, portfolio volatility, Sharpe ratio
        """
        def sharpe_ratio(w):
            # Portfolio return and volatility
            mu_p = w @ self.mu
            sigma_p = np.sqrt(w @ self.S @ w)
            return -(mu_p - self.rf) / sigma_p  # We negate to maximize instead of minimize

        # Initial equal weights
        initial_weights = np.ones(self.N) / self.N
        bounds = [(0, 1) for _ in range(self.N)]  # No shorting by default
        constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}

        result = minimize(sharpe_ratio, initial_weights, bounds=bounds, constraints=constraints)

        if not result.success:
            raise ValueError("Maximum Sharpe ratio optimization failed to converge.")

        weights = result.x
        if isinstance(self.tickers, pd.Index):
            weights = pd.Series(weights, index=self.tickers)

        mu_p = weights @ self.mu
        sigma_p = np.sqrt(weights @ self.S @ weights)
        sharpe_ratio_value = (mu_p - self.rf) / sigma_p

        return weights, mu_p, sigma_p**2, sharpe_ratio_value

    def find_optimal_portfolio(self):
        """
        Public method to retrieve the optimal portfolio with the maximum Sharpe ratio.
        """
        weights, mu_p, sigma_p2, sharpe_ratio_value = self.compute_portfolio()

        return {
            'weights': weights,
            'expected_return': mu_p,
            'variance': sigma_p2,
            'sharpe_ratio': sharpe_ratio_value
        }
