from fastapi import APIRouter, HTTPException
from datetime import datetime
from pydantic import BaseModel
from services.optimizers.mean_variance import MeanVarianceOptimizer
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

class OptimizeRequest(BaseModel):
    tickers: list[str]
    start_date: str
    end_date: str
    tau: float = 0.5
    return_model: str = "simple"

@router.post("/optimizer/mean-variance")
async def optimize_portfolio(request: OptimizeRequest):
    try:
        # Validate tau
        if request.tau < 0:
            raise ValueError("Risk tolerance tau must be non-negative")
        
        # Validate return_model
        if request.return_model not in ["simple", "log"]:
            raise ValueError("return_model must be 'simple' or 'log'")
        
        # Parse dates with strict format
        try:
            start_date = datetime.strptime(request.start_date, '%Y-%m-%d')
            end_date = datetime.strptime(request.end_date, '%Y-%m-%d')
        except ValueError as e:
            raise ValueError("Dates must be in YYYY-MM-DD format")
        
        # Validate date order
        if start_date >= end_date:
            raise ValueError("Start date must be earlier than end date")
        
        # Validate tickers
        if not request.tickers or not all(isinstance(t, str) for t in request.tickers):
            raise ValueError("Tickers must be a non-empty list of strings")
        
        optimizer = MeanVarianceOptimizer(
            tickers=request.tickers,
            start_date=start_date,
            end_date=end_date,
            tau=request.tau,
            return_model=request.return_model
        )
        report = optimizer.generate_report()
        return report
    except ValueError as e:
        logger.error(f"Optimization error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during optimization: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")