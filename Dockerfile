FROM python:3.12-slim

WORKDIR /app

# Copy everything
COPY . /app

# Install dependencies (make sure you have a requirements.txt)
RUN pip install --no-cache-dir -r requirements.txt

# Run your FastAPI app on port 8080
CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "8080"]
