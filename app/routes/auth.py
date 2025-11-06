
from flask import Blueprint, request, jsonify
from app import db
from app.models import User, UserSession
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
import hashlib

auth_bp = Blueprint('auth', __name__)
bcrypt = Bcrypt()

def hash_token(token):
    return hashlib.sha256(token.encode()).hexdigest()

@auth_bp.route('/auth/register', methods=['POST'])
def register():
    """
    Register a new user
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - email
            - password
            - nickname
            - role
          properties:
            email:
              type: string
              description: User's email
              example: "user@example.com"
            password:
              type: string
              description: User's password
              example: "password123"
            nickname:
              type: string
              description: User's nickname
              example: "MyNickname"
            role:
              type: string
              description: User's role
              example: "Игрок"
            city:
              type: string
              description: User's city
              example: "Москва"
            firstName:
              type: string
              description: User's first name
              example: "Иван"
            lastName:
              type: string
              description: User's last name
              example: "Иванов"
    responses:
      201:
        description: User registered successfully
      400:
        description: Missing data
      409:
        description: Email or nickname already exists
    """
    data = request.get_json()
    if not data or not all(k in data for k in ('email', 'password', 'nickname', 'role')):
        return jsonify({'error': 'Missing data'}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 409

    if User.query.filter_by(nickname=data['nickname']).first():
        return jsonify({'error': 'Nickname already exists'}), 409
    
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')

    new_user = User(
        email=data['email'],
        password=hashed_password,
        nickname=data['nickname'],
        role=data['role'],
        city=data.get('city'),
        firstName=data.get('firstName'),
        lastName=data.get('lastName')
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify(new_user.to_dict()), 201

@auth_bp.route('/auth/login', methods=['POST'])
def login():
    """
    Login a user
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
              description: User's email
              example: "user@example.com"
            password:
              type: string
              description: User's password
              example: "password123"
    responses:
      200:
        description: User logged in successfully
      400:
        description: Missing email or password
      401:
        description: Invalid credentials
    """
    data = request.get_json()
    if not data or not all(k in data for k in ('email', 'password')):
        return jsonify({'error': 'Missing email or password'}), 400

    user = User.query.filter_by(email=data['email']).first()

    if user and bcrypt.check_password_hash(user.password, data['password']):
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))
        
        refresh_token_hash = hash_token(refresh_token)

        new_session = UserSession(
            userId=user.id,
            refreshTokenHash=refresh_token_hash,
            userAgent=request.headers.get('User-Agent'),
            ipAddress=request.remote_addr
        )
        db.session.add(new_session)
        db.session.commit()
        
        return jsonify({
            'accessToken': access_token,
            'refreshToken': refresh_token,
            'user': user.to_dict()
        })
    
    return jsonify({'error': 'Invalid credentials'}), 401

@auth_bp.route('/auth/refresh', methods=['POST'])
def refresh():
    """
    Refresh access token
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - refreshToken
          properties:
            refreshToken:
              type: string
              description: The refresh token
    responses:
      200:
        description: Access token refreshed successfully
      400:
        description: Missing refresh token
      401:
        description: Invalid or expired refresh token
    """
    data = request.get_json()
    if 'refreshToken' not in data:
        return jsonify({'error': 'Missing refresh token'}), 400

    refresh_token = data['refreshToken']
    refresh_token_hash = hash_token(refresh_token)

    session = UserSession.query.filter_by(refreshTokenHash=refresh_token_hash).first()

    if not session:
        return jsonify({'error': 'Invalid or expired refresh token'}), 401

    user_id = str(session.user.id)
    new_access_token = create_access_token(identity=user_id)
    
    # Update last active time
    session.lastActiveAt = db.func.now()
    db.session.commit()

    return jsonify({'accessToken': new_access_token})

@auth_bp.route('/auth/logout', methods=['POST'])
def logout():
    """
    Logout a user
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - refreshToken
          properties:
            refreshToken:
              type: string
              description: The refresh token
    responses:
      200:
        description: User logged out successfully
      400:
        description: Missing refresh token
    """
    data = request.get_json()
    if 'refreshToken' not in data:
        return jsonify({'error': 'Missing refresh token'}), 400

    refresh_token = data['refreshToken']
    refresh_token_hash = hash_token(refresh_token)

    session = UserSession.query.filter_by(refreshTokenHash=refresh_token_hash).first()
    if session:
        db.session.delete(session)
        db.session.commit()

    return jsonify({"message": "Successfully logged out"}), 200
