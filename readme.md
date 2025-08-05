# 🚀 Museum Audio Guide Platform

<div align="center">

  
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Jinja2](https://img.shields.io/badge/Jinja2-B41717?style=for-the-badge&logo=jinja&logoColor=white)

*A lightweight, server-driven audio guide platform built for seamless audio playback*

</div>

## 📋 Overview

This project demonstrates a lean audio guide platform using **FastAPI** and **Jinja2** for server-side rendering. The architecture prioritizes performance and simplicity, eliminating unnecessary JavaScript overhead while providing smooth audio playback functionality.

## 🏗️ Architecture Decisions

### Server-Side Rendering Choice
- **FastAPI + Jinja2**: Chosen for direct template rendering without client-side complexity
- **No JavaScript framework**: Avoids abstraction layers and reduces bundle size
- **Server-driven**: Data is populated directly into templates, eliminating additional HTTP requests

### Database Design
The relational model facilitates efficient data relationships and clean population patterns:

```python
class Guide(Base):
    __tablename__ = "guides"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(String(300), nullable=False)
    category: Mapped[str] = mapped_column(nullable=False)
    tracks: Mapped[List["Track"]] = relationship(back_populates="guide")

class Track(Base):
    __tablename__ = "tracks"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(50), nullable=False)
    file_path: Mapped[str] = mapped_column(nullable=False)
    duration: Mapped[float] = mapped_column(nullable=False)
    order_num: Mapped[int] = mapped_column(nullable=False)
    guide_id: Mapped[int] = mapped_column(ForeignKey("guides.id"))
    guide: Mapped["Guide"] = relationship(back_populates="tracks")
```

## 🎵 Audio Handling Strategy

**Metadata Storage**: Audio file paths are stored in the database rather than binary data, optimizing for:
- **Performance**: Eliminates large blob storage overhead
- **Scalability**: Maintains efficient database operations
- **Flexibility**: Supports various audio formats and external storage solutions

**Streaming Endpoint**: Direct file serving through FastAPI's `FileResponse`
```python
@app.get("/tracks/{track_id}/audio")
async def stream_audio(track_id: int):
    track = await database.fetch_one(track_query)
    return FileResponse(track["file_path"], media_type="audio/mpeg")
```

## 🎯 Key Features

- **Direct Template Rendering**: No API layer needed for basic operations
- **Efficient Relationships**: One-to-many Guide↔Track relationship with proper foreign keys
- **Audio Streaming**: Direct file serving with proper MIME types
- **Clean Separation**: Models, schemas, and routes properly organized

## 🔄 Jinja vs JavaScript Comparison

### Jinja Template (Server-Side)
```html
<div class="track-list">
    {% for track in tracks %}
    <div class="track-item">
        <div class="track-header">
            <span class="track-number">{{ track.order_num }}</span>
            <h3 class="track-title">{{ track.title }}</h3>
        </div>
        <div class="audio-player">
            <audio controls preload="none">
                <source src="/tracks/{{ track.id }}/audio" type="audio/mpeg">
            </audio>
        </div>
    </div>
    {% endfor %}
</div>
```

### JavaScript Alternative (Client-Side)
```html
<div id="track-list" class="track-list"></div>
<script>
  const tracks = await fetch('/api/tracks').then(r => r.json());
  const trackList = document.getElementById("track-list");
  
  tracks.forEach(track => {
    const trackItem = document.createElement("div");
    trackItem.className = "track-item";
    trackItem.innerHTML = `
      <div class="track-header">
        <span class="track-number">${track.order_num}</span>
        <h3 class="track-title">${track.title}</h3>
      </div>
      <div class="audio-player">
        <audio controls preload="none">
          <source src="/tracks/${track.id}/audio" type="audio/mpeg">
        </audio>
      </div>
    `;
    trackList.appendChild(trackItem);
  });
</script>
```

**Why Jinja Wins**: Less code, no DOM manipulation, no additional HTTP requests, and data is available immediately on page load.


## 📸 Screenshots

### Home Page
![Home Page](screenshots/home.png)

### Audio Guide - Sokoto Exhibit
![Sokoto Guide](screenshots/sokoto.png)

### Audio Guide - Tang Dynasty Exhibit  
![Tang Guide](screenshots/tang.png)

## 🛠️ Tech Stack

- **Backend**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy
- **Templates**: Jinja2
- **Audio**: HTML5 Audio API
- **Styling**: Static CSS files

## 📁 Project Structure

```
├── main.py              # FastAPI application and routes
├── models.py            # SQLAlchemy database models
├── schemas.py           # Pydantic schemas for validation
├── templates/           # Jinja2 HTML templates
├── static/             # CSS and static assets
├── screenshots/        # Application screenshots
└── audio_files/        # Audio file storage
```

---

*This project demonstrates practical audio streaming implementation with modern Python web frameworks, optimized for performance and maintainability.*