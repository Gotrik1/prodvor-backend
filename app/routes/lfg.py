from apiflask import APIBlueprint
from flask import request, jsonify
from app.models import LfgPost, db, User, Team, Sport
from app.utils.decorators import jwt_required

lfg_bp = APIBlueprint('lfg_bp', __name__)

@lfg_bp.route('/lfg', methods=['GET'])
def get_lfg_posts():
    """
    Get all LFG posts with optional filters
    ---
    tags:
      - LFG (Looking for Group)
    summary: Get all LFG posts
    description: Retrieves a list of all LFG posts, with optional query parameters for filtering.
    parameters:
      - in: query
        name: type
        schema:
          type: string
          enum: [player, team]
        description: Filter by post type (player looking for team, or team looking for player).
      - in: query
        name: sportId
        schema:
          type: string
        description: Filter by sport ID.
      - in: query
        name: role
        schema:
          type: string
        description: Filter by required player role (e.g., 'goalkeeper').
    responses:
      200:
        description: A list of LFG posts.
    """
    args = request.args
    query = LfgPost.query

    if 'type' in args:
        query = query.filter_by(type=args['type'])
    if 'sportId' in args:
        query = query.filter_by(sportId=args['sportId'])
    if 'role' in args:
        query = query.filter(LfgPost.requiredRole.ilike(f"%{args['role']}%"))

    posts = query.order_by(LfgPost.createdAt.desc()).all()
    return jsonify([post.to_dict() for post in posts]), 200


@lfg_bp.route('/lfg', methods=['POST'])
@jwt_required
def create_lfg_post(current_user):
    """
    Create a new LFG post
    ---
    tags:
      - LFG (Looking for Group)
    summary: Create a new LFG post
    description: >
      Creates a new LFG post. User must be authenticated.
      If the post type is 'team', the user must be the captain of the specified team.
    security:
      - bearerAuth: []
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - type
              - sportId
              - requiredRole
              - message
            properties:
              type:
                type: string
                enum: [player, team]
                description: The type of LFG post.
              teamId:
                type: integer
                description: The ID of the team (required if type is 'team').
              sportId:
                type: string
                description: The ID of the sport.
              requiredRole:
                type: string
                description: The role required (e.g., 'forward', 'defender').
                example: "Goalkeeper"
              message:
                type: string
                description: A message for the post.
                example: "Looking for a team for the weekend tournament."
    responses:
      201:
        description: LFG post created successfully.
      400:
        description: Bad request (missing fields or invalid type).
      403:
        description: Forbidden (user is not the captain of the team).
      404:
        description: Not found (sport or team not found).
    """
    data = request.get_json()

    # Валидация обязательных полей
    if not all(key in data for key in ['type', 'sportId', 'requiredRole', 'message']):
        return jsonify({"error": "Missing required fields"}), 400

    # Проверка типа
    if data['type'] not in ['player', 'team']:
        return jsonify({"error": "Invalid type specified"}), 400
        
    # Проверка существования sportId
    sport = Sport.query.get(data['sportId'])
    if not sport:
        return jsonify({"error": "Sport not found"}), 404

    # Если тип 'team', teamId обязателен и должен существовать
    team = None
    if data['type'] == 'team':
        if 'teamId' not in data:
            return jsonify({"error": "teamId is required for type 'team'"}), 400
        team = Team.query.get(data['teamId'])
        if not team:
            return jsonify({"error": "Team not found"}), 404
        # Проверка, является ли пользователь капитаном команды
        if team.captainId != current_user.id:
            return jsonify({"error": "Only the team captain can create a 'team' LFG post"}), 403


    new_post = LfgPost(
        type=data['type'],
        authorId=current_user.id,
        teamId=data.get('teamId'),
        sportId=data['sportId'],
        requiredRole=data['requiredRole'],
        message=data['message']
    )

    db.session.add(new_post)
    db.session.commit()

    return jsonify(new_post.to_dict()), 201
