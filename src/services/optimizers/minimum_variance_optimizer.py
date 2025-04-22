# engine/optimizer.py (continued)
import numpy as np
import pandas as pd
from scipy.optimize import minimize

class MinimumVarianceOptimizer:
    """
    A class to compute the Minimum Variance Portfolio.
    The goal is to minimize portfolio variance regardless of return.
    """

    def __init__(self, S, tickers=None):
        """
        :param S: Covariance matrix of asset returns (as pd.DataFrame or np.ndarray)
        :param tickers: Optional list or index for asset names
        """
        self.S = S.values if isinstance(S, pd.DataFrame) else S
        self.N = self.S.shape[0]
        self.tickers = tickers if tickers is not None else (
            list(S.columns) if isinstance(S, pd.DataFrame) else [f"Asset {i+1}" for i in range(self.N)]
        )

    def compute_portfolio(self, allow_short=False):
        """
        Compute the minimum variance portfolio.
        :param allow_short: Whether to allow short positions (weights < 0)
        :return: weights, portfolio variance
        """
        initial_weights = np.ones(self.N) / self.N
        bounds = [(-1.0, 1.0) if allow_short else (0, 1) for _ in range(self.N)]
        constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}

        def portfolio_variance(w):
            return w @ self.S @ w

        result = minimize(portfolio_variance, initial_weights, bounds=bounds, constraints=constraints)

        if not result.success:
            raise ValueError("Minimum variance optimization failed to converge.")

        weights = result.x
        if isinstance(self.tickers, pd.Index):
            weights = pd.Series(weights, index=self.tickers)

        sigma_p2 = weights @ self.S @ weights
        return weights, sigma_p2

    def find_optimal_portfolio(self, allow_short=False):
        """
        Public method to retrieve the optimized portfolio.
        """
        weights, sigma_p2 = self.compute_portfolio(allow_short=allow_short)

        return {
            'weights': weights,
            'variance': sigma_p2
        }
