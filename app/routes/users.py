
from flask import request, jsonify, Blueprint
from app import db
from app.models import User, Sport
from flask_jwt_extended import jwt_required, get_jwt_identity

users_bp = Blueprint('users', __name__)

@users_bp.route('/users', methods=['GET'])
def get_users():
    """
    Get all users
    ---
    tags:
        - Users
    responses:
        '200':
            description: A list of users.
    """
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@users_bp.route('/users/me', methods=['GET'])
@jwt_required()
def get_me():
    """
    Get current user
    ---
    tags:
        - Users
    security:
        - bearerAuth: []
    responses:
        '200':
            description: The current user's profile.
        '404':
            description: User not found.
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    include_teams = request.args.get('include_teams', 'false').lower() == 'true'
    return jsonify(user.to_dict(include_teams=include_teams, include_sports=True))

@users_bp.route('/users/<string:user_id>', methods=['GET'])
def get_user(user_id):
    """
    Get a user by ID
    ---
    tags:
        - Users
    parameters:
        -   name: user_id
            in: path
            required: true
            type: string
    responses:
        '200':
            description: A single user's profile.
        '404':
            description: User not found.
    """
    user = User.query.get_or_404(user_id)
    include_teams = request.args.get('include_teams', 'false').lower() == 'true'
    return jsonify(user.to_dict(include_teams=include_teams, include_sports=True))

@users_bp.route('/users/<string:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """
    Update a user
    ---
    tags:
        - Users
    security:
        - bearerAuth: []
    parameters:
        -   name: user_id
            in: path
            required: true
            type: string
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              nickname:
                type: string
              city:
                type: string
              sports:
                type: array
                items:
                  type: string
    responses:
        '200':
            description: User updated successfully.
        '400':
            description: No data provided.
        '403':
            description: Forbidden.
    """
    current_user_id = get_jwt_identity()
    user_to_update = User.query.get_or_404(user_id)
    current_user = User.query.get(current_user_id)

    if str(user_to_update.id) != current_user_id and (not current_user or current_user.role != 'admin'):
        return jsonify({"error": "Forbidden"}), 403

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    # Prevent users from changing their own role, but allow admins to do so
    if 'role' in data and (str(user_to_update.id) != current_user_id or (current_user and current_user.role != 'admin')):
        return jsonify({"error": "You cannot change your own role."}), 403
    
    if 'role' in data and current_user and current_user.role == 'admin':
        user_to_update.role = data.get('role', user_to_update.role)

    user_to_update.nickname = data.get('nickname', user_to_update.nickname)
    user_to_update.city = data.get('city', user_to_update.city)
    user_to_update.firstName = data.get('firstName', user_to_update.firstName)
    user_to_update.lastName = data.get('lastName', user_to_update.lastName)
    user_to_update.gender = data.get('gender', user_to_update.gender)
    user_to_update.bio = data.get('bio', user_to_update.bio)
    user_to_update.birthDate = data.get('birthDate', user_to_update.birthDate)


    if 'sports' in data and isinstance(data['sports'], list):
        user_to_update.sports.clear()
        # Assuming sports are sent as a list of sport IDs (which are now UUIDs)
        sports_to_add = Sport.query.filter(Sport.id.in_(data['sports'])).all()
        for sport in sports_to_add:
            user_to_update.sports.append(sport)
    
    db.session.commit()
    return jsonify(user_to_update.to_dict(include_teams=True, include_sports=True))

@users_bp.route('/users/avatar', methods=['POST'])
@jwt_required()
def update_avatar():
    """
    Upload an avatar for a user
    ---
    tags:
        - Users
    security:
        - bearerAuth: []
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
            description: Avatar updated successfully.
        '400':
            description: Missing fileUrl.
        '404':
            description: User not found.
    """
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

