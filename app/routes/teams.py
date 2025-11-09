
from apiflask import APIBlueprint
from flask import request, jsonify, abort
from app import db
from app.models import Team, User, Sport, TeamApplication
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.routes.users import serialize_pagination
import uuid

teams_bp = APIBlueprint('teams', __name__, url_prefix='/api/v1/teams')

@teams_bp.route('/', methods=['GET'])
def get_teams():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    paginated_teams = Team.query.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify(serialize_pagination(paginated_teams, 'data', lambda t: t.to_dict()))

@teams_bp.route('/<string:team_id>', methods=['GET'])
def get_team(team_id):
    team = Team.query.get_or_404(team_id)
    return jsonify(team.to_dict(include_members=True))

@teams_bp.route('/', methods=['POST'])
@jwt_required()
def create_team():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    if not data or not data.get('name') or not data.get('sportId'):
        abort(400, description="Missing required fields: name, sportId")
    sport = Sport.query.get(data['sportId'])
    if not sport:
        abort(404, description="Sport with the given ID not found.")
    new_team = Team(
        id=str(uuid.uuid4()),
        name=data['name'],
        sportId=data['sportId'],
        city=data.get('city'),
        logoUrl=data.get('logoUrl'),
        captainId=current_user_id
    )
    captain = User.query.get(current_user_id)
    if captain:
        new_team.members.append(captain)
    db.session.add(new_team)
    db.session.commit()
    return jsonify(new_team.to_dict(include_members=True)), 201

@teams_bp.route('/<string:team_id>/members/<string:user_id>', methods=['DELETE'])
@jwt_required()
def remove_member(team_id, user_id):
    current_user_id = get_jwt_identity()
    team = Team.query.get_or_404(team_id)
    if str(team.captainId) != current_user_id:
        abort(403, description="Only the captain can remove members")
    if str(team.captainId) == user_id:
        abort(400, description="Captain cannot remove themselves")
    user_to_remove = User.query.get(user_id)
    if not user_to_remove or user_to_remove not in team.members:
        abort(404, description="Player is not a member of this team")
    team.members.remove(user_to_remove)
    db.session.commit()
    return jsonify({"success": True, "message": "Player removed successfully"})

@teams_bp.route('/<string:team_id>/logo', methods=['POST'])
@jwt_required()
def update_team_logo(team_id):
    current_user_id = get_jwt_identity()
    team = Team.query.get_or_404(team_id)
    if str(team.captainId) != current_user_id:
        abort(403, description="Only the captain can update the logo")
    data = request.get_json()
    if not data or 'fileUrl' not in data:
        abort(400, description="Missing fileUrl")
    team.logoUrl = data['fileUrl']
    db.session.commit()
    return jsonify({"message": "Логотип успешно обновлен", "logoUrl": team.logoUrl})

@teams_bp.route('/<string:team_id>/apply', methods=['POST'])
@jwt_required()
def apply_to_team(team_id):
    current_user_id = get_jwt_identity()
    team = Team.query.get_or_404(team_id)
    user = User.query.get(current_user_id)
    if user in team.members:
        abort(400, description="You are already a member of this team")
    existing_application = TeamApplication.query.filter_by(teamId=team_id, userId=current_user_id).first()
    if existing_application:
        abort(400, description="You have already applied to this team")
    application = TeamApplication(userId=current_user_id, teamId=team_id, status='pending')
    db.session.add(application)
    db.session.commit()
    return jsonify({"success": True, "message": "Заявка успешно отправлена"})

@teams_bp.route('/<string:team_id>/applications', methods=['GET'])
@jwt_required()
def get_applications(team_id):
    current_user_id = get_jwt_identity()
    team = Team.query.get_or_404(team_id)
    if str(team.captainId) != current_user_id:
        abort(403, description="Only the captain can view applications")
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    applications_pagination = TeamApplication.query.filter_by(teamId=team_id, status='pending').paginate(page=page, per_page=per_page, error_out=False)
    
    # We need to serialize the user associated with the application
    def serialize_applicant(application):
        user = User.query.get(application.userId)
        return user.to_summary_dict() if user else None

    # Filter out None values in case a user was deleted but the application remains
    serialized_items = [serialize_applicant(app) for app in applications_pagination.items]
    non_null_items = [item for item in serialized_items if item is not None]
    
    # Manually build the final response to handle the custom serialization
    return jsonify({
        "data": non_null_items,
        "meta": {
            "page": applications_pagination.page,
            "per_page": applications_pagination.per_page,
            "total": applications_pagination.total,
            "pages": applications_pagination.pages,
            "has_next": applications_pagination.has_next,
            "has_prev": applications_pagination.has_prev
        }
    })

@teams_bp.route('/<string:team_id>/applications/<string:user_id>/respond', methods=['POST'])
@jwt_required()
def respond_to_application(team_id, user_id):
    current_user_id = get_jwt_identity()
    team = Team.query.get_or_404(team_id)
    if str(team.captainId) != current_user_id:
        abort(403, description="Only the captain can respond to applications")
    application = TeamApplication.query.filter_by(teamId=team_id, userId=user_id, status='pending').first()
    if not application:
        abort(404, description="Application not found")
    data = request.get_json()
    action = data.get('action')
    if action == 'accept':
        user_to_add = User.query.get(user_id)
        if not user_to_add:
             abort(404, description="User to add not found")
        team.members.append(user_to_add)
        db.session.delete(application)
        db.session.commit()
        return jsonify({"success": True, "message": "Решение принято: игрок принят"})
    elif action == 'decline':
        db.session.delete(application)
        db.session.commit()
        return jsonify({"success": True, "message": "Решение принято: игрок отклонен"})
    else:
        abort(400, description="Invalid action")

@teams_bp.route('/<string:team_id>/follow', methods=['POST'])
@jwt_required()
def follow_team(team_id):
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    team = Team.query.get_or_404(team_id)
    if team in user.followingTeams:
        user.followingTeams.remove(team)
        db.session.commit()
        return jsonify({"success": True, "isFollowing": False})
    else:
        user.followingTeams.append(team)
        db.session.commit()
        return jsonify({"success": True, "isFollowing": True})
