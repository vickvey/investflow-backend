import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import stock_routes
from dotenv import load_dotenv
from starlette.middleware.base import BaseHTTPMiddleware

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Custom Middleware to log requests
class LogRequestMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        logger.info(f"Received request: {request.method} {request.url}")
        response = await call_next(request)
        return response

# Add the logging middleware first
app.add_middleware(LogRequestMiddleware)

# Allow all origins for development environment
origins = ["*"] if os.getenv("ENV") == "development" else os.getenv("ALLOWED_ORIGINS", "*").split(",")

# CORS middleware should be added after the logging middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Log the CORS configuration
logger.info(f"CORS configured with origins: {origins}")

# Include the stock routes
app.include_router(stock_routes.router, prefix="/api", tags=["stocks"])

# Simple health check route
@app.get("/")
def say_hello_world():
    logger.info("Health check request received")
    return {"msg": "Hello World, from FastAPI!"}

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting FastAPI application")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)  # Enable auto-reloading in development
