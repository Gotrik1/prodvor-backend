
from sqlalchemy.sql import func
from . import db

# --- Связующие таблицы ---

TeamMembers = db.Table('team_members',
    db.Column('userId', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('teamId', db.Integer, db.ForeignKey('team.id'), primary_key=True)
)

TeamFollowers = db.Table('team_followers',
    db.Column('userId', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('teamId', db.Integer, db.ForeignKey('team.id'), primary_key=True)
)

UserSports = db.Table('user_sports',
    db.Column('userId', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('sportId', db.String, db.ForeignKey('sport.id'), primary_key=True)
)

# --- Основные модели ---

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    avatarUrl = db.Column(db.String(200))
    role = db.Column(db.String(50), nullable=False)
    city = db.Column(db.String(100))
    elo = db.Column(db.Integer, default=1200)
    password = db.Column(db.String(255), nullable=False)

    player_profile = db.relationship('PlayerProfile', backref='user', uselist=False, cascade="all, delete-orphan")
    referee_profile = db.relationship('RefereeProfile', backref='user', uselist=False, cascade="all, delete-orphan")
    coach_profile = db.relationship('CoachProfile', backref='user', uselist=False, cascade="all, delete-orphan")
    posts = db.relationship('Post', backref='author', lazy=True)
    comments = db.relationship('Comment', backref='author', lazy=True)
    teams = db.relationship('Team', secondary=TeamMembers, backref=db.backref('members', lazy='dynamic'))
    sports = db.relationship('Sport', secondary=UserSports, backref=db.backref('users', lazy='dynamic'))

    def to_dict(self, include_teams=False, include_sports=False):
        data = {
            "id": self.id,
            "nickname": self.nickname,
            "email": self.email,
            "avatarUrl": self.avatarUrl,
            "role": self.role,
            "city": self.city,
            "elo": self.elo
        }
        if include_teams:
            data['teams'] = [team.to_dict() for team in self.teams]
        if include_sports:
            data['sports'] = [sport.to_dict() for sport in self.sports]
        return data

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    logoUrl = db.Column(db.String(200))
    captainId = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    game = db.Column(db.String(100))
    rank = db.Column(db.Integer, default=1200)
    city = db.Column(db.String(100))
    wins = db.Column(db.Integer, default=0)
    losses = db.Column(db.Integer, default=0)
    leagueRank = db.Column(db.String(50))
    currentStreakType = db.Column(db.String(1))
    currentStreakCount = db.Column(db.Integer)
    form = db.Column(db.String(5))
    mvpPlayerId = db.Column(db.Integer, db.ForeignKey('user.id'))
    topScorerPlayerId = db.Column(db.Integer, db.ForeignKey('user.id'))
    cleanSheets = db.Column(db.Integer, default=0)
    avgRating = db.Column(db.Integer, default=0)
    createdAt = db.Column(db.DateTime(timezone=True), server_default=func.now())
    
    posts = db.relationship('Post', backref='team', lazy=True)
    captain = db.relationship('User', foreign_keys=[captainId])

    def to_dict(self, include_members=False):
        data = {
            "id": self.id,
            "name": self.name,
            "logoUrl": self.logoUrl,
            "captainId": self.captainId,
            "game": self.game,
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
        if include_members:
            data['members'] = [member.to_dict() for member in self.members]
            data['captain'] = self.captain.to_dict() if self.captain else None
        return data

class PlayerProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    elo = db.Column(db.Integer, default=1000)
    matchesPlayed = db.Column(db.Integer, default=0)
    wins = db.Column(db.Integer, default=0)

class RefereeProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    category = db.Column(db.String(50))
    matchesJudged = db.Column(db.Integer, default=0)

class CoachProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    specialization = db.Column(db.String(150))
    experienceYears = db.Column(db.Integer)

class Tournament(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    game = db.Column(db.String(100))
    status = db.Column(db.String(50))
    prizePool = db.Column(db.String(100))
    participants = db.Column(db.Integer, default=0)
    maxParticipants = db.Column(db.Integer)
    startDate = db.Column(db.String(100))

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    authorId = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    teamId = db.Column(db.Integer, db.ForeignKey('team.id'))
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime(timezone=True), server_default=func.now())
    
    comments = db.relationship('Comment', backref='post', lazy=True, cascade="all, delete-orphan")

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    postId = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    authorId = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime(timezone=True), server_default=func.now())

class Playground(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    address = db.Column(db.String(250))
    type = db.Column(db.String(100))
    surface = db.Column(db.String(100))

class Quest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    description = db.Column(db.Text)
    type = db.Column(db.String(50))
    xp_reward = db.Column(db.Integer)

class Achievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    description = db.Column(db.Text)
    icon = db.Column(db.String(50))

class Sponsor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    logoUrl = db.Column(db.String(200))
    contribution = db.Column(db.String(200))

class TeamApplication(db.Model):
    __tablename__ = 'team_applications'
    userId = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    teamId = db.Column(db.Integer, db.ForeignKey('team.id'), primary_key=True)
    status = db.Column(db.String(20), default='pending')
    createdAt = db.Column(db.DateTime(timezone=True), server_default=func.now())

class TeamSeasonStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teamId = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    season = db.Column(db.Integer, nullable=False)
    leagueRank = db.Column(db.String(50))
    finalElo = db.Column(db.Integer)
    wins = db.Column(db.Integer)
    losses = db.Column(db.Integer)

class UserSession(db.Model):
    __tablename__ = 'user_sessions'
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    refreshToken = db.Column(db.String(512), nullable=False)
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
