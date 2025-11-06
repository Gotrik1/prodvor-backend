
from flask import Blueprint, request, jsonify
from app import db, limiter
from app.models import User, UserSession
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from app.utils import hash_token

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/auth/register', methods=['POST'])
@limiter.limit("5 per minute") # Дополнительно ограничиваем частоту регистраций
def register():
    data = request.get_json()
    if not data or not all(k in data for k in ('email', 'password', 'nickname', 'role')):
        return jsonify({'error': 'Missing data'}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 409

    if User.query.filter_by(nickname=data['nickname']).first():
        return jsonify({'error': 'Nickname already exists'}), 409
    
    new_user = User(
        email=data['email'],
        nickname=data['nickname'],
        role=data['role'],
        city=data.get('city'),
        firstName=data.get('firstName'),
        lastName=data.get('lastName')
    )
    # Используем новый метод для установки пароля (Argon2)
    new_user.set_password(data['password'])

    db.session.add(new_user)
    db.session.commit()

    return jsonify(new_user.to_dict()), 201

@auth_bp.route('/auth/login', methods=['POST'])
# Лимит уже установлен глобально в __init__.py для этого эндпоинта
def login():
    data = request.get_json()
    if not data or not all(k in data for k in ('email', 'password')):
        return jsonify({'error': 'Missing email or password'}), 400

    user = User.query.filter_by(email=data['email']).first()

    # Используем новый метод для проверки пароля (Argon2 + обратная совместимость с bcrypt)
    if user and user.check_password(data['password']):
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
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
@jwt_required(refresh=True)
def refresh():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user: return jsonify({"error": "User not found"}), 404

    new_access_token = create_access_token(identity=user.id)
    return jsonify({'accessToken': new_access_token})


@auth_bp.route('/auth/logout', methods=['POST'])
def logout():
    data = request.get_json()
    if 'refreshToken' not in data:
        return jsonify({'error': 'Missing refresh token'}), 400

    refresh_token_hash = hash_token(data['refreshToken'])

    session = UserSession.query.filter_by(refreshTokenHash=refresh_token_hash).first()
    if session:
        db.session.delete(session)
        db.session.commit()

    return jsonify({"message": "Successfully logged out"}), 200
