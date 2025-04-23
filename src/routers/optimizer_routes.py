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

@router.post("/optimizer/mean-variance")
async def optimize_portfolio(request: OptimizeRequest):
    try:
        start_date = datetime.strptime(request.start_date, '%Y-%m-%d')
        end_date = datetime.strptime(request.end_date, '%Y-%m-%d')
        optimizer = MeanVarianceOptimizer(
            tickers=request.tickers,
            start_date=start_date,
            end_date=end_date,
            tau=request.tau
        )
        report = optimizer.generate_report()
        return report
    except ValueError as e:
        logger.error(f"Optimization error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during optimization: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")