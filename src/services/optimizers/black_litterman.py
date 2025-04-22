# engine/optimizer.py (continued)
import numpy as np
import pandas as pd

class BlackLittermanOptimizer:
    """
    A class to perform portfolio optimization using the Black-Litterman model.
    """

    def __init__(self, mu_eq, S, P, Q, Omega=None, tau=0.05):
        """
        :param mu_eq: Equilibrium excess returns (as pd.Series or np.ndarray)
        :param S: Covariance matrix of asset returns (as pd.DataFrame or np.ndarray)
        :param P: Pick matrix for views (as np.ndarray or pd.DataFrame)
        :param Q: View returns (as np.ndarray or pd.Series)
        :param Omega: Diagonal covariance matrix of errors in views (optional)
        :param tau: Scalar for scaling the covariance matrix (typically small like 0.05)
        """
        self.mu_eq = mu_eq.values if isinstance(mu_eq, pd.Series) else mu_eq
        self.S = S.values if isinstance(S, pd.DataFrame) else S
        self.P = P.values if isinstance(P, (pd.DataFrame, pd.Series)) else P
        self.Q = Q.values if isinstance(Q, pd.Series) else Q
        self.tau = tau

        self.N = len(self.mu_eq)
        self.tickers = mu_eq.index if isinstance(mu_eq, pd.Series) else None
        self.e = np.ones(self.N)

        # If Omega is not provided, assume diagonal with small uncertainties
        if Omega is None:
            self.Omega = np.diag(np.diag(self.P @ (tau * self.S) @ self.P.T))
        else:
            self.Omega = Omega.values if isinstance(Omega, pd.DataFrame) else Omega

        # Compute the Black-Litterman expected returns
        self.mu_bl = self._compute_bl_returns()

    def _compute_bl_returns(self):
        tauS = self.tau * self.S
        middle_term = np.linalg.inv(self.P @ tauS @ self.P.T + self.Omega)
        adjustment = tauS @ self.P.T @ middle_term @ (self.Q - self.P @ self.mu_eq)
        return self.mu_eq + adjustment

    def compute_portfolio(self):
        """
        Computes the optimal weights using mean-variance optimization on BL returns.
        """
        try:
            S_inv = np.linalg.inv(self.S)
        except np.linalg.LinAlgError:
            raise ValueError("Covariance matrix is not invertible.")

        weights = S_inv @ self.mu_bl
        weights /= np.sum(weights)  # Normalize to sum to 1

        if self.tickers is not None:
            weights = pd.Series(weights, index=self.tickers)

        mu_p = weights @ self.mu_bl
        sigma_p2 = weights @ self.S @ weights
        ratio = mu_p / sigma_p2 if sigma_p2 != 0 else np.inf

        return weights, mu_p, sigma_p2, ratio

    def find_optimal_portfolio(self, enforce_positive_weights=False):
        weights, mu_p, sigma_p2, ratio = self.compute_portfolio()

        if enforce_positive_weights and (weights < 0).any():
            print("Warning: Negative weights found. Constraint enforcement not implemented.")

        return {
            'weights': weights,
            'expected_return': mu_p,
            'variance': sigma_p2,
            'ratio': ratio
        }
