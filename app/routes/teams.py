
from flask import Blueprint, jsonify, request
from app import db
from app.models import Team, TeamApplication, User, Sport, TeamMembers, TeamFollowers
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import joinedload
from sqlalchemy import func, desc, asc

teams_bp = Blueprint('teams', __name__)

@teams_bp.route('/teams', methods=['GET'])
def get_teams():
    """
    Get all teams
    ---
    tags:
      - Teams
    parameters:
      - name: city
        in: query
        type: string
        required: false
        description: Filter by city
      - name: sort_by
        in: query
        type: string
        required: false
        description: Sort by attribute (name, followers, rank, createdAt)
      - name: order
        in: query
        type: string
        required: false
        description: Sort order (asc, desc)
      - name: limit
        in: query
        type: integer
        required: false
        description: Limit number of results
      - name: expand
        in: query
        type: string
        required: false
        description: Expand members
    responses:
      200:
        description: Returns a list of all teams
    """
    # Get query parameters
    city = request.args.get('city')
    sort_by = request.args.get('sort_by', 'name') # default sort by name
    order = request.args.get('order', 'asc') # default order asc
    limit = request.args.get('limit', type=int)
    expand_members = request.args.get('expand') == 'members'

    # Base query
    query = Team.query

    # Filtering by city
    if city:
        # Use ilike for case-insensitive partial matching
        query = query.filter(Team.city.ilike(f'%{city}%'))

    # Sorting logic
    order_direction = desc if order.lower() == 'desc' else asc

    if sort_by == 'followers':
        # Join with the followers table, group by team, and order by the count of followers
        query = query.outerjoin(Team.followers).group_by(Team.id).order_by(order_direction(func.count(User.id)))
    elif hasattr(Team, sort_by):
        # Sort by a direct attribute of the Team model (e.g., rank, name, createdAt)
        query = query.order_by(order_direction(getattr(Team, sort_by)))

    # Limiting the number of results
    if limit:
        query = query.limit(limit)

    # Option to expand member details
    if expand_members:
        query = query.options(joinedload(Team.members), joinedload(Team.captain))

    # Execute query
    teams = query.all()

    return jsonify([team.to_dict(expand=expand_members) for team in teams])

@teams_bp.route('/teams', methods=['POST'])
@jwt_required()
def create_team():
    """
    Create a new team
    ---
    tags:
      - Teams
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - name
            - sport_id
            - city
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
      201:
        description: Team created successfully
      400:
        description: Missing data
    """
    data = request.get_json()
    if not data or not all(k in data for k in ('name', 'sport_id', 'city')):
        return jsonify({'error': 'Missing data, required fields: name, sport_id, city'}), 400

    captain_id = get_jwt_identity()
    captain = User.query.get(captain_id)
    if not captain:
        return jsonify({'error': 'Captain user not found'}), 400

    new_team = Team(
        name=data['name'],
        captainId=captain_id,
        sport_id=data['sport_id'],
        city=data['city'],
        logoUrl=data.get('logoUrl')
    )

    db.session.add(new_team)
    db.session.flush()  # Flush to get the new_team.id

    # Add captain to team members
    team_member = TeamMembers.insert().values(userId=new_team.captainId, teamId=new_team.id)
    db.session.execute(team_member)
    
    db.session.commit()
    return jsonify(new_team.to_dict(expand=True)), 201

@teams_bp.route('/teams/<int:team_id>', methods=['GET'])
def get_team(team_id):
    """
    Get a team by ID
    ---
    tags:
      - Teams
    parameters:
      - name: team_id
        in: path
        required: true
        type: integer
    responses:
      200:
        description: Returns a single team
      404:
        description: Team not found
    """
    team = db.session.query(Team).options(joinedload(Team.members), joinedload(Team.captain)).filter_by(id=team_id).first_or_404()
    return jsonify(team.to_dict(expand=True))

