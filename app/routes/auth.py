
from apiflask import APIBlueprint
from flask import request, jsonify, abort
from app import db, bcrypt
from app.models import User, PlayerProfile, RefereeProfile, CoachProfile, UserSession
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
import uuid

auth_bp = APIBlueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user
    ---
    tags:
      - Auth
    summary: Register a new user
    description: Creates a new user with the given email, nickname, password, and role.
    requestBody:
      required: true
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/UserRegistration'
    responses:
      201:
        description: User created successfully.
      409:
        description: User with this email or nickname already exists.
    """
    data = request.get_json()
    
    email = data.get('email')
    nickname = data.get('nickname')
    password = data.get('password')
    role = data.get('role', 'player') # По умолчанию роль - player

    if User.query.filter_by(email=email).first() or User.query.filter_by(nickname=nickname).first():
        abort(409, description="Пользователь с таким email или никнеймом уже существует")

    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    new_user = User(
        id=uuid.uuid4(),
        email=email,
        password_hash=password_hash,
        nickname=nickname,
        role=role,
        city=data.get('city'),
        firstName=data.get('firstName'),
        lastName=data.get('lastName'),
        age=data.get('age'),
        gender=data.get('gender')
    )

    # Создаем специфичный профиль в зависимости от роли
    if role == 'player':
        new_user.player_profile = PlayerProfile()
    elif role == 'referee':
        new_user.referee_profile = RefereeProfile()
    elif role == 'coach':
        new_user.coach_profile = CoachProfile()

    db.session.add(new_user)
    db.session.commit()
    
    return jsonify(new_user.to_dict()), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Log in a user
    ---
    tags:
      - Auth
    summary: Authenticate a user
    description: Authenticates a user with email and password, returning access and refresh tokens.
    requestBody:
      required: true
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/UserLogin'
    responses:
      200:
        description: Login successful.
      401:
        description: Invalid credentials.
    """
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    if user and bcrypt.check_password_hash(user.password_hash, password):
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))

        new_session = UserSession(
            userId=user.id,
            refreshToken=refresh_token,
            userAgent=request.user_agent.string,
            ipAddress=request.remote_addr
        )
        db.session.add(new_session)
        db.session.commit()

        return jsonify({
            "accessToken": access_token,
            "refreshToken": refresh_token,
            "user": user.to_dict(include_teams=True, include_sports=True)
        })
    
    abort(401, description="Неверные учетные данные")

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    Refresh access token
    ---
    tags:
      - Auth
    summary: Get a new access token
    description: Uses a valid refresh token to get a new access token.
    security:
      - bearerAuth: []
    responses:
      200:
        description: Access token refreshed successfully.
      401:
        description: Unauthorized.
    """
    current_user_id = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user_id)
    return jsonify(accessToken=new_access_token)

@auth_bp.route('/logout', methods=['POST'])
@jwt_required(refresh=True)
def logout():
    """
    Log out a user
    ---
    tags:
      - Auth
    summary: Invalidate a refresh token
    description: Logs the user out by deleting their session based on the provided refresh token.
    security:
      - bearerAuth: []
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - refreshToken
            properties:
              refreshToken:
                type: string
    responses:
      200:
        description: Logout successful.
      401:
        description: Unauthorized.
    """
    token = request.get_json().get('refreshToken')
    session = UserSession.query.filter_by(refreshToken=token).first()
    if session:
        db.session.delete(session)
        db.session.commit()
    
    return jsonify({"message": "Вы успешно вышли из системы"}), 200
