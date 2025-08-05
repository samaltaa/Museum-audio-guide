from pydantic import BaseModel
from typing import List, Optional

class TrackCreate(BaseModel):
    title: str
    file_path: str
    duration: float
    order_num: int

class GuideCreate(BaseModel):
    title: str
    description: str
    category: str
    tracks: Optional[List[TrackCreate]] = None
