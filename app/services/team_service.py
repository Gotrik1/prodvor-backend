
from sqlalchemy.ext.asyncio import AsyncSession
from app import crud, models, schemas
from fastapi import HTTPException
from pydantic import UUID4

class TeamService:
    async def get_teams(self, db: AsyncSession, *, skip: int, limit: int) -> list[models.Team]:
        return await crud.team.get_multi(db, skip=skip, limit=limit)

    async def create_team(self, db: AsyncSession, *, team_in: schemas.TeamCreate, owner_id: UUID4) -> models.Team:
        return await crud.team.create_with_owner(db, obj_in=team_in, owner_id=owner_id)

    async def get_team(self, db: AsyncSession, *, team_id: UUID4) -> models.Team:
        team = await crud.team.get(db, id=team_id)
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
        return team

    async def list_applications(self, db: AsyncSession, *, team_id: UUID4, owner_id: UUID4):
        applications = await crud.team.list_applications(db, team_id=team_id, owner_id=owner_id)
        return [app.user for app in applications]

    async def respond_to_application(self, db: AsyncSession, *, team_id: UUID4, user_id: UUID4, owner_id: UUID4, action: str):
        if action == "accept":
            await crud.team.accept(db, team_id=team_id, owner_id=owner_id, user_id=user_id)
            return {"message": "Player accepted"}
        else:
            await crud.team.decline(db, team_id=team_id, owner_id=owner_id, user_id=user_id)
            return {"message": "Player declined"}

    async def apply_to_team(self, db: AsyncSession, *, team_id: UUID4, user_id: UUID4):
        await crud.team.apply(db, team_id=team_id, user_id=user_id)

    async def toggle_team_follow(self, db: AsyncSession, *, team_id: UUID4, user_id: UUID4) -> bool:
        team = await crud.team.get(db, id=team_id)
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")

        return await crud.subscription.toggle(
            db=db,
            user_id=user_id,
            team_id=team_id,
        )

    async def update_team_logo(self, db: AsyncSession, *, team_id: UUID4, owner_id: UUID4, logo_url: str):
        team = await crud.team.update_logo(
            db,
            team_id=team_id,
            owner_id=owner_id,
            logo_url=logo_url
        )
        if not team:
            raise HTTPException(status_code=404, detail="Team not found or user is not the owner")
        return team

    async def remove_team_member(self, db: AsyncSession, *, team_id: UUID4, owner_id: UUID4, user_id: UUID4):
        await crud.team.remove_member(db, team_id=team_id, owner_id=owner_id, user_id=user_id)

team_service = TeamService()
