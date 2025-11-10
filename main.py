
from fastapi import FastAPI
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

@app.get("/healthz", tags=["healthcheck"])
async def root():
    return {"message": "OK"}
