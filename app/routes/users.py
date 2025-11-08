from flask import request, jsonify, Blueprint
from app import db
from app.models import User, Sport
from flask_jwt_extended import jwt_required, get_jwt_identity

users_bp = Blueprint('users', __name__)

@users_bp.route('/', methods=['GET'])
def get_users():
    """Возвращает список всех пользователей."""
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@users_bp.route('/me', methods=['GET'])
@jwt_required()
def get_me():
    """Возвращает профиль текущего аутентифицированного пользователя."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    include_teams = request.args.get('include_teams', 'false').lower() == 'true'
    return jsonify(user.to_dict(include_teams=include_teams, include_sports=True))

@users_bp.route('/<string:user_id>', methods=['GET'])
def get_user(user_id):
    """Возвращает профиль пользователя по ID."""
    user = User.query.get_or_404(user_id)
    include_teams = request.args.get('include_teams', 'false').lower() == 'true'
    return jsonify(user.to_dict(include_teams=include_teams, include_sports=True))

@users_bp.route('/<string:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """Обновляет профиль пользователя."""
    current_user_id = get_jwt_identity()
    user_to_update = User.query.get_or_404(user_id)
    current_user = User.query.get(current_user_id)

    # Проверка прав: доступ имеет только владелец профиля или администратор
    if str(user_to_update.id) != current_user_id and (not current_user or current_user.role != 'admin'):
        return jsonify({"error": "Forbidden"}), 403

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    # Обновляем поля, если они есть в запросе
    user_to_update.nickname = data.get('nickname', user_to_update.nickname)
    user_to_update.city = data.get('city', user_to_update.city)
    user_to_update.firstName = data.get('firstName', user_to_update.firstName)
    user_to_update.lastName = data.get('lastName', user_to_update.lastName)
    user_to_update.age = data.get('age', user_to_update.age)
    user_to_update.gender = data.get('gender', user_to_update.gender)
    user_to_update.bio = data.get('bio', user_to_update.bio)
    if 'birthDate' in data:
        # Здесь может понадобиться парсинг даты из строки в объект datetime
        # Для простоты пока предполагаем, что дата приходит в корректном формате
        user_to_update.birthDate = data.get('birthDate') 

    # Обработка sports: полная перезапись
    if 'sports' in data and isinstance(data['sports'], list):
        user_to_update.sports.clear()
        sports_to_add = Sport.query.filter(Sport.id.in_(data['sports'])).all()
        for sport in sports_to_add:
            user_to_update.sports.append(sport)
    
    db.session.commit()
    return jsonify(user_to_update.to_dict(include_teams=True, include_sports=True))

@users_bp.route('/avatar', methods=['POST'])
@jwt_required()
def update_avatar():
    """Обновляет URL аватара пользователя."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()
    if not data or 'fileUrl' not in data:
        return jsonify({"error": "Missing fileUrl"}), 400

    user.avatarUrl = data['fileUrl']
    db.session.commit()

    return jsonify({"message": "Аватар успешно обновлен", "user": user.to_dict()})
