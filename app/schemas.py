from pydantic import BaseModel

class GuideCreate(BaseModel):
    title: str
    description: str
    category: str

class TrackCreate(BaseModel):
    title: str
    file_path: str
    duration: float
    order_num: int
