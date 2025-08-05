from fastapi import FastAPI, HTTPException, Request, Body 
from databases import Database
from sqlalchemy import create_engine
from models import Guide, Track, Base
from schemas import GuideCreate, TrackCreate

from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates

DATABASE_URL = "postgresql://altagrasa:pinkelephant@localhost:5432/altagrasa" 
database = Database(DATABASE_URL)

app = FastAPI()
templates = Jinja2Templates(directory="../templates")

@app.on_event("startup")
async def startup():
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine) 
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/health")
async def health():
    await database.execute("SELECT 1")
    return {"status": "ok"}

# Routes for guides 
@app.post("/guides/")
async def post_guide(payload: GuideCreate):
    guide_query = Guide.__table__.insert().values(
        title=payload.title,
        description=payload.description,
        category=payload.category
    )
    guide_id = await database.execute(guide_query)
    
    # Insert tracks if provided
    if payload.tracks:
        for track_data in payload.tracks:
            track_query = Track.__table__.insert().values(
                title=track_data.title,
                file_path=track_data.file_path,
                duration=track_data.duration,
                order_num=track_data.order_num,
                guide_id=guide_id
            )
            await database.execute(track_query)
    
    return {"message": "guide saved", "guide_id": guide_id}

@app.get("/guides/{id}", response_class=HTMLResponse)
async def read_guide(request: Request, id: int):
    guide_query = Guide.__table__.select().where(Guide.__table__.c.id == id)
    guide = await database.fetch_one(guide_query)

    if not guide:
        raise HTTPException(status_code=404, detail="Guide not found")
    
    # Get tracks for this guide
    tracks_query = Track.__table__.select().where(Track.__table__.c.guide_id == id).order_by(Track.__table__.c.order_num)
    tracks = await database.fetch_all(tracks_query)
    
    return templates.TemplateResponse(
        request=request,
        name="guides.html",
        context={"guide": guide, "tracks": tracks}
    )

@app.get("/guides/")
async def list_guides():
    query = Guide.__table__.select()
    guides = await database.fetch_all(query)
    return {"guides": guides}

@app.delete("/guides/{id}")
async def delete_guide(id: int):
    # First check if guide exists
    guide_query = Guide.__table__.select().where(Guide.__table__.c.id == id)
    guide = await database.fetch_one(guide_query)
    
    if not guide:
        raise HTTPException(status_code=404, detail="Guide not found")
    
    # Delete tracks first (due to foreign key constraint)
    tracks_delete_query = Track.__table__.delete().where(Track.__table__.c.guide_id == id)
    await database.execute(tracks_delete_query)
    
    # Then delete the guide
    guide_delete_query = Guide.__table__.delete().where(Guide.__table__.c.id == id)
    await database.execute(guide_delete_query)
    
    return {"message": f"Guide {id} and its tracks deleted successfully"}

#endpoints for tracks
# Get tracks for a specific guide (already covered in your guide detail)
@app.get("/guides/{guide_id}/tracks")
async def get_guide_tracks(guide_id: int):
    query = Track.__table__.select().where(Track.__table__.c.guide_id == guide_id).order_by(Track.__table__.c.order_num)
    tracks = await database.fetch_all(query)
    return {"tracks": tracks}

# Stream audio file - this is critical
@app.get("/tracks/{track_id}/audio")
async def stream_audio(track_id: int):
    track_query = Track.__table__.select().where(Track.__table__.c.id == track_id)
    track = await database.fetch_one(track_query)
    
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    
    return FileResponse(track["file_path"], media_type="audio/mpeg")