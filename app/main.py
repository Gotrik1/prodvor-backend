from fastapi import FastAPI
from app.routers import auth

app = FastAPI()

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])

@app.get("/healthz", tags=["Health"])
def healthz():
    return {"message": "OK"}
