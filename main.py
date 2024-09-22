from fastapi import FastAPI
import sqlite3

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/test/{item_id}")
async def test(item_id:str,query: int = 1):
    return {"hello" : item_id}