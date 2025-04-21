# engine/optimizer.py
import numpy as np
import pandas as pd

class MarkowitzOptimizer:
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
        
        # Debugging output
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