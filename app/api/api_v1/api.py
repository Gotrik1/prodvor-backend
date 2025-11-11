from fastapi import APIRouter

from app.api.api_v1.endpoints import (
    event,
    sport,
    team,
    user,
    user_event,
    user_team,
    sport_event,
    team_event,
    user_favorite_sport,
    login
)

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(user.router, prefix="/users", tags=["users"])
api_router.include_router(team.router, prefix="/teams", tags=["teams"])
api_router.include_router(event.router, prefix="/events", tags=["events"])
api_router.include_router(sport.router, prefix="/sports", tags=["sports"])
api_router.include_router(user_event.router, prefix="/user_events", tags=["user_events"])
api_router.include_router(user_team.router, prefix="/user_teams", tags=["user_teams"])
api_router.include_router(sport_event.router, prefix="/sport_events", tags=["sport_events"])
api_router.include_router(team_event.router, prefix="/team_events", tags=["team_events"])
api_router.include_router(
    user_favorite_sport.router, prefix="/user_favorite_sports", tags=["user_favorite_sports"]
)
