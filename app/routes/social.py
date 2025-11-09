
from flask import Blueprint, jsonify, request
from ..models import User, Team
from ..utils.decorators import jwt_required

social_bp = Blueprint('social', __name__, url_prefix='/api/v1/users')

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

@social_bp.route('/<uuid:user_id>/friends', methods=['GET'])
@jwt_required
def get_user_friends(current_user, user_id):
    user = User.query.get_or_404(user_id)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # TODO: Добавить проверку приватности
    
    paginated_friends = user.friends.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify(serialize_pagination(paginated_friends, 'friends', lambda u: u.to_summary_dict()))

@social_bp.route('/<uuid:user_id>/followers', methods=['GET'])
def get_user_followers(user_id):
    user = User.query.get_or_404(user_id)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    paginated_followers = user.followers.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify(serialize_pagination(paginated_followers, 'followers', lambda u: u.to_summary_dict()))

@social_bp.route('/<uuid:user_id>/following', methods=['GET'])
@jwt_required
def get_user_following(current_user, user_id):
    user = User.query.get_or_404(user_id)
    
    # TODO: Добавить проверку приватности
    
    # Пагинация для пользователей
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    paginated_users = user.followingUsers.paginate(page=page, per_page=per_page, error_out=False)
    
    # Команды пока без пагинации, как и указано в задаче
    followed_teams = [team.to_summary_dict() for team in user.followingTeams]
    
    user_pagination_data = serialize_pagination(paginated_users, 'users', lambda u: u.to_summary_dict())

    return jsonify({
        "following": {
            "users": user_pagination_data['users'],
            "teams": followed_teams
        },
        "pagination": user_pagination_data['pagination'] # Пагинация относится только к пользователям
    })
