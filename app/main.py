from fastapi import FastAPI, HTTPException, Body 
from databases import Database
from sqlalchemy import *
from models import Guide, Track, Base

DATABASE_URL = "" 
database = Database(DATABASE_URL)

app = FastAPI()

@app.on_event("startup")
async def startup():
    engine = create_engine(DATABASE_URL)
    Base.create_all(engine) 
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/health")
async def health():
    await database.execute("SELECT 1")
    return {"status": "ok"}

#routes
@app.post("/guides/")
async def post_audio(Guide)