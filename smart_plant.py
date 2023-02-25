from app import settings, create_app
import uvicorn
from pathlib import Path

app = create_app()

if __name__ == "__main__":
    uvicorn.run(f"{Path(__file__).stem}:app", host=settings.WSGI_HOST, port=settings.WSGI_PORT, reload=settings.RELOAD)