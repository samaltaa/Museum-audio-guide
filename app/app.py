from fastapi import FastAPI, HTTPException, Request
from .schemas import GuideCreate

from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import json
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent  # go up from app/ to project root

# File path for JSON data
DATA_FILE = Path(__file__).resolve().parent / "data" / "guides.json"
DATA_FILE.parent.mkdir(exist_ok=True)

app = FastAPI()
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# Helper functions to replace database operations
def load_data():
    if DATA_FILE.exists():
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {"guides": [], "tracks": [], "next_guide_id": 1, "next_track_id": 1}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

@app.on_event("startup")
async def startup():
    # Initialize JSON file if it doesn't exist
    if not DATA_FILE.exists():
        initial_data = {"guides": [], "tracks": [], "next_guide_id": 1, "next_track_id": 1}
        save_data(initial_data)

@app.get("/health")
async def health():
    return {"status": "ok"}

# Routes for guides 
@app.get("/", response_class=HTMLResponse)
async def homepage(request: Request):
    data = load_data()
    guides = data["guides"]
    return templates.TemplateResponse(
        request=request,
        name="base.html",
        context={"guides": guides}
    )

@app.post("/guides/")
async def post_guide(payload: GuideCreate):
    data = load_data()
    
    guide_id = data["next_guide_id"]
    
    # Create guide
    new_guide = {
        "id": guide_id,
        "title": payload.title,
        "description": payload.description,
        "category": payload.category
    }
    data["guides"].append(new_guide)
    data["next_guide_id"] += 1
    
    # Insert tracks if provided
    if payload.tracks:
        for track_data in payload.tracks:
            new_track = {
                "id": data["next_track_id"],
                "title": track_data.title,
                "file_path": track_data.file_path,
                "duration": track_data.duration,
                "order_num": track_data.order_num,
                "guide_id": guide_id
            }
            data["tracks"].append(new_track)
            data["next_track_id"] += 1
    
    save_data(data)
    return {"message": "guide saved", "guide_id": guide_id}

@app.get("/guides/{id}", response_class=HTMLResponse)
async def read_guide(request: Request, id: int):
    data = load_data()
    
    # Find guide
    guide = next((g for g in data["guides"] if g["id"] == id), None)
    if not guide:
        raise HTTPException(status_code=404, detail="Guide not found")
    
    # Get tracks for this guide
    tracks = [t for t in data["tracks"] if t["guide_id"] == id]
    tracks.sort(key=lambda x: x["order_num"])
    
    return templates.TemplateResponse(
        request=request,
        name="guides.html",
        context={"guide": guide, "tracks": tracks}
    )

@app.get("/guides/")
async def list_guides():
    data = load_data()
    return {"guides": data["guides"]}

@app.delete("/guides/{id}")
async def delete_guide(id: int):
    data = load_data()
    
    # First check if guide exists
    guide = next((g for g in data["guides"] if g["id"] == id), None)
    if not guide:
        raise HTTPException(status_code=404, detail="Guide not found")
    
    # Delete tracks first
    data["tracks"] = [t for t in data["tracks"] if t["guide_id"] != id]
    
    # Then delete the guide
    data["guides"] = [g for g in data["guides"] if g["id"] != id]
    
    save_data(data)
    return {"message": f"Guide {id} and its tracks deleted successfully"}

#endpoints for tracks
# Get tracks for a specific guide 
@app.get("/guides/{guide_id}/tracks")
async def get_guide_tracks(guide_id: int):
    data = load_data()
    tracks = [t for t in data["tracks"] if t["guide_id"] == guide_id]
    tracks.sort(key=lambda x: x["order_num"])
    return {"tracks": tracks}

# Stream audio file 
@app.get("/tracks/{track_id}/audio")
async def stream_audio(track_id: int):
    data = load_data()
    track = next((t for t in data["tracks"] if t["id"] == track_id), None)
    
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    
    return FileResponse(track["file_path"], media_type="audio/mpeg")