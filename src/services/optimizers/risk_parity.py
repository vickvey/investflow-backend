# engine/optimizer.py (continued)
import numpy as np
import pandas as pd
from scipy.optimize import minimize

class RiskParityOptimizer:
    """
    A class to perform portfolio optimization using the Risk Parity approach.
    Each asset contributes equally to portfolio risk.
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

    def _risk_contribution(self, weights):
        portfolio_vol = np.sqrt(weights.T @ self.S @ weights)
        marginal_contrib = self.S @ weights
        risk_contrib = weights * marginal_contrib / portfolio_vol
        return risk_contrib

    def _objective(self, weights):
        rc = self._risk_contribution(weights)
        target = np.mean(rc)
        return np.sum((rc - target)**2)

    def compute_portfolio(self, initial_weights=None):
        """
        Finds weights that equalize the risk contribution of each asset.
        """
        if initial_weights is None:
            initial_weights = np.ones(self.N) / self.N

        bounds = [(0, 1) for _ in range(self.N)]
        constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}

        result = minimize(self._objective, initial_weights, bounds=bounds, constraints=constraints)

        if not result.success:
            raise ValueError("Risk parity optimization failed to converge.")

        weights = result.x
        if isinstance(self.tickers, pd.Index):
            weights = pd.Series(weights, index=self.tickers)

        mu_p = None  # Not defined in risk parity; optional to provide mu externally
        sigma_p2 = weights @ self.S @ weights
        risk_contrib = self._risk_contribution(weights)

        return weights, sigma_p2, risk_contrib

    def find_optimal_portfolio(self):
        weights, sigma_p2, risk_contrib = self.compute_portfolio()

        return {
            'weights': weights,
            'variance': sigma_p2,
            'risk_contributions': risk_contrib
        }
