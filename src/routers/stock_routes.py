from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
from services.stock_service import (
    single_stock,
    basic_stock_info,
    today_performance,
    fixed_period_performance,
    get_stock_performance_metrics,
    get_price_history,
    get_volume_history,
    compare_stocks,
    get_stock_ohlc,
    get_top_performers
)
import re

router = APIRouter()

def validate_ticker(ticker: str) -> str:
    """Validate that the ticker is a non-empty string of 1-10 uppercase alphanumeric characters."""
    if not ticker or not isinstance(ticker, str):
        raise HTTPException(status_code=422, detail="Ticker must be a non-empty string")
    if not re.match(r"^[A-Z0-9]{1,10}$", ticker):
        raise HTTPException(status_code=422, detail="Invalid ticker format. Use uppercase alphanumeric characters (1-10 length)")
    return ticker.strip()

@router.get("/stock/{ticker}/info")
def get_basic_stock_info(ticker: str):
    """
    Get basic stock information for a single ticker.
    Example: /api/stock/AAPL/info
    """
    try:
        ticker = validate_ticker(ticker)
        result = basic_stock_info(ticker)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stock info: {str(e)}")

# New Added
@router.get("/stock/compare")
def compare_two_stocks(
    stock1: str = Query(default="AAPL", description="First stock ticker"),
    stock2: str = Query(default="GOOGL", description="Second stock ticker")
):
    """
    Compare two stocks over the last 12 months, returning key metrics and price history.
    Example: /api/stock/compare?stock1=AAPL&stock2=GOOGL
    """
    try:
        stock1 = validate_ticker(stock1)
        stock2 = validate_ticker(stock2)
        result = compare_stocks(stock1, stock2)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error comparing stocks: {str(e)}")

# New Added
@router.get("/stock/top-performers")
def get_top_performers_route(
    index: str = Query("NIFTY", description="Index to fetch top performers for (NIFTY or SENSEX)")
):
    """
    Get top 10 performing stocks for the specified index over the last 12 months.
    Example: /api/stock/top-performers?index=NIFTY
    """
    try:
        if index not in ["NIFTY", "SENSEX"]:
            raise ValueError("Index must be either NIFTY or SENSEX")
        result = get_top_performers(index)
        return {"performers": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching top performers: {str(e)}")

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
        ticker = validate_ticker(ticker)
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
        ticker = validate_ticker(ticker)
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
        ticker = validate_ticker(ticker)
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
        ticker = validate_ticker(ticker)
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
        ticker = validate_ticker(ticker)
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
    
# New Added
# @router.get("/stock/{ticker}/ohlc")
# def get_stock_ohlc_data(
#     ticker: str,
#     start: datetime = Query(..., description="Start date in YYYY-MM-DD format"),
#     end: datetime = Query(..., description="End date in YYYY-MM-DD format")
# ):
#     """
#     Get OHLC (Open, High, Low, Close) data for candlestick charts.
#     Example: /api/stock/AAPL/ohlc?start=2024-03-01&end=2024-04-01
#     """
#     try:
#         ticker = validate_ticker(ticker)
#         result = get_stock_ohlc(ticker, start, end)
#         return result
#     except ValueError as e:
#         raise HTTPException(status_code=400, detail=str(e))
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error fetching OHLC data: {str(e)}")

@router.get("/stock/{ticker}/ohlc")
def get_stock_ohlc_data(
    ticker: str,
    start: datetime = Query(..., description="YYYY-MM-DD"),
    end:   datetime = Query(..., description="YYYY-MM-DD"),
):
    """
    Example: GET /api/stock/AAPL/ohlc?start=2024-03-01&end=2024-04-01
    """
    try:
        ticker = validate_ticker(ticker)
        return get_stock_ohlc(ticker, start, end)
    except ValueError as e:
        raise HTTPException(400, detail=str(e))
    except Exception as e:
        raise HTTPException(500, detail=f"Error fetching OHLC data: {e}")
    
