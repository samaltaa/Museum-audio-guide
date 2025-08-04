from typing import List 
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Guide(Base):
    __tablename__ = "guides"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    title: Mapped[str] = mapped_column (String(50), nullable=False)
    description: Mapped[str] = mapped_column(String(300), nullable=False)
    category: Mapped[str] = mapped_column(nullable=False)

    tracks: Mapped[List["Track"]] = relationship(back_populates="guide")

class Track(Base):
    __tablename__ = "tracks"

    id: Mapped[int] = mapped_column(autoincrement=False)
    title: Mapped[str] = mapped_column(String(50), nullable=False)
    file_path: Mapped[str] = mapped_column(nullable=False)
    duration: Mapped[float] = mapped_column(nullable=False)
    order_num: Mapped[int] = mapped_column(nullable=False)

    guide_id: Mapped[int] = ForeignKey("guides.id")
    guide: Mapped["Guide"] = relationship(back_populates="tracks")