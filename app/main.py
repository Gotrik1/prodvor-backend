from fastapi import FastAPI, Request, HTTPException
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from app.routers import (users, teams, sports, auth, sponsors, playgrounds, posts, comments, like, invitation, friend_request, lfg, subscriptions)
from app.core.config import settings
from fastapi.openapi.utils import get_openapi
import copy

class LimitRequestSizeMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_size: int):
        super().__init__(app)
        self.max_size = max_size

    async def dispatch(self, request: Request, call_next):
        content_length = request.headers.get('Content-Length')
        if content_length and int(content_length) > self.max_size:
            raise HTTPException(413, detail="Request body is too large")
        return await call_next(request)


app = FastAPI(title=settings.PROJECT_NAME)
app.openapi_version = "3.1.0"

# Add the middleware with a 1MB size limit
app.add_middleware(LimitRequestSizeMiddleware, max_size=1_000_000) 


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, specify your frontend's domain
    allow_credentials=True,
    allow_methods=["*"]
)

def _dev_patch_openapi(doc: dict) -> dict:
     import copy
     def fix_node(node):
         if isinstance(node, dict):
             # anyOf [X, null] -> nullable, формат не трогаем
             if "anyOf" in node:
                 types = [x.get("type") for x in node["anyOf"] if isinstance(x, dict)]
                 if "null" in types:
                     base = next((x for x in node["anyOf"] if x.get("type") != "null"), None)
                     if base:
                         node.pop("anyOf", None)
                         node.update({k: v for k, v in base.items()})
                         node["nullable"] = True
             # ↓ Больше ничего не трогаем: format: uuid остаётся
             for v in list(node.values()):
                 fix_node(v)
         elif isinstance(node, list):
             for v in node: fix_node(v)
     new_doc = copy.deepcopy(doc)
     fix_node(new_doc)
     return new_doc

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(title=settings.PROJECT_NAME, version="1.0.0",
                         description="Prodvor API", routes=app.routes)
    app.openapi_schema = _dev_patch_openapi(schema)
    return app.openapi_schema

app.openapi = custom_openapi


@app.get("/")
def read_root():
    return {"message": "Welcome to Prodvor API"}

@app.get("/health", tags=["healthcheck"])
def health_check():
    """
    Checks if the server is running.
    """
    return {"status": "ok"}

app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(teams.router, prefix="/api/v1/teams", tags=["teams"])
app.include_router(sports.router, prefix="/api/v1/sports", tags=["sports"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(sponsors.router, prefix="/api/v1/sponsors", tags=["sponsors"])
app.include_router(playgrounds.router, prefix="/api/v1/playgrounds", tags=["playgrounds"])
app.include_router(posts.router, prefix="/api/v1/posts", tags=["posts"])
app.include_router(comments.router, prefix="/api/v1/comments", tags=["comments"])
app.include_router(like.router, prefix="/api/v1/likes", tags=["likes"])
app.include_router(invitation.router, prefix="/api/v1/invitations", tags=["invitations"])
app.include_router(friend_request.router, prefix="/api/v1/friend-requests", tags=["friend-requests"])
app.include_router(lfg.router, prefix="/api/v1/lfg", tags=["lfg"])
app.include_router(subscriptions.router, prefix="/api/v1/subscriptions", tags=["subscriptions"])
