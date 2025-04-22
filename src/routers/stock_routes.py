from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
from services.stock_service import single_stock, basic_stock_info, today_performance, fixed_period_performance

router = APIRouter()

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

# from fastapi import APIRouter, HTTPException, Query
# from datetime import datetime

# # Adjust import if services is a sibling directory
# from services.stock_service import single_stock

# router = APIRouter()

# @router.get("/stock/{ticker}")
# def get_single_stock(
#     ticker: str,
#     start: datetime = Query(..., description="Start date in YYYY-MM-DD format"),
#     end: datetime = Query(..., description="End date in YYYY-MM-DD format")
# ):
#     """
#     Get closing prices for a single stock within a date range.
#     Example: /api/stock/AAPL?start=2024-03-01&end=2024-04-01
#     """
#     try:
#         result = single_stock(ticker, start, end)
#         return {"ticker": ticker, "start": start, "end": end, "result": result}
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f"Error fetching data: {str(e)}")
