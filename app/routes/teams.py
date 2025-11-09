from flask import request, jsonify, Blueprint
from app import db
from app.models import Team, User, Sport, TeamApplication
from flask_jwt_extended import jwt_required, get_jwt_identity
import uuid

teams_bp = Blueprint('teams', __name__)


@teams_bp.route('/', methods=['GET'])
def get_teams():
    """
    Get all teams (paginated)
    ---
    tags:
      - Teams
    summary: Get all teams
    description: Returns a paginated list of all teams.
    parameters:
      - in: query
        name: page
        schema:
          type: integer
          default: 1
        description: The page number for pagination.
      - in: query
        name: limit
        schema:
          type: integer
          default: 12
        description: The number of teams to return per page.
    responses:
      200:
        description: A paginated list of teams.
    """
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 12))
    except (ValueError, TypeError):
        page = 1
        limit = 12

    paginated_teams = Team.query.paginate(page=page, per_page=limit, error_out=False)

    teams_list = [team.to_dict() for team in paginated_teams.items]

    return jsonify({
        "teams": teams_list,
        "pagination": {
            "totalItems": paginated_teams.total,
            "totalPages": paginated_teams.pages,
            "currentPage": paginated_teams.page,
            "limit": paginated_teams.per_page
        }
    })


@teams_bp.route('/<string:team_id>', methods=['GET'])
def get_team(team_id):
    """
    Get a specific team by ID
    ---
    tags:
      - Teams
    summary: Get a single team by its ID
    description: Returns details for a single team, including its members.
    parameters:
      - in: path
        name: team_id
        required: true
        schema:
          type: string
        description: The ID of the team to retrieve.
    responses:
      200:
        description: Team details.
      404:
        description: Team not found.
    """
    team = Team.query.get_or_404(team_id)
    return jsonify(team.to_dict(include_members=True))


@teams_bp.route('/', methods=['POST'])
@jwt_required()
def create_team():
    """
    Create a new team
    ---
    tags:
      - Teams
    summary: Create a new team
    description: Creates a new team. The authenticated user will become the captain.
    security:
      - bearerAuth: []
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - name
              - sportId
            properties:
              name:
                type: string
                example: "The All-Stars"
              sportId:
                type: string
                example: "sport-1"
              city:
                type: string
                example: "New York"
              logoUrl:
                type: string
                example: "https://example.com/logo.png"
    responses:
      201:
        description: Team created successfully.
      400:
        description: Bad request (missing required fields).
      404:
        description: Captain user not found.
    """
    current_user_id = get_jwt_identity()
    data = request.get_json()

    if not data or not data.get('name') or not data.get('sportId'):
        return jsonify({"error": "Missing required fields: name, sportId"}), 400

    captain = User.query.get(current_user_id)
    if not captain:
        return jsonify({"error": "Captain user not found"}), 404

    new_team = Team(
        id=uuid.uuid4(),
        name=data['name'],
        sportId=data['sportId'],
        city=data.get('city'),
        logoUrl=data.get('logoUrl'),
        captainId=captain.id
    )

    # Капитан автоматически становится участником команды
    new_team.members.append(captain)

    db.session.add(new_team)
    db.session.commit()

    return jsonify(new_team.to_dict(include_members=True)), 201


@teams_bp.route('/<string:team_id>/members/<string:user_id>', methods=['DELETE'])
@jwt_required()
def remove_member(team_id, user_id):
    """
    Remove a member from a team
    ---
    tags:
      - Teams
    summary: Remove a member from a team (Captain only)
    description: Removes a specified user from a team. This action can only be performed by the team captain.
    security:
      - bearerAuth: []
    parameters:
      - in: path
        name: team_id
        required: true
        schema:
          type: string
        description: The ID of the team.
      - in: path
        name: user_id
        required: true
        schema:
          type: string
        description: The ID of the user to remove.
    responses:
      200:
        description: Player removed successfully.
      400:
        description: Bad request (captain cannot remove themselves).
      403:
        description: Forbidden (only the captain can remove members).
      404:
        description: Not found (team or player not found).
    """
    current_user_id = get_jwt_identity()
    team = Team.query.get_or_404(team_id)

    if str(team.captainId) != current_user_id:
        return jsonify({"error": "Only the captain can remove members"}), 403

    if str(team.captainId) == user_id:
        return jsonify({"error": "Captain cannot remove themselves"}), 400

    user_to_remove = User.query.get(user_id)
    if not user_to_remove or user_to_remove not in team.members:
        return jsonify({"error": "Player is not a member of this team"}), 404

    team.members.remove(user_to_remove)
    db.session.commit()

    return jsonify({"success": True, "message": "Player removed successfully"})


@teams_bp.route('/<string:team_id>/logo', methods=['POST'])
@jwt_required()
def update_team_logo(team_id):
    """
    Update team logo
    ---
    tags:
      - Teams
    summary: Update team logo (Captain only)
    description: Updates the logo URL for a team. This action can only be performed by the team captain.
    security:
      - bearerAuth: []
    parameters:
      - in: path
        name: team_id
        required: true
        schema:
          type: string
        description: The ID of the team to update.
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required: [fileUrl]
            properties:
              fileUrl:
                type: string
                format: uri
                example: "https://example.com/new_logo.png"
    responses:
      200:
        description: Logo updated successfully.
      400:
        description: Bad request (missing fileUrl).
      403:
        description: Forbidden (only the captain can update the logo).
    """
    current_user_id = get_jwt_identity()
    team = Team.query.get_or_404(team_id)

    if str(team.captainId) != current_user_id:
        return jsonify({"error": "Only the captain can update the logo"}), 403

    data = request.get_json()
    if not data or 'fileUrl' not in data:
        return jsonify({"error": "Missing fileUrl"}), 400

    team.logoUrl = data['fileUrl']
    db.session.commit()

    return jsonify({"message": "Логотип успешно обновлен", "logoUrl": team.logoUrl})

