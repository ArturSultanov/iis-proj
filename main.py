import uvicorn
from app import app
from app.config import settings

if __name__ == "__main__":
    uvicorn.run(app, host=settings.WEB_HOST, port=settings.WEB_PORT)