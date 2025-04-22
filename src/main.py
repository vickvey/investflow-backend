from fastapi import FastAPI
from routers import stocks  # correct relative import

app = FastAPI()

app.include_router(stocks.router, prefix="/api", tags=["stocks"])

@app.get("/")
def say_hello_world():
    return {"msg": "Hello World, from FastAPI!"}
