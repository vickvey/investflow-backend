import sys
import os
import pytest
from fastapi.testclient import TestClient

# Adjust path so that src is importable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from main import app
import routers.stock_routes as stock_routes_module

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_monkeypatch(monkeypatch):
    # Ensure no leftover patches between tests
    yield

# Health check route

def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World, from FastAPI!"}

# /stock/{ticker}

def test_get_single_stock_success(monkeypatch):
    dummy = [{"date": "2024-01-01", "close": 100}]
    def mock_single_stock(ticker, start, end):
        return dummy
    monkeypatch.setattr(stock_routes_module, "single_stock", mock_single_stock)

    response = client.get("/api/stock/TEST?start=2024-01-01&end=2024-02-01")
    assert response.status_code == 200
    assert response.json() == {
        "ticker": "TEST",
        "start": "2024-01-01T00:00:00",
        "end": "2024-02-01T00:00:00",
        "result": dummy
    }


def test_get_single_stock_value_error(monkeypatch):
    def mock_single_stock(ticker, start, end):
        raise ValueError("Invalid ticker")
    monkeypatch.setattr(stock_routes_module, "single_stock", mock_single_stock)

    response = client.get("/api/stock/TEST?start=2024-01-01&end=2024-02-01")
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid ticker"

# /stock/{ticker}/info

def test_get_basic_stock_info_success(monkeypatch):
    info = {"name": "Test Corp"}
    monkeypatch.setattr(stock_routes_module, "basic_stock_info", lambda t: info)
    response = client.get("/api/stock/TEST/info")
    assert response.status_code == 200
    assert response.json() == info


def test_get_basic_stock_info_value_error(monkeypatch):
    monkeypatch.setattr(stock_routes_module, "basic_stock_info", lambda t: (_ for _ in ()).throw(ValueError("No data")))
    response = client.get("/api/stock/TEST/info")
    assert response.status_code == 400
    assert response.json()["detail"] == "No data"

# /stock/{ticker}/today

def test_get_today_performance_success(monkeypatch):
    perf = {"change": 1.23}
    monkeypatch.setattr(stock_routes_module, "today_performance", lambda t: perf)
    response = client.get("/api/stock/TEST/today")
    assert response.status_code == 200
    assert response.json() == perf


def test_get_today_performance_value_error(monkeypatch):
    monkeypatch.setattr(stock_routes_module, "today_performance", lambda t: (_ for _ in ()).throw(ValueError("Market closed")))
    response = client.get("/api/stock/TEST/today")
    assert response.status_code == 400
    assert response.json()["detail"] == "Market closed"

# /stock/{ticker}/period

def test_get_fixed_period_performance_success(monkeypatch):
    perf = {"return": 5}
    monkeypatch.setattr(stock_routes_module, "fixed_period_performance", lambda t, p: perf)
    response = client.get("/api/stock/TEST/period?period=1mo")
    assert response.status_code == 200
    assert response.json() == perf


def test_get_fixed_period_performance_value_error(monkeypatch):
    monkeypatch.setattr(stock_routes_module, "fixed_period_performance", lambda t, p: (_ for _ in ()).throw(ValueError("Invalid period")))
    response = client.get("/api/stock/TEST/period?period=invalid")
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid period"

# /stock/{ticker}/performance

def test_get_performance_metrics_success(monkeypatch):
    metrics = {"volatility": 0.5}
    monkeypatch.setattr(stock_routes_module, "get_stock_performance_metrics", lambda t, s, e: metrics)
    response = client.get("/api/stock/TEST/performance?start=2024-01-01&end=2024-03-01")
    assert response.status_code == 200
    assert response.json() == metrics


def test_get_performance_metrics_value_error(monkeypatch):
    monkeypatch.setattr(stock_routes_module, "get_stock_performance_metrics", lambda t, s, e: (_ for _ in ()).throw(ValueError("Bad range")))
    response = client.get("/api/stock/TEST/performance?start=2024-01-01&end=2024-03-01")
    assert response.status_code == 400
    assert response.json()["detail"] == "Bad range"

# /stock/{ticker}/history

def test_get_stock_history_success(monkeypatch):
    prices = [{"date": "2024-01-01", "price": 100}]
    volumes = [{"date": "2024-01-01", "volume": 1000}]
    monkeypatch.setattr(stock_routes_module, "get_price_history", lambda t, s, e: prices)
    monkeypatch.setattr(stock_routes_module, "get_volume_history", lambda t, s, e: volumes)
    response = client.get("/api/stock/TEST/history?start=2024-01-01&end=2024-03-01")
    assert response.status_code == 200
    assert response.json() == {"priceHistory": prices, "volumeHistory": volumes}


def test_get_stock_history_value_error(monkeypatch):
    volumes = [{"date": "2024-01-01", "volume": 1000}]  # ✅ Add this line
    monkeypatch.setattr(stock_routes_module, "get_price_history", lambda t, s, e: (_ for _ in ()).throw(ValueError("No data")))
    monkeypatch.setattr(stock_routes_module, "get_volume_history", lambda t, s, e: volumes)
    response = client.get("/api/stock/TEST/history?start=2024-01-01&end=2024-03-01")
    assert response.status_code == 400
    assert response.json()["detail"] == "No data"

