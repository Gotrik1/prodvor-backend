
import os
import uuid
import traceback
from flask import Blueprint, jsonify, request
from app import db
from app.models import User, PlayerProfile, RefereeProfile, CoachProfile, Sport
from flask_jwt_extended import jwt_required, get_jwt_identity
from supabase import create_client
from werkzeug.datastructures import FileStorage
from werkzeug.security import generate_password_hash

users_bp = Blueprint('users', __name__)

def _get_supabase_client():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        raise ValueError("Supabase URL or Key is not configured on the server.")
    return create_client(url, key)

def _delete_old_file_from_storage(supabase_client, bucket_name, old_url):
    if not old_url:
        return
    try:
        file_path = old_url.split(f'/storage/v1/object/public/{bucket_name}/')[-1]
        if file_path and file_path != old_url:
            print(f"--- Deleting old file: {file_path} from bucket: {bucket_name} ---")
            supabase_client.storage.from_(bucket_name).remove([file_path])
    except Exception as e:
        print(f"--- ERROR deleting old file {old_url}: {e} ---")
        traceback.print_exc()

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
    parameters:
      - name: include_teams
        in: query
        type: boolean
        required: false
        description: Include teams in the response
      - name: include_follows
        in: query
        type: boolean
        required: false
        description: Include followed teams in the response
    responses:
      200:
        description: Returns the current user
      401:
        description: Unauthorized
      404:
        description: User not found
    """
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()

    if not user:
        return jsonify({"msg": "User not found"}), 404

    include_teams_param = request.args.get('include_teams', 'false').lower() == 'true'
    include_follows_param = request.args.get('include_follows', 'false').lower() == 'true'
    return jsonify(user.to_dict(include_teams=include_teams_param, include_follows=include_follows_param)), 200

@users_bp.route('/users', methods=['GET'])
def get_users():
    """
    Get all users
    ---
    tags:
      - Users
    responses:
      200:
        description: Returns a list of all users
    """
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@users_bp.route('/users/<string:user_id>', methods=['GET'])
def get_user(user_id):
    """
    Get a user by ID
    ---
    tags:
      - Users
    parameters:
      - name: user_id
        in: path
        required: true
        type: string
      - name: include_teams
        in: query
        type: boolean
        required: false
        description: Include teams in the response
      - name: include_follows
        in: query
        type: boolean
        required: false
        description: Include followed teams in the response
    responses:
      200:
        description: Returns a single user
      404:
        description: User not found
    """
    if user_id.isdigit():
        user = db.get_or_404(User, int(user_id))
    else:
        user = User.query.filter_by(id=user_id).first_or_404()
    include_teams_param = request.args.get('include_teams', 'false').lower() == 'true'
    include_follows_param = request.args.get('include_follows', 'false').lower() == 'true'
    return jsonify(user.to_dict(include_teams=include_teams_param, include_follows=include_follows_param))

@users_bp.route('/users', methods=['POST'])
def create_user():
    """
    Create a new user
    ---
    tags:
      - Users
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - nickname
            - email
            - role
            - city
            - firstName
            - lastName
            - password
          properties:
            nickname:
              type: string
            email:
              type: string
            role:
              type: string
            city:
              type: string
            firstName:
              type: string
            lastName:
              type: string
            password:
              type: string
            age:
              type: integer
            gender:
              type: string
    responses:
      201:
        description: User created successfully
      400:
        description: Missing data or nickname/email already exists
    """
    data = request.get_json()
    required_fields = ['nickname', 'email', 'role', 'city', 'firstName', 'lastName', 'password']
    if not data or not all(k in data for k in required_fields):
        return jsonify({'error': 'Missing data'}), 400

    if User.query.filter_by(nickname=data['nickname']).first():
        return jsonify({'error': 'Nickname already exists'}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400

    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
    new_user = User(
        nickname=data['nickname'],
        email=data['email'],
        password=hashed_password,
        role=data['role'],
        city=data['city'],
        firstName=data['firstName'],
        lastName=data['lastName'],
        age=data.get('age'),
        gender=data.get('gender')
    )

    role = data.get('role')
    if role == 'Игрок' or role == 'Капитан':
        new_user.player_profile = PlayerProfile()
    elif role == 'Судья':
        new_user.referee_profile = RefereeProfile()
    elif role == 'Тренер':
        new_user.coach_profile = CoachProfile()

    db.session.add(new_user)
    db.session.commit()

    return jsonify(new_user.to_dict()), 201

@users_bp.route('/users/<string:user_id>', methods=['PUT'])
def update_user(user_id):
    """
    Update a user
    ---
    tags:
      - Users
    parameters:
      - name: user_id
        in: path
        required: true
        type: string
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            nickname:
              type: string
            email:
              type: string
            firstName:
              type: string
            lastName:
              type: string
            city:
              type: string
            gender:
              type: string
            age:
              type: integer
            phone:
              type: string
            bio:
              type: string
            avatarUrl:
              type: string
            coverImageUrl:
              type: string
            sports:
              type: array
              items:
                type: string
    responses:
      200:
        description: User updated successfully
      400:
        description: No data provided or nickname/email already exists
      404:
        description: User not found
    """
    if user_id.isdigit():
        user = db.get_or_404(User, int(user_id))
    else:
        user = User.query.filter_by(id=user_id).first_or_404()
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    if 'nickname' in data and data['nickname'] != user.nickname:
        if User.query.filter_by(nickname=data['nickname']).first():
            return jsonify({'error': 'Nickname already exists'}), 400
        user.nickname = data['nickname']

    if 'email' in data and data['email'] != user.email:
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 400
        user.email = data['email']

    user.firstName = data.get('firstName', user.firstName)
    user.lastName = data.get('lastName', user.lastName)
    user.city = data.get('city', user.city)
    user.gender = data.get('gender', user.gender)
    user.age = data.get('age', user.age)
    user.phone = data.get('phone', user.phone)
    user.bio = data.get('bio', user.bio)
    user.avatarUrl = data.get('avatarUrl', user.avatarUrl)
    user.coverImageUrl = data.get('coverImageUrl', user.coverImageUrl)

    if 'sports' in data and isinstance(data['sports'], list):
        user.sports.clear()
        sport_ids = data['sports']
        if sport_ids:
            sports_to_add = Sport.query.filter(Sport.id.in_(sport_ids)).all()
            for sport in sports_to_add:
                user.sports.append(sport)
    
    db.session.commit()
    return jsonify(user.to_dict()), 200

@users_bp.route('/users/<string:user_id>/avatar', methods=['POST'])
def upload_avatar(user_id):
    """
    Upload an avatar for a user
    ---
    tags:
      - Users
    parameters:
      - name: user_id
        in: path
        required: true
        type: string
      - name: avatar
        in: formData
        required: true
        type: file
    responses:
      200:
        description: Avatar uploaded successfully
      400:
        description: No avatar file provided
      500:
        description: An internal error occurred during avatar upload
    """
    if 'avatar' not in request.files:
        return jsonify({'error': 'No avatar file provided'}), 400

    file: FileStorage = request.files['avatar']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        supabase = _get_supabase_client()
        if user_id.isdigit():
            user = db.get_or_404(User, int(user_id))
        else:
            user = User.query.filter_by(id=user_id).first_or_404()
        bucket_name = "avatars"

        _delete_old_file_from_storage(supabase, bucket_name, user.avatarUrl)

        file_bytes = file.read()
        file_ext = file.filename.rsplit('.', 1)[-1].lower()
        file_name = f"{user_id}_{uuid.uuid4()}.{file_ext}"
        
        supabase.storage.from_(bucket_name).upload(
            path=file_name,
            file=file_bytes,
            file_options={"content-type": file.content_type}
        )

        public_url = supabase.storage.from_(bucket_name).get_public_url(file_name)

        user.avatarUrl = public_url
        db.session.commit()

        print(f"--- Successfully uploaded avatar for user {user_id}. URL: {public_url} ---")
        return jsonify(user.to_dict()), 200

    except Exception as e:
        print(f"--- ERROR during avatar upload for user {user_id}: ---")
        traceback.print_exc()
        return jsonify({'error': 'An internal error occurred during avatar upload.', 'details': str(e)}), 500

@users_bp.route('/users/<string:user_id>/cover', methods=['POST'])
def upload_cover(user_id):
    """
    Upload a cover image for a user
    ---
    tags:
      - Users
    parameters:
      - name: user_id
        in: path
        required: true
        type: string
      - name: cover
        in: formData
        required: true
        type: file
    responses:
      200:
        description: Cover image uploaded successfully
      400:
        description: No cover file provided
      500:
        description: An internal error occurred during cover upload
    """
    if 'cover' not in request.files:
        return jsonify({'error': 'No cover file provided'}), 400

    file: FileStorage = request.files['cover']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        supabase = _get_supabase_client()
        if user_id.isdigit():
            user = db.get_or_404(User, int(user_id))
        else:
            user = User.query.filter_by(id=user_id).first_or_404()
        bucket_name = "covers"

        _delete_old_file_from_storage(supabase, bucket_name, user.coverImageUrl)

        file_bytes = file.read()
        file_ext = file.filename.rsplit('.', 1)[-1].lower()
        file_name = f"{user_id}_{uuid.uuid4()}.{file_ext}"
        
        supabase.storage.from_(bucket_name).upload(
            path=file_name,
            file=file_bytes,
            file_options={"content-type": file.content_type}
        )

        public_url = supabase.storage.from_(bucket_name).get_public_url(file_name)

        user.coverImageUrl = public_url
        db.session.commit()

        print(f"--- Successfully uploaded cover for user {user_id}. URL: {public_url} ---")
        return jsonify(user.to_dict()), 200

    except Exception as e:
        print(f"--- ERROR during cover upload for user {user_id}: ---")
        traceback.print_exc()
        return jsonify({'error': 'An internal error occurred during cover upload.', 'details': str(e)}), 500
