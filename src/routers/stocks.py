from fastapi import APIRouter, HTTPException, Query
from datetime import datetime

# Adjust import if services is a sibling directory
from services.stock_engine import single_stock

router = APIRouter()

@router.get("/stock/{ticker}")
def get_single_stock(
    ticker: str,
    start: datetime = Query(..., description="Start date in YYYY-MM-DD format"),
    end: datetime = Query(..., description="End date in YYYY-MM-DD format")
):
    """
    Get closing prices for a single stock within a date range.
    Example: /api/stock/AAPL?start=2024-03-01&end=2024-04-01
    """
    try:
        result = single_stock(ticker, start, end)
        return {"ticker": ticker, "start": start, "end": end, "result": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching data: {str(e)}")
