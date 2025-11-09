
from flask import Blueprint, jsonify, request
from uuid import UUID
from ..models import db, User, FriendRequest, Team, UserSettings, UserPrivacySettings
from ..utils.decorators import jwt_required

users_bp = Blueprint('users', __name__, url_prefix='/api/v1/users')

def serialize_pagination(pagination, data_key, serializer):
    return {
        data_key: [serializer(item) for item in pagination.items],
        "pagination": {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev
        }
    }

def get_profile_buttons(current_user_id, profile_owner):
    buttons = []
    if current_user_id == profile_owner.id:
        buttons.append({"action": {"type": "edit_profile"}, "text": "Редактировать"})
    else:
        is_friend = any(friend.id == current_user_id for friend in profile_owner.friends)
        if is_friend:
            buttons.append({"action": {"type": "friend_request", "status": "already_friend"}, "text": "Вы друзья"})
        else:
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

@users_bp.route('/<string:user_id>', methods=['GET'])
@jwt_required
def get_user(current_user, user_id):
    """
    Get user profile by ID
    ---
    tags:
      - User Profile
    summary: Get a user's profile by their ID
    description: Retrieves public profile information for a specific user, along with context-aware action buttons (e.g., 'Add Friend').
    security:
      - bearerAuth: []
    parameters:
      - in: path
        name: user_id
        required: true
        schema:
          type: string
          format: uuid
        description: The UUID of the user to retrieve.
    responses:
      200:
        description: User profile data retrieved successfully.
      404:
        description: User not found.
      400:
        description: Invalid UUID format.
    """
    try:
        user_uuid = UUID(user_id, version=4)
    except ValueError:
        return jsonify({"error": "Invalid UUID format"}), 400

    user = User.query.get_or_404(user_uuid)
    profile_buttons = get_profile_buttons(current_user.id, user)
    return jsonify(user.to_dict(profile_buttons=profile_buttons, include_settings=False))

@users_bp.route('/me', methods=['GET'])
@jwt_required
def get_me(current_user):
    """
    Get current user's profile
    ---
    tags:
      - User Profile
    summary: Get current user's profile
    description: Retrieves the complete profile information for the currently authenticated user, including teams and settings.
    security:
      - bearerAuth: []
    responses:
      200:
        description: User profile data successfully retrieved.
      401:
        description: Unauthorized. JWT is missing or invalid.
    """
    user = User.query.get_or_404(current_user.id)
    profile_buttons = get_profile_buttons(current_user.id, user)
    return jsonify(user.to_dict(include_teams=True, profile_buttons=profile_buttons, include_settings=True))

# ... (остальные эндпоинты без изменений) ...
