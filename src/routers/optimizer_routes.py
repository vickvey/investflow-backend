from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
import numpy as np
import pandas as pd

from services.optimizers.minimum_variance_optimizer import MinimumVarianceOptimizer

router = APIRouter()

class OptimizationRequest(BaseModel):
    covariance_matrix: list[list[float]]
    tickers: list[str] | None = None
    allow_short: bool = False

@router.post("/portfolio/minimum-variance")
def optimize_minimum_variance_portfolio(data: OptimizationRequest = Body(...)):
    """
    Optimize the minimum variance portfolio given a covariance matrix.
    POST /api/portfolio/minimum-variance
    """
    try:
        # Create covariance matrix as DataFrame or ndarray
        cov_matrix = (
            pd.DataFrame(data.covariance_matrix, index=data.tickers, columns=data.tickers)
            if data.tickers else np.array(data.covariance_matrix)
        )

        optimizer = MinimumVarianceOptimizer(cov_matrix, tickers=data.tickers)
        result = optimizer.find_optimal_portfolio(allow_short=data.allow_short)

        # Convert weights to dictionary if they are in pandas Series
        if isinstance(result['weights'], pd.Series):
            result['weights'] = result['weights'].to_dict()

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error optimizing portfolio: {str(e)}")
