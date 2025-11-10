
from apiflask import APIBlueprint
from flask import jsonify, request, abort
from uuid import UUID
from ..models import db, User, FriendRequest, Team, UserSettings, UserPrivacySettings, TeamFollowers
from flask_jwt_extended import jwt_required, current_user

users_bp = APIBlueprint('users', __name__, url_prefix='/api/v1/users')

def serialize_pagination(pagination, serializer):
    """Helper function to serialize paginated data according to the spec."""
    return {
        "data": [serializer(item) for item in pagination.items],
        "meta": {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages,
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
@users_bp.doc(operation_id='getUserById')
@jwt_required()
def get_user(user_id):
    """Get user profile by ID. Returns a full user object, including player_profile if available."""
    try:
        user_uuid = UUID(user_id, version=4)
    except ValueError:
        abort(400, description="Invalid UUID format")

    user = User.query.get_or_404(user_uuid)
    profile_buttons = get_profile_buttons(current_user.id, user)
    return jsonify(user.to_dict(profile_buttons=profile_buttons, include_settings=False))

@users_bp.route('/me', methods=['GET'])
@users_bp.doc(operation_id='getCurrentUser')
@jwt_required()
def get_me():
    """Get current user's profile."""
    # current_user is now a proxy from flask_jwt_extended
    user = User.query.get_or_404(current_user.id)
    profile_buttons = get_profile_buttons(current_user.id, user)
    return jsonify(user.to_dict(include_teams=True, profile_buttons=profile_buttons, include_settings=True))

@users_bp.route('/<string:user_id>/friends', methods=['GET'])
@users_bp.doc(operation_id='listUserFriends')
@jwt_required()
def get_user_friends(user_id):
    """Get a paginated list of a user's friends."""
    try:
        user_uuid = UUID(user_id, version=4)
    except ValueError:
        abort(400, description="Invalid UUID format")

    user = User.query.get_or_404(user_uuid)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    friends_pagination = user.friends.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify(serialize_pagination(friends_pagination, lambda u: u.to_dict()))

@users_bp.route('/<string:user_id>/followers', methods=['GET'])
@users_bp.doc(operation_id='listUserFollowers')
@jwt_required()
def get_user_followers(user_id):
    """Get a paginated list of a user's followers."""
    try:
        user_uuid = UUID(user_id, version=4)
    except ValueError:
        abort(400, description="Invalid UUID format")

    user = User.query.get_or_404(user_uuid)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    followers_pagination = user.followers.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify(serialize_pagination(followers_pagination, lambda u: u.to_dict()))

@users_bp.route('/<string:user_id>/following', methods=['GET'])
@users_bp.doc(operation_id='listUserFollowing')
@jwt_required()
def get_user_following(user_id):
    """Get paginated lists of users and teams a user is following."""
    try:
        user_uuid = UUID(user_id, version=4)
    except ValueError:
        abort(400, description="Invalid UUID format")

    user = User.query.get_or_404(user_uuid)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    # Paginate user's followed users
    users_following_pagination = user.followingUsers.paginate(page=page, per_page=per_page, error_out=False)

    # Paginate user's followed teams
    teams_following_query = Team.query.join(TeamFollowers).filter(TeamFollowers.c.userId == user.id)
    teams_following_pagination = teams_following_query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "users": serialize_pagination(users_following_pagination, lambda u: u.to_dict()),
        "teams": serialize_pagination(teams_following_pagination, lambda t: t.to_dict())
    })
