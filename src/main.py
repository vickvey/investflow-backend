from fastapi import FastAPI

app = FastAPI()

@app.get('/')
def say_hello_world():
    return {"msg": "Hello World, from FastAPI!"}