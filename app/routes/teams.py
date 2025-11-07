
from flask import request, jsonify, Blueprint
from app import db
from app.models import Team, User, TeamApplication, TeamFollowers
from flask_jwt_extended import jwt_required, get_jwt_identity

teams_bp = Blueprint('teams', __name__)

@teams_bp.route('/teams', methods=['GET'])
def get_teams():
    """
    Get all teams
    ---
    tags:
        - Teams
    responses:
        '200':
            description: A list of teams.
    """
    teams = Team.query.all()
    return jsonify([team.to_dict() for team in teams])

@teams_bp.route('/teams/<int:team_id>', methods=['GET'])
def get_team(team_id):
    """
    Get a team by ID
    ---
    tags:
        - Teams
    parameters:
        -   name: team_id
            in: path
            required: true
            type: integer
    responses:
        '200':
            description: A single team.
        '404':
            description: Team not found.
    """
    team = Team.query.get_or_404(team_id)
    return jsonify(team.to_dict(include_members=True))

@teams_bp.route('/teams', methods=['POST'])
@jwt_required()
def create_team():
    """
    Create a new team
    ---
    tags:
        - Teams
    security:
        - bearerAuth: []
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required: [name, sport_id, city]
            properties:
              name:
                type: string
              sport_id:
                type: string
              city:
                type: string
              logoUrl:
                type: string
    responses:
        '201':
            description: Team created successfully.
        '400':
            description: Missing required fields.
    """
    current_user_id = get_jwt_identity()
    data = request.get_json()

    if not data or not data.get('name') or not data.get('sport_id') or not data.get('city'):
        return jsonify({"error": "Missing required fields: name, sport_id, city"}), 400

    new_team = Team(
        name=data['name'],
        game=data['sport_id'], 
        city=data['city'],
        logoUrl=data.get('logoUrl'),
        captainId=current_user_id
    )

    user = User.query.get(current_user_id)
    if user:
        new_team.members.append(user)

    db.session.add(new_team)
    db.session.commit()

    return jsonify(new_team.to_dict(include_members=True)), 201

@teams_bp.route('/teams/<int:team_id>/members/<int:user_id>', methods=['DELETE'])
@jwt_required()
def remove_team_member(team_id, user_id):
    """
    Remove a team member
    ---
    tags:
        - Teams
    security:
        - bearerAuth: []
    parameters:
        -   name: team_id
            in: path
            required: true
            type: integer
        -   name: user_id
            in: path
            required: true
            type: integer
    responses:
        '200':
            description: Player removed successfully.
        '400':
            description: Captain cannot remove themselves.
        '403':
            description: Only the team captain can remove members.
        '404':
            description: Player is not a member of this team.
    """
    current_user_id = get_jwt_identity()
    team = Team.query.get_or_404(team_id)

    if team.captainId != current_user_id:
        return jsonify({"error": "Forbidden: Only the team captain can remove members."}), 403

    if team.captainId == user_id:
        return jsonify({"error": "Bad Request: Captain cannot remove themselves."}), 400

    user_to_remove = User.query.get(user_id)
    if not user_to_remove or user_to_remove not in team.members:
        return jsonify({"error": "Not Found: Player is not a member of this team."}), 404

    team.members.remove(user_to_remove)
    db.session.commit()

    return jsonify({"success": True, "message": "Player removed successfully"})

@teams_bp.route('/teams/<int:team_id>/logo', methods=['POST'])
@jwt_required()
def update_team_logo(team_id):
    """
    Update team logo
    ---
    tags:
        - Teams
    security:
        - bearerAuth: []
    parameters:
        -   name: team_id
            in: path
            required: true
            type: integer
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
    responses:
        '200':
            description: Logo updated successfully.
        '400':
            description: Missing fileUrl.
        '403':
            description: Only the captain can update.
    """
    current_user_id = get_jwt_identity()
    team = Team.query.get_or_404(team_id)

    if team.captainId != current_user_id:
        return jsonify({"error": "Forbidden: Only the team captain can update the logo."}), 403

    data = request.get_json()
    if not data or 'fileUrl' not in data:
        return jsonify({"error": "Missing fileUrl in request body"}), 400

    team.logoUrl = data['fileUrl']
    db.session.commit()

    return jsonify({"message": "Логотип успешно обновлен", "logoUrl": team.logoUrl})


