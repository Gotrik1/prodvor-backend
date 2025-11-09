
import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from . import db

# --- Связующие таблицы ---

TeamMembers = db.Table('team_members',
    db.Column('userId', UUID(as_uuid=True), db.ForeignKey('user.id'), primary_key=True),
    db.Column('teamId', UUID(as_uuid=True), db.ForeignKey('team.id'), primary_key=True)
)

TeamFollowers = db.Table('team_followers',
    db.Column('userId', UUID(as_uuid=True), db.ForeignKey('user.id'), primary_key=True),
    db.Column('teamId', UUID(as_uuid=True), db.ForeignKey('team.id'), primary_key=True)
)

UserSports = db.Table('user_sports',
    db.Column('userId', UUID(as_uuid=True), db.ForeignKey('user.id'), primary_key=True),
    db.Column('sportId', db.String, db.ForeignKey('sport.id'), primary_key=True)
)

class UserAchievement(db.Model):
    __tablename__ = 'user_achievements'
    userId = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'), primary_key=True)
    achievementId = db.Column(UUID(as_uuid=True), db.ForeignKey('achievement.id'), primary_key=True)
    unlockedAt = db.Column(db.DateTime(timezone=True), server_default=func.now())

    achievement = db.relationship('Achievement')

Friendship = db.Table('friendships',
    db.Column('user_id', UUID(as_uuid=True), db.ForeignKey('user.id'), primary_key=True),
    db.Column('friend_id', UUID(as_uuid=True), db.ForeignKey('user.id'), primary_key=True)
)

UserFollows = db.Table('user_follows',
    db.Column('follower_id', UUID(as_uuid=True), db.ForeignKey('user.id'), primary_key=True),
    db.Column('followed_id', UUID(as_uuid=True), db.ForeignKey('user.id'), primary_key=True)
)

class FriendRequest(db.Model):
    __tablename__ = 'friend_requests'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    from_user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'), nullable=False)
    to_user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='pending', nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    __table_args__ = (db.UniqueConstraint('from_user_id', 'to_user_id', name='_from_to_uc'),)

# --- Модели настроек ---

class UserSettings(db.Model):
    __tablename__ = 'user_settings'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'), nullable=False, unique=True)
    theme = db.Column(db.String(50), default='light')
    language = db.Column(db.String(10), default='en')

    def to_dict(self):
        return {
            "theme": self.theme,
            "language": self.language
        }

class UserPrivacySettings(db.Model):
    __tablename__ = 'user_privacy_settings'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'), nullable=False, unique=True)
    profile_visibility = db.Column(db.String(50), default='all')
    teams_visibility = db.Column(db.String(50), default='all')
    messages_privacy = db.Column(db.String(50), default='friends')

    def to_dict(self):
        return {
            "profile_visibility": self.profile_visibility,
            "teams_visibility": self.teams_visibility,
            "messages_privacy": self.messages_privacy
        }

# --- Основные модели ---

