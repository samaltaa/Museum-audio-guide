from fastapi import FastAPI, HTTPException, Request, Body 
from databases import Database
from sqlalchemy import *
from models import Guide, Track, Base
from schemas import GuideCreate, TrackCreate

#template 
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

DATABASE_URL = "" 
database = Database(DATABASE_URL)

app = FastAPI()

templates = Jinja2Templates(directory="templates")


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

#routes for guides 
@app.post("/guides/")
async def post_guide(payload: GuideCreate):
    guide_data = {
        "title": payload.title,
        "description": payload.description,
        "category": payload.category
    }

    guide_id = await database.execute(Guide.insert().values(**guide_data))

    
    return {"message": "guide saved", "guide_id": guide_id}

@app.get("/guides/{id}", response_class=HTMLResponse)
async def read_guide(request: Request, id: int):

    query = Guide.select().where(Guide.c.id == id)
    guide = await database.fetch_one(query)

    if not guide:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return templates.TemplateResponse(
        request=request,
        name="guides.html",
        context={"Guide": Guide}
    )

#routes for