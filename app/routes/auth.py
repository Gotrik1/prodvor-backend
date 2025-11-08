
from flask import request, jsonify, Blueprint
from app import db, bcrypt
from app.models import User, UserSession, PlayerProfile, RefereeProfile, CoachProfile
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jti

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/auth/register', methods=['POST'])
def register():
    """
    Register a new user
    Creates a new user and a corresponding profile based on the specified role.
    ---
    tags:
      - Authentication
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              email:
                type: string
              password:
                type: string
              nickname:
                type: string
              role:
                type: string
                enum: ['player', 'referee', 'coach']
              city:
                type: string
            required:
              - email
              - password
              - nickname
              - role
    responses:
      '201':
        description: User created successfully.
      '400':
        description: Missing required fields.
      '409':
        description: User with this email or nickname already exists.
    """
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password') or not data.get('nickname') or not data.get('role'):
        return jsonify({"error": "Missing required fields"}), 400

    if User.query.filter_by(email=data['email']).first() or User.query.filter_by(nickname=data['nickname']).first():
        return jsonify({"error": "User with this email or nickname already exists"}), 409

    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    
    new_user = User(email=data['email'], password_hash=hashed_password, nickname=data['nickname'], role=data['role'], city=data.get('city'))

    db.session.add(new_user)
    db.session.flush()

    if data['role'] == 'player':
        db.session.add(PlayerProfile(userId=new_user.id))
    elif data['role'] == 'referee':
        db.session.add(RefereeProfile(userId=new_user.id))
    elif data['role'] == 'coach':
        db.session.add(CoachProfile(userId=new_user.id))

    db.session.commit()
    return jsonify(new_user.to_dict()), 201

@auth_bp.route('/auth/login', methods=['POST'])
def login():
    """
    User Login
    Authenticates a user and returns access and refresh tokens.
    ---
    tags:
      - Authentication
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              email:
                type: string
                example: user@example.com
              password:
                type: string
                format: password
                example: "password123"
            required:
              - email
              - password
    responses:
      '200':
        description: Authentication successful
      '401':
        description: Invalid credentials
    """
    data = request.get_json()
    user = User.query.filter_by(email=data.get('email')).first()

    if user and bcrypt.check_password_hash(user.password_hash, data.get('password')):
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        refresh_jti = get_jti(refresh_token)
        
        new_session = UserSession(
            userId=user.id,
            refreshToken=refresh_jti,
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
    """
    Refresh access token
    Uses a valid refresh token to get a new access token.
    ---
    tags:
      - Authentication
    security:
      - bearerAuth: []
    responses:
      '200':
        description: Access token refreshed successfully.
      '401':
        description: Invalid or expired refresh token.
    """
    identity = get_jwt_identity()
    jti = get_jwt()['jti']
    
    session = UserSession.query.filter_by(refreshToken=jti).first()
    if not session:
        return jsonify({"error": "Invalid or expired refresh token"}), 401

    access_token = create_access_token(identity=identity)
    return jsonify(accessToken=access_token)

@auth_bp.route('/auth/logout', methods=['POST'])
@jwt_required(refresh=True)
def logout():
    """
    Logout user
    Invalidates the user's refresh token.
    ---
    tags:
      - Authentication
    security:
      - bearerAuth: []
    responses:
      '200':
        description: Successfully logged out.
    """
    jti = get_jwt()['jti']
    session = UserSession.query.filter_by(refreshToken=jti).first()
    if session:
        db.session.delete(session)
        db.session.commit()
    
    return jsonify({"message": "Successfully logged out"}), 200