@teams_bp.route('/teams/<int:team_id>/follow', methods=['POST'])
@jwt_required()
def toggle_follow_team(team_id):
    """
    Toggle follow a team
    ---
    tags:
      - Teams
    security:
      - Bearer: []
    parameters:
      - name: team_id
        in: path
        required: true
        type: integer
    responses:
      200:
        description: Follow status toggled
      404:
        description: Team or user not found
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    team = Team.query.get_or_404(team_id)

    if not user:
         return jsonify({"error": "User not found"}), 404

    is_already_following = user.followed_teams.filter(TeamFollowers.c.teamId == team_id).first()

    if is_already_following:
        user.followed_teams.remove(team)
        db.session.commit()
        return jsonify({"success": True, "isFollowing": False}), 200
    else:
        user.followed_teams.append(team)
        db.session.commit()
        return jsonify({"success": True, "isFollowing": True}), 200

@teams_bp.route('/teams/<int:team_id>/members/<int:user_id>', methods=['DELETE'])
@jwt_required()
def remove_team_member(team_id, user_id):
    """
    Remove a team member
    ---
    tags:
      - Teams
    security:
      - Bearer: []
    parameters:
      - name: team_id
        in: path
        required: true
        type: integer
      - name: user_id
        in: path
        required: true
        type: integer
    responses:
      200:
        description: Member removed successfully
      400:
        description: Captain cannot remove themselves
      403:
        description: Only the captain can remove members
      404:
        description: Team or member not found
    """
    current_user_id = get_jwt_identity()
    team = db.get_or_404(Team, team_id)

    if team.captainId != int(current_user_id):
        return jsonify({"error": "Forbidden: Only the team captain can remove members."}), 403

    if team.captainId == user_id:
        return jsonify({"error": "Bad Request: Captain cannot remove themselves from the team."}), 400

    member_to_remove = db.session.query(TeamMembers).filter_by(teamId=team_id, userId=user_id).first()

    if not member_to_remove:
        return jsonify({"error": "Not Found: This user is not a member of the team."}), 404

    stmt = TeamMembers.delete().where(TeamMembers.c.userId == user_id).where(TeamMembers.c.teamId == team_id)
    db.session.execute(stmt)
    db.session.commit()

    return jsonify({"success": True, "message": "Player removed successfully"}), 200

@teams_bp.route('/teams/<int:team_id>/apply', methods=['POST'])
@jwt_required()
def apply_to_team(team_id):
    """
    Apply to a team
    ---
    tags:
      - Teams
    security:
      - Bearer: []
    parameters:
      - name: team_id
        in: path
        required: true
        type: integer
    responses:
      200:
        description: Application sent successfully
      400:
        description: You have already applied or are a member
    """
    request.get_json(silent=True)
    user_id = int(get_jwt_identity())
    team = db.get_or_404(Team, team_id)

    existing_application = TeamApplication.query.filter_by(teamId=team_id, userId=user_id, status='pending').first()
    if existing_application:
        return jsonify({"error": "You have already applied to this team"}), 400

    is_member = db.session.query(TeamMembers).filter_by(userId=user_id, teamId=team_id).first()
    if is_member:
        return jsonify({"error": "You are already a member of this team"}), 400

    new_application = TeamApplication(teamId=team_id, userId=user_id)
    db.session.add(new_application)
    db.session.commit()

    return jsonify({"success": True, "message": "Заявка успешно отправлена"}), 200

@teams_bp.route('/teams/<int:team_id>/applications', methods=['GET'])
@jwt_required()
def get_team_applications(team_id):
    """
    Get team applications
    ---
    tags:
      - Teams
    security:
      - Bearer: []
    parameters:
      - name: team_id
        in: path
        required: true
        type: integer
    responses:
      200:
        description: Returns a list of applicants
      403:
        description: Forbidden
    """
    user_id = get_jwt_identity()
    team = db.get_or_404(Team, team_id)

    if team.captainId != int(user_id):
        return jsonify({"error": "Forbidden"}), 403

    applications = TeamApplication.query.filter_by(teamId=team_id, status='pending').all()
    applicants = [User.query.get(app.userId).to_dict() for app in applications]

    return jsonify(applicants), 200

@teams_bp.route('/teams/<int:team_id>/applications/<int:user_id>/respond', methods=['POST'])
@jwt_required()
def respond_to_application(team_id, user_id):
    """
    Respond to a team application
    ---
    tags:
      - Teams
    security:
      - Bearer: []
    parameters:
      - name: team_id
        in: path
        required: true
        type: integer
      - name: user_id
        in: path
        required: true
        type: integer
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - action
          properties:
            action:
              type: string
              description: "accept or decline"
    responses:
      200:
        description: Response sent successfully
      400:
        description: Invalid action
      403:
        description: Forbidden
      404:
        description: Application not found
    """
    captain_id = get_jwt_identity()
    team = db.get_or_404(Team, team_id)

    if team.captainId != int(captain_id):
        return jsonify({"error": "Forbidden"}), 403

    application = TeamApplication.query.filter_by(teamId=team_id, userId=user_id, status='pending').first()
    if not application:
        return jsonify({"error": "Application not found"}), 404

    data = request.get_json()
    action = data.get('action')

    if action not in ['accept', 'decline']:
        return jsonify({"error": "Invalid action"}), 400

    if action == 'accept':
        team_member = TeamMembers.insert().values(userId=user_id, teamId=team_id)
        db.session.execute(team_member)
        db.session.delete(application)
        db.session.commit()
        return jsonify({"success": True, "message": "Решение принято"}), 200
    
    elif action == 'decline':
        db.session.delete(application)
        db.session.commit()
        return jsonify({"success": True, "message": "Решение принято"}), 200
