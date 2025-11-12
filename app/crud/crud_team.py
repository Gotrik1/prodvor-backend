from typing import Tuple, List, Optional
from app.crud.base import CRUDBase
from app.models.team import Team, team_followers
from app.models.user import User
from app.models.user_team import UserTeam 
from app.schemas.team import TeamCreate, TeamUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, and_
import uuid

class CRUDTeam(CRUDBase[Team, TeamCreate, TeamUpdate]):
    async def create_with_captain(self, db: AsyncSession, *, obj_in: TeamCreate, captain_id: uuid.UUID) -> Team:
        team_data = obj_in.model_dump()
        new_team = self.model(
            name=team_data['name'], 
            sport_id=team_data['sport_id'],
            captain_id=captain_id, 
            city=team_data.get('city'), 
            game=team_data.get('game')
        )
        db.add(new_team)
        await db.commit()
        await db.refresh(new_team)
        return new_team

    async def get_followed_teams_with_total(self, db: AsyncSession, *, user_id: uuid.UUID, skip: int = 0, limit: int = 10) -> Tuple[List[Team], int]:
        total_query = select(func.count()).select_from(team_followers).where(team_followers.c.user_id == user_id)
        total_result = await db.execute(total_query)
        total = total_result.scalar_one()

        if total == 0:
            return [], 0

        followed_team_ids_query = select(team_followers.c.team_id).where(team_followers.c.user_id == user_id).offset(skip).limit(limit)
        followed_team_ids_result = await db.execute(followed_team_ids_query)
        followed_team_ids = followed_team_ids_result.scalars().all()

        if not followed_team_ids:
            return [], total

        teams_query = select(Team).where(Team.id.in_(followed_team_ids))
        teams_result = await db.execute(teams_query)
        teams = teams_result.scalars().all()
        return teams, total

    async def apply(self, db: AsyncSession, *, team_id: uuid.UUID, user_id: uuid.UUID):
        pass

    async def list_applications(self, db: AsyncSession, *, team_id: uuid.UUID, captain_id: uuid.UUID) -> List[User]:
        return []

    async def accept(self, db: AsyncSession, *, team_id: uuid.UUID, captain_id: uuid.UUID, user_id: uuid.UUID):
        pass

    async def decline(self, db: AsyncSession, *, team_id: uuid.UUID, captain_id: uuid.UUID, user_id: uuid.UUID):
        pass

    async def update_logo(self, db: AsyncSession, *, team_id: uuid.UUID, captain_id: uuid.UUID, logo_url: str) -> Optional[Team]:
        team = await self.get(db, id=team_id)
        if team and team.captain_id == captain_id:
            team.logoUrl = logo_url
            await db.commit()
            await db.refresh(team)
            return team
        return None

    async def remove_member(self, db: AsyncSession, *, team_id: uuid.UUID, captain_id: uuid.UUID, user_id: uuid.UUID):
        team = await self.get(db, id=team_id)
        if not team or team.captain_id != captain_id:
            return
        
        if captain_id == user_id:
            return

        stmt = UserTeam.__table__.delete().where(
            and_(UserTeam.team_id == team_id, UserTeam.user_id == user_id)
        )
        await db.execute(stmt)
        await db.commit()


team = CRUDTeam(Team)