# --- Application and Follow Endpoints ---

@teams_bp.route('/teams/<int:team_id>/apply', methods=['POST'])
@jwt_required()
def apply_to_team(team_id):
    """
    Apply to a team
    ---
    tags:
        - Teams
    security:
        - bearerAuth: []
    parameters:
        -   name: team_id
            in: path
            required: true
            type: integer
    responses:
        '201':
            description: Application sent successfully.
        '409':
            description: Application already sent.
    """
    user_id = get_jwt_identity()
    
    if TeamApplication.query.filter_by(userId=user_id, teamId=team_id).first():
        return jsonify({"error": "Application already sent"}), 409

    application = TeamApplication(userId=user_id, teamId=team_id, status='pending')
    db.session.add(application)
    db.session.commit()
    
    return jsonify({"success": True, "message": "Заявка успешно отправлена"}), 201

@teams_bp.route('/teams/<int:team_id>/applications', methods=['GET'])
@jwt_required()
def get_team_applications(team_id):
    """
    Get team applications
    ---
    tags:
        - Teams
    security:
        - bearerAuth: []
    parameters:
        -   name: team_id
            in: path
            required: true
            type: integer
    responses:
        '200':
            description: A list of user applications.
        '403':
            description: Forbidden.
    """
    current_user_id = get_jwt_identity()
    team = Team.query.get_or_404(team_id)

    if team.captainId != current_user_id:
        return jsonify({"error": "Forbidden"}), 403

    applications = TeamApplication.query.filter_by(teamId=team_id, status='pending').all()
    applicant_ids = [app.userId for app in applications]
    users = User.query.filter(User.id.in_(applicant_ids)).all()

    return jsonify([user.to_dict() for user in users])

@teams_bp.route('/teams/<int:team_id>/applications/<int:user_id>/respond', methods=['POST'])
@jwt_required()
def respond_to_application(team_id, user_id):
    """
    Respond to a team application
    ---
    tags:
        - Teams
    security:
        - bearerAuth: []
    parameters:
        -   name: team_id
            in: path
            required: true
            type: integer
        -   name: user_id
            in: path
            required: true
            type: integer
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
                  enum: ['accept', 'decline']
    responses:
        '200':
            description: Response recorded.
        '400':
            description: Invalid action.
        '403':
            description: Forbidden.
    """
    current_user_id = get_jwt_identity()
    team = Team.query.get_or_404(team_id)

    if team.captainId != current_user_id:
        return jsonify({"error": "Forbidden"}), 403

    application = TeamApplication.query.filter_by(userId=user_id, teamId=team_id).first_or_404()
    data = request.get_json()
    action = data.get('action')

    if action == 'accept':
        user = User.query.get(user_id)
        team.members.append(user)
        db.session.delete(application)
    elif action == 'decline':
        db.session.delete(application)
    else:
        return jsonify({"error": "Invalid action"}), 400

    db.session.commit()
    return jsonify({"success": True, "message": "Решение принято"})

@teams_bp.route('/teams/<int:team_id>/follow', methods=['POST'])
@jwt_required()
def follow_team(team_id):
    """
    Toggle follow a team
    ---
    tags:
        - Teams
    security:
        - bearerAuth: []
    parameters:
        -   name: team_id
            in: path
            required: true
            type: integer
    responses:
        '200':
            description: Follow status toggled.
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    team = Team.query.get_or_404(team_id)

    is_following = db.session.query(TeamFollowers).filter_by(userId=user_id, teamId=team_id).first() is not None

    if is_following:
        stmt = TeamFollowers.delete().where(TeamFollowers.c.userId == user_id, TeamFollowers.c.teamId == team_id)
        db.session.execute(stmt)
        is_following_after = False
    else:
        stmt = TeamFollowers.insert().values(userId=user_id, teamId=team_id)
        db.session.execute(stmt)
        is_following_after = True
        
    db.session.commit()
    return jsonify({"success": True, "isFollowing": is_following_after})
