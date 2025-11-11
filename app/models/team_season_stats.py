import uuid
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.db.base_class import Base

class TeamSeasonStats(Base):
    __tablename__ = 'team_season_stats'
    teamId = Column(UUID(as_uuid=True), ForeignKey('teams.id'), primary_key=True, nullable=False)
    season = Column(Integer, primary_key=True, nullable=False)
    leagueRank = Column(String(50))
    finalElo = Column(Integer)
    wins = Column(Integer)
    losses = Column(Integer)
