# app/db/base.py
from .base_class import Base

# Импорт ВСЕХ моделей, чтобы они были зарегистрированы в Base.metadata
from app.models.user import User
from app.models.team import Team
from app.models.post import Post
from app.models.comment import Comment
from app.models.sport import Sport
from app.models.playground import Playground
from app.models.achievement import Achievement
from app.models.coach_profile import CoachProfile
from app.models.event import Event
from app.models.friend_request import FriendRequest
from app.models.invitation import Invitation
from app.models.like import Like
from app.models.looking_for_game import LookingForGame
from app.models.notification import Notification
from app.models.player_profile import PlayerProfile
from app.models.quest import Quest
from app.models.referee_profile import RefereeProfile
from app.models.session import Session
from app.models.sponsor import Sponsor
from app.models.sport_event import SportEvent
from app.models.subscription import Subscription
from app.models.team_application import TeamApplication
from app.models.team_event import TeamEvent
from app.models.team_season_stats import TeamSeasonStats
from app.models.tournament import Tournament
from app.models.user_event import UserEvent
from app.models.user_favorite_sport import UserFavoriteSport
from app.models.user_privacy_settings import UserPrivacySettings
from app.models.user_settings import UserSettings
from app.models.user_team import UserTeam
