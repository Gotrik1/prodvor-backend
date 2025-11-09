
from flask import Blueprint, jsonify
from ..models import User, FriendRequest
from ..utils.decorators import jwt_required

users_bp = Blueprint('users', __name__, url_prefix='/api/v1/users')

def get_profile_buttons(current_user_id, profile_owner):
    buttons = []
    # Это наш собственный профиль
    if current_user_id == profile_owner.id:
        buttons.append({"action": {"type": "edit_profile"}, "text": "Редактировать"})
    else:
        # Проверяем, друзья ли мы
        is_friend = any(friend.id == current_user_id for friend in profile_owner.friends)
        if is_friend:
            buttons.append({"action": {"type": "friend_request", "status": "already_friend"}, "text": "Вы друзья"})
        else:
            # Проверяем, была ли отправлена заявка
            sent_request = FriendRequest.query.filter_by(from_user_id=current_user_id, to_user_id=profile_owner.id, status='pending').first()
            received_request = FriendRequest.query.filter_by(from_user_id=profile_owner.id, to_user_id=current_user_id, status='pending').first()

            if sent_request:
                buttons.append({"action": {"type": "friend_request", "status": "request_sent"}, "text": "Отменить заявку"})
            elif received_request:
                 buttons.append({"action": {"type": "friend_request", "status": "request_received"}, "text": "Принять заявку"})
            else:
                buttons.append({"action": {"type": "friend_request", "status": "not_friend"}, "text": "Добавить в друзья"})
        
        buttons.append({"action": {"type": "write_message"}, "text": "Сообщение"})
    
    buttons.append({"action": {"type": "more_options"}, "text": "..."})
    return buttons

@users_bp.route('/<uuid:user_id>', methods=['GET'])
@jwt_required
def get_user(current_user, user_id):
    user = User.query.get_or_404(user_id)
    
    profile_buttons = get_profile_buttons(current_user.id, user)

    # Настройки приватности и интерфейса не должны быть видны другим пользователям
    return jsonify(user.to_dict(profile_buttons=profile_buttons, include_settings=False))

@users_bp.route('/me', methods=['GET'])
@jwt_required
def get_me(current_user):
    user = User.query.get_or_404(current_user.id)

    profile_buttons = get_profile_buttons(current_user.id, user)
    
    # Включаем настройки в ответ для /me
    return jsonify(user.to_dict(include_teams=True, profile_buttons=profile_buttons, include_settings=True))

@users_bp.route('/me/sessions', methods=['GET'])
@jwt_required
def get_my_sessions(current_user):
    # Логика получения сессий
    return jsonify([])

@users_bp.route('/me/sessions/<uuid:session_id>', methods=['DELETE'])
@jwt_required
def delete_my_session(current_user, session_id):
    # Логика удаления сессии
    return jsonify({}), 204

@users_bp.route('/me/sessions/all-except-current', methods=['DELETE'])
@jwt_required
def delete_all_my_sessions(current_user):
    # Логика удаления всех сессий, кроме текущей
    return jsonify({}), 204
