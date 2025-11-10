
from apiflask import APIBlueprint
from flask import request, jsonify, abort
from app import db, bcrypt
from app.models import User, PlayerProfile, RefereeProfile, CoachProfile, UserSession
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
import uuid

auth_bp = APIBlueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
@auth_bp.doc(operation_id='register')
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
      '201':
        description: User created successfully.
      '409':
        description: User with this email or nickname already exists.
    """
    data = request.get_json()
    
    email = data.get('email')
    nickname = data.get('nickname')
    password = data.get('password')
    role = data.get('role', 'player')

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
@auth_bp.doc(operation_id='login')
def login():
    """
    Login
    ---
    summary: Login
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required: [email, password]
            properties:
              email:
                type: string
                format: email
              password:
                type: string
                minLength: 6
    responses:
      '200':
        description: OK
        content:
          application/json:
            schema:
              type: object
              properties:
                access_token:
                  type: string
                refresh_token:
                  type: string
      '401':
        description: Unauthorized
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
            "access_token": access_token,
            "refresh_token": refresh_token
        })
    
    abort(401, description="Invalid credentials")

@auth_bp.route('/refresh', methods=['POST'])
@auth_bp.doc(operation_id='refreshToken')
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
      '200':
        description: Access token refreshed successfully.
      '401':
        description: Unauthorized.
    """
    current_user_id = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user_id)
    return jsonify(accessToken=new_access_token)

@auth_bp.route('/logout', methods=['POST'])
@auth_bp.doc(operation_id='logout')
@jwt_required(refresh=True)
def logout():
    """
    Log out a user
    ---
    tags:
      - Auth
    summary: Invalidate a refresh token
    description: Logs the user out by invalidating the refresh token. The token is passed in the Authorization header.
    security:
      - bearerAuth: []
    responses:
      '200':
        description: Logout successful.
      '401':
        description: Unauthorized.
      '404':
        description: Token not found.
    """
    auth_header = request.headers.get('Authorization')
    token = auth_header.split()[1] if auth_header else None

    if not token:
        abort(401, description="Authorization header is missing.")

    session = UserSession.query.filter_by(refreshToken=token).first()
    if session:
        db.session.delete(session)
        db.session.commit()
        return jsonify({"message": "Вы успешно вышли из системы"}), 200
    else:
        abort(404, "Сессия не найдена или уже завершена.")
