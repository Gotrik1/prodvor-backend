
# app/main.py
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from app.core.config import settings
from app.routers import (
    auth,
    comment,
    friend_request,
    invitation,
    lfg,
    like,
    playgrounds,
    posts,
    sponsors,
    sports,
    subscriptions,
    teams,
    users,
)
from app.schemas.generic import Msg, Status

app = FastAPI(title=settings.PROJECT_NAME)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Создание основного роутера
api_router = APIRouter()

# Подключение роутеров
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(comment.router, prefix="/comments", tags=["comments"])
api_router.include_router(friend_request.router, prefix="/friend-requests", tags=["friend-requests"])
api_router.include_router(invitation.router, prefix="/invitations", tags=["invitations"])
api_router.include_router(lfg.router, prefix="/lfg", tags=["lfg"])
api_router.include_router(like.router, prefix="/likes", tags=["likes"])
api_router.include_router(playgrounds.router, prefix="/playgrounds", tags=["playgrounds"])
api_router.include_router(posts.router, prefix="/posts", tags=["posts"])
api_router.include_router(sponsors.router, prefix="/sponsors", tags=["sponsors"])
api_router.include_router(sports.router, prefix="/sports", tags=["sports"])
api_router.include_router(subscriptions.router, prefix="/subscriptions", tags=["subscriptions"])
api_router.include_router(teams.router, prefix="/teams", tags=["teams"])
api_router.include_router(users.router, prefix="/users", tags=["users"])

app.include_router(api_router, prefix="/api/v1")

@app.get("/", response_model=Msg)
def read_root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}

@app.get("/health", response_model=Status)
def health_check():
    return {"status": "ok"}

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=settings.PROJECT_NAME,
        version="1.0.0",
        description="Here's a description of the API",
        routes=app.routes,
    )
    # This part is for modifying the OpenAPI schema
    for schema in openapi_schema["components"]["schemas"].values():
        if "properties" in schema:
            for prop, value in schema["properties"].items():
                # Fix for Optional fields being represented as anyOf
                if "anyOf" in value:
                    types = [v["type"] for v in value["anyOf"] if "type" in v]
                    if "null" in types:
                        value["nullable"] = True
                        # Remove the null type from anyOf and get the first other type
                        non_null_types = [t for t in value["anyOf"] if t.get("type") != "null"]
                        if non_null_types:
                            value.update(non_null_types[0])
                        del value["anyOf"]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
