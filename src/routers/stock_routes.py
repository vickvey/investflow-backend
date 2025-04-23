from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
from services.stock_service import (
    single_stock,
    basic_stock_info,
    today_performance,
    fixed_period_performance,
    get_stock_performance_metrics,
    get_price_history,
    get_volume_history
)

router = APIRouter()

@router.get("/stock/{ticker}/info")
def get_basic_stock_info(ticker: str):
    """
    Get basic stock information for a single ticker.
    Example: /api/stock/AAPL/info
    """
    try:
        result = basic_stock_info(ticker)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stock info: {str(e)}")

@router.get("/stock/{ticker}")
def get_single_stock(
    ticker: str,
    start: datetime = Query(..., description="Start date in YYYY-MM-DD format"),
    end: datetime = Query(..., description="End date in YYYY-MM-DD format")
):
    """
    Get historical closing prices for a single stock within a date range.
    Example: /api/stock/AAPL?start=2024-03-01&end=2024-04-01
    """
    try:
        return {"ticker": ticker, "start": start, "end": end, "result": single_stock(ticker, start, end)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")

@router.get("/stock/{ticker}/today")
def get_today_performance(ticker: str):
    """
    Get today's performance metrics for a stock.
    Example: /api/stock/AAPL/today
    """
    try:
        result = today_performance(ticker)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching today's performance: {str(e)}")

@router.get("/stock/{ticker}/period")
def get_fixed_period_performance(
    ticker: str,
    period: str = Query("1mo", description="Period for performance (e.g., 1d, 5d, 1mo, 3mo, 6mo, 1y)")
):
    """
    Get performance metrics for a stock over a fixed period.
    Example: /api/stock/AAPL/period?period=1mo
    """
    try:
        result = fixed_period_performance(ticker, period)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching period performance: {str(e)}")

@router.get("/stock/{ticker}/performance")
def get_performance_metrics(
    ticker: str,
    start: datetime = Query(..., description="Start date in YYYY-MM-DD format"),
    end: datetime = Query(..., description="End date in YYYY-MM-DD format")
):
    """
    Get performance metrics for a stock over a date range.
    Example: /api/stock/AAPL/performance?start=2024-01-01&end=2024-12-31
    """
    try:
        result = get_stock_performance_metrics(ticker, start, end)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching performance metrics: {str(e)}")

@router.get("/stock/{ticker}/history")
def get_stock_history(
    ticker: str,
    start: datetime = Query(..., description="Start date in YYYY-MM-DD format"),
    end: datetime = Query(..., description="End date in YYYY-MM-DD format")
):
    """
    Get price and volume history for a stock over a date range.
    Example: /api/stock/AAPL/history?start=2024-01-01&end=2024-12-31
    """
    try:
        price_history = get_price_history(ticker, start, end)
        volume_history = get_volume_history(ticker, start, end)
        return {
            "priceHistory": price_history,
            "volumeHistory": volume_history
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching history data: {str(e)}")