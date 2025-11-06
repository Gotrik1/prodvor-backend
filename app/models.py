
from app import db, bcrypt
from sqlalchemy.sql import func
from sqlalchemy.orm import joinedload
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher()

TeamMembers = db.Table('team_members',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('team_id', db.Integer, db.ForeignKey('team.id'), primary_key=True)
)

TeamFollowers = db.Table('team_followers',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('team_id', db.Integer, db.ForeignKey('team.id'), primary_key=True)
)

user_sports = db.Table('user_sports',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('sport_id', db.Integer, db.ForeignKey('sport.id'), primary_key=True)
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    is_active = db.Column(db.Boolean, default=True)
    avatarUrl = db.Column(db.String(512), nullable=True)
    
    sessions = db.relationship('UserSession', backref='user', lazy=True, cascade="all, delete-orphan")
    teams_created = db.relationship('Team', backref='creator', lazy=True, foreign_keys='Team.creator_id')

    def set_password(self, password):
        self.password = ph.hash(password)

    def check_password(self, password):
        try:
            ph.verify(self.password, password)
            if ph.check_needs_rehash(self.password):
                self.set_password(password)
                db.session.commit()
            return True
        except VerifyMismatchError:
            try:
                if bcrypt.check_password_hash(self.password, password):
                    self.set_password(password)
                    db.session.commit()
                    return True
            except (ValueError, TypeError):
                 return False
            return False
        except Exception:
            return False

    def to_dict(self, include_teams=False, include_follows=False):
        data = {
            'id': self.id,
            'nickname': self.nickname,
            'email': self.email,
            'avatarUrl': self.avatarUrl,
            'createdAt': self.created_at.isoformat()
        }
        if include_teams:
            data['teamsCreated'] = [team.to_dict() for team in self.teams_created]
        if include_follows:
            pass
        return data

class UserSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    refresh_token_jti = db.Column(db.String(36), nullable=False, index=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    expires_at = db.Column(db.DateTime(timezone=True), nullable=False)
    user_agent = db.Column(db.String(200))
    ip_address = db.Column(db.String(45))

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    logoUrl = db.Column(db.String(512), nullable=True) # <-- ДОБАВЛЕНО
    
    members = db.relationship('User', secondary=TeamMembers, lazy='subquery',
                              backref=db.backref('teams_member_of', lazy=True))
    followers = db.relationship('User', secondary=TeamFollowers, lazy='subquery',
                                backref=db.backref('teams_following', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'creatorId': self.creator_id,
            'logoUrl': self.logoUrl # <-- ДОБАВЛЕНО
        }

class Sport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
