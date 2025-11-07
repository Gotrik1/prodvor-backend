
from flask import request, jsonify, Blueprint
from app import db, bcrypt
from app.models import User, UserSession, PlayerProfile, RefereeProfile, CoachProfile
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password') or not data.get('nickname') or not data.get('role'):
        return jsonify({"error": "Missing required fields"}), 400

    if User.query.filter_by(email=data['email']).first() or User.query.filter_by(nickname=data['nickname']).first():
        return jsonify({"error": "User with this email or nickname already exists"}), 409

    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    
    new_user = User(
        email=data['email'],
        password=hashed_password,
        nickname=data['nickname'],
        role=data['role'],
        city=data.get('city'),
        # firstName, lastName, age, gender are not in the User model from the plan
    )

    db.session.add(new_user)
    db.session.flush() # Flush to get the new_user.id for profile creation

    # Create profile based on role
    if data['role'] == 'player':
        profile = PlayerProfile(userId=new_user.id)
        db.session.add(profile)
    elif data['role'] == 'referee':
        profile = RefereeProfile(userId=new_user.id)
        db.session.add(profile)
    elif data['role'] == 'coach':
        profile = CoachProfile(userId=new_user.id)
        db.session.add(profile)

    db.session.commit()

    return jsonify(new_user.to_dict()), 201

@auth_bp.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"error": "Missing email or password"}), 400

    user = User.query.filter_by(email=data['email']).first()

    if user and bcrypt.check_password_hash(user.password, data['password']):
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)

        # Create user session
        new_session = UserSession(
            userId=user.id,
            refreshToken=refresh_token,
            userAgent=request.headers.get('User-Agent'),
            ipAddress=request.remote_addr
        )
        db.session.add(new_session)
        db.session.commit()

        return jsonify({
            "accessToken": access_token,
            "refreshToken": refresh_token,
            "user": user.to_dict(include_teams=True)
        })
    
    return jsonify({"error": "Invalid credentials"}), 401

@auth_bp.route('/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    # The decorator already checks the token validity. We can add an extra check against our DB.
    refresh_token_from_request = request.get_json().get('refreshToken')
    session = UserSession.query.filter_by(userId=identity, refreshToken=refresh_token_from_request).first()

    if not session:
        return jsonify({"error": "Invalid or expired refresh token"}), 401

    access_token = create_access_token(identity=identity)
    return jsonify(accessToken=access_token)

@auth_bp.route('/auth/logout', methods=['POST'])
def logout():
    data = request.get_json()
    refresh_token = data.get('refreshToken')
    if not refresh_token:
        return jsonify({"error": "Missing refresh token"}), 400

    session = UserSession.query.filter_by(refreshToken=refresh_token).first()
    if session:
        db.session.delete(session)
        db.session.commit()
    
    return jsonify({"message": "Successfully logged out"}), 200
