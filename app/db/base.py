# Import all the models, so that Base has them before being
# imported by Alembic
from app.db.base_class import Base  # noqa
from app.models.user import User  # noqa
from app.models.team import Team # noqa
from app.models.notification import Notification # noqa
from app.models.coach_profile import CoachProfile # noqa
from app.models.player_profile import PlayerProfile # noqa
from app.models.referee_profile import RefereeProfile # noqa
from app.models.session import Session # noqa
from app.models.sport import Sport # noqa
from app.models.achievement import Achievement # noqa
from app.models.user_settings import UserSettings # noqa
from app.models.user_privacy_settings import UserPrivacySettings # noqa
from app.models.friend_request import FriendRequest # noqa
from app.models.post import Post # noqa
from app.models.comment import Comment # noqa
from app.models.playground import Playground # noqa
from app.models.quest import Quest # noqa
from app.models.sponsor import Sponsor # noqa
from app.models.team_application import TeamApplication # noqa
from app.models.team_season_stats import TeamSeasonStats # noqa
from app.models.tournament import Tournament # noqa
from app.models.looking_for_game import LookingForGame # noqa