class User(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = db.Column(db.String(120), unique=True, nullable=False)
    nickname = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    firstName = db.Column(db.String(100), nullable=True)
    lastName = db.Column(db.String(100), nullable=True)
    birthDate = db.Column(db.DateTime, nullable=True)
    avatarUrl = db.Column(db.String(255), nullable=True)
    coverImageUrl = db.Column(db.String(255), nullable=True)
    role = db.Column(db.String(50), nullable=False)
    city = db.Column(db.String(100), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    gender = db.Column(db.String(50), nullable=True)
    phone = db.Column(db.String(50), nullable=True, unique=True)
    bio = db.Column(db.Text, nullable=True)
    elo = db.Column(db.Integer, default=1200)

    # Связи
    player_profile = db.relationship('PlayerProfile', backref='user', uselist=False, cascade="all, delete-orphan")
    referee_profile = db.relationship('RefereeProfile', backref='user', uselist=False, cascade="all, delete-orphan")
    coach_profile = db.relationship('CoachProfile', backref='user', uselist=False, cascade="all, delete-orphan")
    posts = db.relationship('Post', backref='author', lazy=True)
    comments = db.relationship('Comment', backref='author', lazy=True)
    teams = db.relationship('Team', secondary=TeamMembers, backref=db.backref('members', lazy='dynamic'))
    sports = db.relationship('Sport', secondary=UserSports, backref=db.backref('users', lazy='dynamic'))
    unlockedAchievements = db.relationship('UserAchievement', backref='user', cascade="all, delete-orphan")
    settings = db.relationship('UserSettings', backref='user', uselist=False, cascade="all, delete-orphan")
    privacy_settings = db.relationship('UserPrivacySettings', backref='user', uselist=False, cascade="all, delete-orphan")

    followingTeams = db.relationship('Team', secondary=TeamFollowers, backref=db.backref('followers', lazy='dynamic'))
    friends = db.relationship('User',
                              secondary=Friendship,
                              primaryjoin=(Friendship.c.user_id == id),
                              secondaryjoin=(Friendship.c.friend_id == id),
                              lazy='dynamic')
    followingUsers = db.relationship('User', 
                                 secondary=UserFollows,
                                 primaryjoin=(UserFollows.c.follower_id == id),
                                 secondaryjoin=(UserFollows.c.followed_id == id),
                                 backref=db.backref('followers', lazy='dynamic'), 
                                 lazy='dynamic')

    def to_summary_dict(self):
        return {
            "id": self.id,
            "nickname": self.nickname,
            "avatarUrl": self.avatarUrl
        }

    def to_dict(self, include_teams=False, include_sports=True, profile_buttons=None, include_settings=False):
        data = {
            "id": self.id,
            "email": self.email,
            "nickname": self.nickname,
            "firstName": self.firstName,
            "lastName": self.lastName,
            "birthDate": self.birthDate.isoformat() if self.birthDate else None,
            "avatarUrl": self.avatarUrl,
            "coverImageUrl": self.coverImageUrl,
            "role": self.role,
            "city": self.city,
            "age": self.age,
            "gender": self.gender,
            "phone": self.phone,
            "bio": self.bio,
            "elo": self.elo
        }
        
        if self.player_profile:
            data['player_profile'] = self.player_profile.to_dict()
        else:
            # Если профиля игрока нет, создаем его со значениями по-умолчанию
            data['player_profile'] = PlayerProfile().to_dict()


        if include_teams:
            data['teams'] = [team.to_dict() for team in self.teams]
        if include_sports:
            data['sports'] = [sport.to_dict() for sport in self.sports]

        data['unlockedAchievements'] = [ua.achievement.id for ua in self.unlockedAchievements]

        data['counters'] = {
            "friends": self.friends.count(),
            "followers": self.followers.count(),
            "followingUsers": self.followingUsers.count(),
            "followingTeams": len(self.followingTeams)
        }

        if profile_buttons is not None:
            data['profile_buttons'] = profile_buttons

        if include_settings:
            data['settings'] = self.settings.to_dict() if self.settings else UserSettings().to_dict()
            data['privacy'] = self.privacy_settings.to_dict() if self.privacy_settings else UserPrivacySettings().to_dict()
            
        return data

class Team(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(120), nullable=False)
    logoUrl = db.Column(db.String(200))
    captainId = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'), nullable=False)
    sportId = db.Column(db.String, db.ForeignKey('sport.id')) 
    rank = db.Column(db.Integer, default=1200)
    city = db.Column(db.String(100))
    wins = db.Column(db.Integer, default=0)
    losses = db.Column(db.Integer, default=0)
    leagueRank = db.Column(db.String(50))
    currentStreakType = db.Column(db.String(1))
    currentStreakCount = db.Column(db.Integer)
    form = db.Column(db.String(5))
    mvpPlayerId = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'))
    topScorerPlayerId = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'))
    cleanSheets = db.Column(db.Integer, default=0)
    avgRating = db.Column(db.Integer, default=0)
    createdAt = db.Column(db.DateTime(timezone=True), server_default=func.now())
    
    posts = db.relationship('Post', backref='team', lazy=True)
    captain = db.relationship('User', foreign_keys=[captainId])
    sport = db.relationship('Sport')

    def to_summary_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "logoUrl": self.logoUrl
        }

    def to_dict(self, include_members=False):
        data = {
            "id": self.id,
            "name": self.name,
            "logoUrl": self.logoUrl,
            "captainId": self.captainId,
            "rank": self.rank,
            "city": self.city,
            "wins": self.wins,
            "losses": self.losses,
            "leagueRank": self.leagueRank,
            "currentStreakType": self.currentStreakType,
            "currentStreakCount": self.currentStreakCount,
            "form": self.form,
            "mvpPlayerId": self.mvpPlayerId,
            "topScorerPlayerId": self.topScorerPlayerId,
            "cleanSheets": self.cleanSheets,
            "avgRating": self.avgRating,
            "createdAt": self.createdAt.isoformat()
        }
        if self.sport:
            data['sport'] = self.sport.to_dict()
            
        if include_members:
            data['members'] = [member.to_dict() for member in self.members]
            data['captain'] = self.captain.to_dict() if self.captain else None
        return data

class PlayerProfile(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    userId = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'), unique=True, nullable=False)
    matchesPlayed = db.Column(db.Integer, default=0)
    wins = db.Column(db.Integer, default=0)
    goals = db.Column(db.Integer, default=0)
    assists = db.Column(db.Integer, default=0)
    mvpAwards = db.Column(db.Integer, default=0)

    def to_dict(self):
        # We can get the elo from the user model directly
        user = User.query.get(self.userId)
        elo = user.elo if user else 1200

        return {
            "matchesPlayed": self.matchesPlayed,
            "wins": self.wins,
            "goals": self.goals,
            "assists": self.assists,
            "mvpAwards": self.mvpAwards,
            "elo": elo
        }


class RefereeProfile(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    userId = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'), unique=True, nullable=False)
    category = db.Column(db.String(50))
    matchesJudged = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            "category": self.category,
            "matchesJudged": self.matchesJudged
        }


class CoachProfile(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    userId = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'), unique=True, nullable=False)
    specialization = db.Column(db.String(150))
    experienceYears = db.Column(db.Integer)

    def to_dict(self):
        return {
            "specialization": self.specialization,
            "experienceYears": self.experienceYears
        }

class Tournament(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(150), nullable=False)
    game = db.Column(db.String(100))
    status = db.Column(db.String(50))
    prizePool = db.Column(db.String(100))
    participants = db.Column(db.Integer, default=0)
    maxParticipants = db.Column(db.Integer)
    startDate = db.Column(db.String(100))

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "game": self.game,
            "status": self.status,
            "prizePool": self.prizePool,
            "participants": self.participants,
            "maxParticipants": self.maxParticipants,
            "startDate": self.startDate
        }

class Post(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    authorId = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'), nullable=False)
    teamId = db.Column(UUID(as_uuid=True), db.ForeignKey('team.id'))
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime(timezone=True), server_default=func.now())
    
    comments = db.relationship('Comment', backref='post', lazy='dynamic', cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'author': self.author.to_dict(),
            'teamId': self.teamId,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'comments': [comment.to_dict() for comment in self.comments]
        }

class Comment(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    postId = db.Column(UUID(as_uuid=True), db.ForeignKey('post.id'), nullable=False)
    authorId = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime(timezone=True), server_default=func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'postId': self.postId,
            'author': self.author.to_dict(),
            'text': self.text,
            'timestamp': self.timestamp.isoformat()
        }

class Playground(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(150))
    address = db.Column(db.String(250))
    type = db.Column(db.String(100))
    surface = db.Column(db.String(100))

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "address": self.address,
            "type": self.type,
            "surface": self.surface
        }

class Quest(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(150))
    description = db.Column(db.Text)
    type = db.Column(db.String(50))
    xp_reward = db.Column(db.Integer)

class Achievement(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(150))
    description = db.Column(db.Text)
    icon = db.Column(db.String(50))

class Sponsor(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(150))
    logoUrl = db.Column(db.String(200))
    contribution = db.Column(db.String(200))

class TeamApplication(db.Model):
    __tablename__ = 'team_applications'
    userId = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'), primary_key=True)
    teamId = db.Column(UUID(as_uuid=True), db.ForeignKey('team.id'), primary_key=True)
    status = db.Column(db.String(20), default='pending')
    createdAt = db.Column(db.DateTime(timezone=True), server_default=func.now())

class TeamSeasonStats(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    teamId = db.Column(UUID(as_uuid=True), db.ForeignKey('team.id'), nullable=False)
    season = db.Column(db.Integer, nullable=False)
    leagueRank = db.Column(db.String(50))
    finalElo = db.Column(db.Integer)
    wins = db.Column(db.Integer)
    losses = db.Column(db.Integer)

class UserSession(db.Model):
    __tablename__ = 'user_sessions'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    userId = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'), nullable=False)
    refreshToken = db.Column(db.String(512), nullable=False, index=True)
    userAgent = db.Column(db.String(255))
    ipAddress = db.Column(db.String(45))
    createdAt = db.Column(db.DateTime(timezone=True), server_default=func.now())
    lastActiveAt = db.Column(db.DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Sport(db.Model):
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False)
    isTeamSport = db.Column(db.Boolean, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "isTeamSport": self.isTeamSport
        }

class Upload(db.Model):
    __tablename__ = 'uploads'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'), nullable=False)
    path = db.Column(db.String(512), nullable=False)
    file_hash = db.Column(db.String(64), nullable=True) 
    content_type = db.Column(db.String(100), nullable=False)
    size = db.Column(db.BigInteger, nullable=False)
    status = db.Column(db.String(20), default='initiated', nullable=False) 
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    expires_at = db.Column(db.DateTime(timezone=True), nullable=False)

    user = db.relationship('User', backref=db.backref('uploads', lazy=True))

    def to_dict(self):
        return {
            "uploadId": self.id,
            "userId": self.user_id,
            "path": self.path,
            "contentType": self.content_type,
            "size": self.size,
            "status": self.status,
            "createdAt": self.created_at.isoformat(),
            "expiresAt": self.expires_at.isoformat(),
        }

class LfgPost(db.Model):
    __tablename__ = 'lfg_posts'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False) # 'player' or 'team'
    authorId = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'), nullable=False)
    teamId = db.Column(UUID(as_uuid=True), db.ForeignKey('team.id'), nullable=True)
    sportId = db.Column(db.String, db.ForeignKey('sport.id'), nullable=False)
    requiredRole = db.Column(db.String(100))
    message = db.Column(db.Text)
    createdAt = db.Column(db.DateTime(timezone=True), server_default=func.now())

    author = db.relationship('User', backref=db.backref('lfg_posts', lazy=True))
    team = db.relationship('Team', backref=db.backref('lfg_posts', lazy=True))
    sport = db.relationship('Sport', backref=db.backref('lfg_posts', lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "author": self.author.to_summary_dict(),
            "team": self.team.to_summary_dict() if self.team else None,
            "sport": self.sport.to_dict(),
            "requiredRole": self.requiredRole,
            "message": self.message,
            "createdAt": self.createdAt.isoformat()
        }