# --- Заявки и подписки --- #

@teams_bp.route('/<string:team_id>/apply', methods=['POST'])
@jwt_required()
def apply_to_team(team_id):
    """
    Apply to join a team
    ---
    tags:
      - Teams - Applications
    summary: Apply to join a team
    description: Submits an application to join a specific team. A user cannot apply if they are already a member or have a pending application.
    security:
      - bearerAuth: []
    parameters:
      - in: path
        name: team_id
        required: true
        schema:
          type: string
        description: The ID of the team to apply to.
    responses:
      200:
        description: Application submitted successfully.
      400:
        description: Bad request (already a member or has a pending application).
      404:
        description: Team not found.
    """
    current_user_id = get_jwt_identity()
    team = Team.query.get_or_404(team_id)
    user = User.query.get(current_user_id)

    # Проверка, не является ли пользователь уже участником
    if user in team.members:
        return jsonify({"error": "You are already a member of this team"}), 400

    # Проверка, не подавал ли уже заявку
    existing_application = TeamApplication.query.filter_by(teamId=team_id, userId=current_user_id).first()
    if existing_application:
        return jsonify({"error": "You have already applied to this team"}), 400

    application = TeamApplication(userId=current_user_id, teamId=team_id, status='pending')
    db.session.add(application)
    db.session.commit()

    return jsonify({"success": True, "message": "Заявка успешно отправлена"})


@teams_bp.route('/<string:team_id>/applications', methods=['GET'])
@jwt_required()
def get_applications(team_id):
    """
    Get team applications
    ---
    tags:
      - Teams - Applications
    summary: Get team applications (Captain only)
    description: Retrieves a list of users who have pending applications to join the team. This is only visible to the team captain.
    security:
      - bearerAuth: []
    parameters:
      - in: path
        name: team_id
        required: true
        schema:
          type: string
        description: The ID of the team.
    responses:
      200:
        description: A list of user summaries for the applicants.
      403:
        description: Forbidden (only the captain can view applications).
      404:
        description: Team not found.
    """
    current_user_id = get_jwt_identity()
    team = Team.query.get_or_404(team_id)

    if str(team.captainId) != current_user_id:
        return jsonify({"error": "Only the captain can view applications"}), 403

    applications = TeamApplication.query.filter_by(teamId=team_id, status='pending').all()
    users = [User.query.get(app.userId) for app in applications]
    
    return jsonify([user.to_summary_dict() for user in users if user])


@teams_bp.route('/<string:team_id>/applications/<string:user_id>/respond', methods=['POST'])
@jwt_required()
def respond_to_application(team_id, user_id):
    """
    Respond to an application
    ---
    tags:
      - Teams - Applications
    summary: Respond to an application (Captain only)
    description: Accepts or declines a user's application to join the team. This is only available to the team captain.
    security:
      - bearerAuth: []
    parameters:
      - in: path
        name: team_id
        required: true
        schema:
          type: string
        description: The ID of the team.
      - in: path
        name: user_id
        required: true
        schema:
          type: string
        description: The ID of the applicant user.
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required: [action]
            properties:
              action:
                type: string
                enum: [accept, decline]
                description: The action to take on the application.
    responses:
      200:
        description: Action completed successfully.
      400:
        description: Invalid action.
      403:
        description: Forbidden (only captain can respond).
      404:
        description: Application or user not found.
    """
    current_user_id = get_jwt_identity()
    team = Team.query.get_or_404(team_id)

    if str(team.captainId) != current_user_id:
        return jsonify({"error": "Only the captain can respond to applications"}), 403

    application = TeamApplication.query.filter_by(teamId=team_id, userId=user_id, status='pending').first()
    if not application:
        return jsonify({"error": "Application not found"}), 404

    data = request.get_json()
    action = data.get('action')

    if action == 'accept':
        user_to_add = User.query.get(user_id)
        if not user_to_add:
             return jsonify({"error": "User to add not found"}), 404
        team.members.append(user_to_add)
        db.session.delete(application)
        db.session.commit()
        return jsonify({"success": True, "message": "Решение принято: игрок принят"})
    
    elif action == 'decline':
        db.session.delete(application)
        db.session.commit()
        return jsonify({"success": True, "message": "Решение принято: игрок отклонен"})

    else:
        return jsonify({"error": "Invalid action"}), 400


@teams_bp.route('/<string:team_id>/follow', methods=['POST'])
@jwt_required()
def follow_team(team_id):
    """
    Follow or unfollow a team
    ---
    tags:
      - Teams - Following
    summary: Toggle follow status for a team
    description: Allows an authenticated user to follow or unfollow a team.
    security:
      - bearerAuth: []
    parameters:
      - in: path
        name: team_id
        required: true
        schema:
          type: string
        description: The ID of the team to follow/unfollow.
    responses:
      200:
        description: The user's new following status.
        content:
          application/json:
            schema:
              type: object
              properties:
                success:
                  type: boolean
                isFollowing:
                  type: boolean
    """
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
