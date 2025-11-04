
from app import db
from sqlalchemy.sql import func
from sqlalchemy.orm import joinedload

TeamMembers = db.Table('team_members',
    db.Column('userId', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('teamId', db.Integer, db.ForeignKey('team.id'), primary_key=True)
)

TeamFollowers = db.Table('team_followers',
    db.Column('userId', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('teamId', db.Integer, db.ForeignKey('team.id'), primary_key=True)
)

user_sports = db.Table('user_sports',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('sport_id', db.String(50), db.ForeignKey('sport.id'), primary_key=True)
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    avatarUrl = db.Column(db.Text)
    coverImageUrl = db.Column(db.Text, nullable=True)
    role = db.Column(db.String(50), nullable=False)
    city = db.Column(db.String(100))
    elo = db.Column(db.Integer, default=0)
    firstName = db.Column(db.String(80), nullable=True)
    lastName = db.Column(db.String(80), nullable=True)
    gender = db.Column(db.String(10), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    bio = db.Column(db.Text, nullable=True)

    player_profile = db.relationship('PlayerProfile', backref='user', uselist=False, cascade="all, delete-orphan")
    referee_profile = db.relationship('RefereeProfile', backref='user', uselist=False, cascade="all, delete-orphan")
    coach_profile = db.relationship('CoachProfile', backref='user', uselist=False, cascade="all, delete-orphan")
    posts = db.relationship('Post', backref='author', lazy=True, cascade="all, delete-orphan")
    comments = db.relationship('Comment', backref='author', lazy=True, cascade="all, delete-orphan")
    member_of_teams = db.relationship('Team', secondary=TeamMembers, backref='members')
    captain_of_teams = db.relationship('Team', backref='captain', foreign_keys='Team.captainId')
    followed_teams = db.relationship('Team', secondary=TeamFollowers, backref='followers', lazy='dynamic')
    sports = db.relationship('Sport', secondary=user_sports, backref='players', lazy=True)
    applications = db.relationship('TeamApplication', backref='user', lazy='dynamic')
    sessions = db.relationship('UserSession', backref='user', lazy=True, cascade="all, delete-orphan")

    def to_dict(self, include_teams=False, include_follows=False):
        data = {
            'id': self.id,
            'nickname': self.nickname,
            'email': self.email,
            'avatarUrl': self.avatarUrl,
            'coverImageUrl': self.coverImageUrl,
            'role': self.role,
            'city': self.city,
            'elo': self.elo,
            'firstName': self.firstName,
            'lastName': self.lastName,
            'gender': self.gender,
            'age': self.age,
            'phone': self.phone,
            'bio': self.bio,
            'sports': [sport.to_dict() for sport in self.sports]
        }
        if include_teams:
            all_teams = {team.id: team for team in self.member_of_teams}
            for team in self.captain_of_teams:
                all_teams[team.id] = team
            data['teams'] = [team.to_dict(expand=True) for team in sorted(all_teams.values(), key=lambda x: x.id)]
        
        if include_follows:
            data['followedTeams'] = [team.to_dict(expand=False) for team in self.followed_teams.all()]

        return data

class UserSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    refreshTokenHash = db.Column(db.String(128), nullable=False, unique=True)
    userAgent = db.Column(db.String(200))
    ipAddress = db.Column(db.String(45))
    lastActiveAt = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    createdAt = db.Column(db.DateTime, default=func.now())

    def to_dict(self, current_token_hash=None):
        return {
            'id': self.id,
            'isCurrent': self.refreshTokenHash == current_token_hash,
            'userAgent': self.userAgent,
            'ipAddress': self.ipAddress,
            'lastActiveAt': self.lastActiveAt.isoformat(),
            'createdAt': self.createdAt.isoformat()
        }


class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    logoUrl = db.Column(db.String(200))
    captainId = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'))
    sport_id = db.Column(db.String(50), db.ForeignKey('sport.id'), nullable=False)
    rank = db.Column(db.Integer, default=1200)
    city = db.Column(db.String(100))
    createdAt = db.Column(db.DateTime, default=func.now())
    
    sport = db.relationship('Sport')
    posts = db.relationship('Post', backref='team', lazy=True, cascade="all, delete-orphan")
    season_stats = db.relationship('TeamSeasonStats', backref='team', lazy=True, cascade="all, delete-orphan")
    applications = db.relationship('TeamApplication', backref='team', lazy='dynamic', cascade="all, delete-orphan")

    # Team Statistics
    wins = db.Column(db.Integer, default=0)
    losses = db.Column(db.Integer, default=0)
    leagueRank = db.Column(db.String(50), nullable=True)
    currentStreakType = db.Column(db.String(1), nullable=True) # 'W' or 'L'
    currentStreakCount = db.Column(db.Integer, default=0)
    form = db.Column(db.String(5), nullable=True) # e.g., 'WWLWD'
    mvpPlayerId = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    topScorerPlayerId = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    cleanSheets = db.Column(db.Integer, default=0)
    avgRating = db.Column(db.Integer, default=0)
    
    mvpPlayer = db.relationship('User', foreign_keys=[mvpPlayerId])
    topScorerPlayer = db.relationship('User', foreign_keys=[topScorerPlayerId])

    def to_dict(self, expand=False):
        # Base data is always included
        data = {
            'id': self.id,
            'name': self.name,
            'logoUrl': self.logoUrl,
            'sport': self.sport.to_dict() if self.sport else None,
            'city': self.city,
            'captainId': self.captainId,
            'followersCount': len(self.followers)
        }

        if not expand:
            # For the basic view, just add member IDs
            member_ids = {member.id for member in self.members}
            if self.captainId:
                member_ids.add(self.captainId)
            data['memberIds'] = sorted(list(member_ids))
            return data

        # If expand is True, add all the details
        all_members = {member.id: member for member in self.members}
        if self.captain and self.captain.id not in all_members:
            all_members[self.captain.id] = self.captain

        data.update({
            # Pass extra flags to prevent circular references
            'captain': self.captain.to_dict(include_teams=False, include_follows=False) if self.captain else None,
            'members': [m.to_dict(include_teams=False, include_follows=False) for m in sorted(all_members.values(), key=lambda x: x.id)],
            'rank': self.rank,
            'createdAt': self.createdAt.isoformat() if self.createdAt else None,
            'wins': self.wins,
            'losses': self.losses,
            'leagueRank': self.leagueRank,
            'currentStreakType': self.currentStreakType,
            'currentStreakCount': self.currentStreakCount,
            'form': self.form,
            'mvpPlayer': self.mvpPlayer.to_dict(include_teams=False, include_follows=False) if self.mvpPlayer else None,
            'topScorerPlayer': self.topScorerPlayer.to_dict(include_teams=False, include_follows=False) if self.topScorerPlayer else None,
            'cleanSheets': self.cleanSheets,
            'avgRating': self.avgRating
        })
        
        return data

class TeamApplication(db.Model):
    __tablename__ = 'team_applications'
    userId = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    teamId = db.Column(db.Integer, db.ForeignKey('team.id'), primary_key=True)
    status = db.Column(db.String(20), default='pending')
    createdAt = db.Column(db.DateTime, default=func.now())

class TeamSeasonStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teamId = db.Column(db.Integer, db.ForeignKey('team.id', ondelete='CASCADE'), nullable=False)
    season = db.Column(db.Integer, nullable=False)
    leagueRank = db.Column(db.String(50))
    finalElo = db.Column(db.Integer)
    wins = db.Column(db.Integer, default=0)
    losses = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            'season': self.season,
            'leagueRank': self.leagueRank,
            'finalElo': self.finalElo,
            'wins': self.wins,
            'losses': self.losses
        }

class PlayerProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), unique=True, nullable=False)
    elo = db.Column(db.Integer, default=1000)
    matchesPlayed = db.Column(db.Integer, default=0)
    wins = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            'id': self.id,
            'userId': self.userId,
            'elo': self.elo,
            'matchesPlayed': self.matchesPlayed,
            'wins': self.wins
        }

class RefereeProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), unique=True, nullable=False)
    category = db.Column(db.String(50))
    matchesJudged = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            'id': self.id,
            'userId': self.userId,
            'category': self.category,
            'matchesJudged': self.matchesJudged
        }

class CoachProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), unique=True, nullable=False)
    specialization = db.Column(db.String(150))
    experienceYears = db.Column(db.Integer)

    def to_dict(self):
        return {
            'id': self.id,
            'userId': self.userId,
            'specialization': self.specialization,
            'experienceYears': self.experienceYears
        }

class Tournament(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    game = db.Column(db.String(100))
    status = db.Column(db.String(50))
    prizePool = db.Column(db.String(100))
    participants = db.Column(db.Integer, default=0)
    maxParticipants = db.Column(db.Integer)
    startDate = db.Column(db.String(100))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'game': self.game,
            'status': self.status,
            'prizePool': self.prizePool,
            'participants': self.participants,
            'maxParticipants': self.maxParticipants,
            'startDate': self.startDate
        }

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    authorId = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    teamId = db.Column(db.Integer, db.ForeignKey('team.id', ondelete='CASCADE'), nullable=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=func.now())
    comments = db.relationship('Comment', backref='post', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'authorId': self.authorId,
            'teamId': self.teamId,
            'content': self.content,
            'timestamp': self.timestamp.isoformat()
        }

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    postId = db.Column(db.Integer, db.ForeignKey('post.id', ondelete='CASCADE'), nullable=False)
    authorId = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'postId': self.postId,
            'authorId': self.authorId,
            'text': self.text,
            'timestamp': self.timestamp.isoformat()
        }

class Playground(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    address = db.Column(db.String(250))
    type = db.Column(db.String(100))
    surface = db.Column(db.String(100))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'type': self.type,
            'surface': self.surface
        }

class Quest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    description = db.Column(db.Text)
    type = db.Column(db.String(50))
    xp_reward = db.Column(db.Integer)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'type': self.type,
            'xp_reward': self.xp_reward
        }

class Achievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    description = db.Column(db.Text)
    icon = db.Column(db.String(50))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'icon': self.icon
        }

class Sponsor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    logoUrl = db.Column(db.String(200))
    contribution = db.Column(db.String(200))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'logoUrl': self.logoUrl,
            'contribution': self.contribution
        }

class Sport(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    isTeamSport = db.Column(db.Boolean, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'isTeamSport': self.isTeamSport
        }
