import sys
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from routers import stock_routes  # Updated import path

# Load environment variables from .env file
load_dotenv()

# Read and split origins from the environment variable, with a default fallback
origins = os.getenv("ALLOWED_ORIGINS", "").split(",") + ['http://localhost:3000']

# Initialize FastAPI app
app = FastAPI()

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # List of allowed origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Include the stock routes (ensure 'stock_routes.router' is correctly set in your routers)
app.include_router(stock_routes.router, prefix="/api", tags=["stocks"])

# Simple health check route
@app.get("/")
def say_hello_world():
    return {"msg": "Hello World, from FastAPI!"}

# Entry point for running the app directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)  # Enable auto-reloading in development
