from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import stock_routes
from dotenv import load_dotenv
import os

# Load env variables from .env file
load_dotenv()

# Read and split origins
origins = os.getenv("ALLOWED_ORIGINS", "").split(",") + ['http://localhost']

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(stock_routes.router, prefix="/api", tags=["stocks"])

@app.get("/")
def say_hello_world():
    return {"msg": "Hello World, from FastAPI!"}
