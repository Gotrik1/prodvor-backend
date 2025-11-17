from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.base import CRUDBase
from app.models.team import Team
from app.models.team_application import TeamApplication
from app.models.user_team import UserTeam
from app.models.subscription import Subscription
from app.schemas.team import TeamCreate, TeamUpdate
from fastapi import HTTPException
from sqlalchemy import delete, select, and_
from sqlalchemy.orm import selectinload
from typing import Any, List, Optional


class CRUDTeam(CRUDBase[Team, TeamCreate, TeamUpdate]):
    async def get(self, db: AsyncSession, id: Any) -> Optional[Team]:
        query = select(self.model).where(self.model.id == id).options(
            selectinload(self.model.member_associations).selectinload(UserTeam.user)
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[Team]:
        query = select(self.model).offset(skip).limit(limit).options(
            selectinload(self.model.member_associations).selectinload(UserTeam.user)
        )
        result = await db.execute(query)
        return result.scalars().unique().all()
    
    async def create_with_owner(self, db: AsyncSession, *, obj_in: TeamCreate, owner_id: UUID) -> Team:
        """ 
        Создает команду и делает пользователя владельцем
        """
        db_obj = self.model(**obj_in.dict(), owner_id=owner_id)
        db.add(db_obj)
        await db.commit()

        # Add owner as a team member
        owner_member = UserTeam(user_id=owner_id, team_id=db_obj.id)
        db.add(owner_member)
        await db.commit()

        # Re-fetch the team with members eagerly loaded to satisfy the response_model and avoid MissingGreenlet
        query = select(Team).where(Team.id == db_obj.id).options(
            selectinload(Team.member_associations).selectinload(UserTeam.user)
        )
        result = await db.execute(query)
        return result.scalar_one()

    async def apply(self, db: AsyncSession, *, team_id: UUID, user_id: UUID):
        # Проверяем, что команда существует
        team = await self.get(db, team_id)
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
        
        # Проверяем, что пользователь уже не в команде
        member_query = await db.execute(select(UserTeam).where(UserTeam.team_id == team_id, UserTeam.user_id == user_id))
        if member_query.scalars().first():
            raise HTTPException(status_code=400, detail="User is already in the team")

        # Проверяем, что пользователь еще не подал заявку
        application_query = await db.execute(select(TeamApplication).where(TeamApplication.team_id == team_id, TeamApplication.user_id == user_id))
        if application_query.scalars().first():
            raise HTTPException(status_code=400, detail="User has already applied to the team")

        # Создаем заявку
        application = TeamApplication(team_id=team_id, user_id=user_id)
        db.add(application)
        await db.commit()

    async def list_applications(self, db: AsyncSession, *, team_id: UUID, owner_id: UUID):
        team = await self.get(db, team_id)
        if not team or team.owner_id != owner_id:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        applications_query = await db.execute(select(TeamApplication).where(TeamApplication.team_id == team_id).options(selectinload(TeamApplication.user)))
        return applications_query.scalars().all()

    async def accept(self, db: AsyncSession, *, team_id: UUID, owner_id: UUID, user_id: UUID):
        team = await self.get(db, team_id)
        if not team or team.owner_id != owner_id:
            raise HTTPException(status_code=403, detail="Not authorized")

        # Находим и удаляем заявку
        application_query = await db.execute(select(TeamApplication).where(TeamApplication.team_id == team_id, TeamApplication.user_id == user_id))
        application = application_query.scalars().first()
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")
        
        await db.delete(application)

        # Добавляем в команду
        new_member = UserTeam(team_id=team_id, user_id=user_id)
        db.add(new_member)
        await db.commit()

    async def decline(self, db: AsyncSession, *, team_id: UUID, owner_id: UUID, user_id: UUID):
        team = await self.get(db, team_id)
        if not team or team.owner_id != owner_id:
            raise HTTPException(status_code=403, detail="Not authorized")

        # Находим и удаляем заявку
        application_query = await db.execute(select(TeamApplication).where(TeamApplication.team_id == team_id, TeamApplication.user_id == user_id))
        application = application_query.scalars().first()
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")
        
        await db.delete(application)
        await db.commit()

    async def update_logo(self, db: AsyncSession, *, team_id: UUID, owner_id: UUID, logo_url: str) -> Team:
        team = await self.get(db, team_id)
        if not team or team.owner_id != owner_id:
            raise HTTPException(status_code=403, detail="Not authorized")

        team.logoUrl = logo_url
        await db.commit()
        await db.refresh(team)
        return team

    async def remove_member(self, db: AsyncSession, *, team_id: UUID, owner_id: UUID, user_id: UUID):
        team = await self.get(db, team_id)
        if not team or team.owner_id != owner_id:
            raise HTTPException(status_code=403, detail="Not authorized to remove members")

        if owner_id == user_id:
            raise HTTPException(status_code=400, detail="Owner cannot remove themselves")

        # Находим и удаляем участника
        member_query = await db.execute(delete(UserTeam).where(UserTeam.team_id == team_id, UserTeam.user_id == user_id))
        if member_query.rowcount == 0:
            raise HTTPException(status_code=404, detail="Member not found in the team")
            
        await db.commit()

    async def toggle_follow(self, db: AsyncSession, *, team_id: UUID, user_id: UUID) -> bool:
        result = await db.execute(
            select(Subscription).where(
                Subscription.user_id == user_id, Subscription.team_id == team_id
            )
        )
        subscription = result.scalar_one_or_none()

        if subscription:
            await db.delete(subscription)
            await db.commit()
            return False
        else:
            new_sub = Subscription(user_id=user_id, team_id=team_id)
            db.add(new_sub)
            await db.commit()
            return True

team = CRUDTeam(Team)
