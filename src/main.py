from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import stock_routes

app = FastAPI()

# CORS configuration for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

app.include_router(stock_routes.router, prefix="/api", tags=["stocks"])

@app.get("/")
def say_hello_world():
    return {"msg": "Hello World, from FastAPI!"}