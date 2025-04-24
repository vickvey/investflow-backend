import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import stock_routes
from routers.optimizer_routes import router as optimizer_router
from dotenv import load_dotenv
load_dotenv()

# Setup logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s %(message)s')

# Initialize FastAPI app
app = FastAPI()

# Configure CORS for development
origins_env = os.getenv("ALLOWED_ORIGINS", "")
allowed_origins = [origin.strip() for origin in origins_env.split(",") if origin.strip()]
logger.info(f"CORS configured with origins: {allowed_origins}")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the stock routes
app.include_router(stock_routes.router, prefix="/api", tags=["stocks"])
app.include_router(optimizer_router, prefix="/api", tags=["optimizer"])

# Simple health check route
@app.get("/")
def say_hello_world():
    logger.info("Health check request received")
    return {"msg": "Hello World, from FastAPI!"}

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting FastAPI application")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
