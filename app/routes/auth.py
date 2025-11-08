from flask import request, jsonify, Blueprint
from app import db, bcrypt
from app.models import User, PlayerProfile, RefereeProfile, CoachProfile, UserSession
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
import uuid

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    email = data.get('email')
    nickname = data.get('nickname')
    password = data.get('password')
    role = data.get('role', 'player') # По умолчанию роль - player

    if User.query.filter_by(email=email).first() or User.query.filter_by(nickname=nickname).first():
        return jsonify({"error": "Пользователь с таким email или никнеймом уже существует"}), 409

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
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    if user and bcrypt.check_password_hash(user.password_hash, password):
        # Создаем токены
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))

        # Сохраняем сессию в БД
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
    
    return jsonify({"error": "Неверные учетные данные"}), 401

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user_id = get_jwt_identity()
    jti = get_jwt()['jti'] # Уникальный идентификатор JWT
    
    # Здесь можно добавить проверку, не отозван ли refresh token, если потребуется
    # Например, проверив его наличие в UserSessions
    
    new_access_token = create_access_token(identity=current_user_id)
    
    return jsonify(accessToken=new_access_token)

@auth_bp.route('/logout', methods=['POST'])
@jwt_required(refresh=True) # Требуем refresh токен для выхода
def logout():
    jti = get_jwt()['jti']
    current_user_id = get_jwt_identity()
    
    # Вместо jti, будем искать по userId и самому токену, если это необходимо
    # Но для простого логаута достаточно удалить сессию по ID пользователя.
    # Для более безопасного логаута (выход со всех устройств), нужно будет реализовать более сложную логику.
    token = request.get_json().get('refreshToken')
    
    session = UserSession.query.filter_by(refreshToken=token).first()
    if session:
        db.session.delete(session)
        db.session.commit()
    
    return jsonify({"message": "Вы успешно вышли из системы"}), 200
