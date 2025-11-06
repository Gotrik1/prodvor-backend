
import os
import uuid
import traceback
from flask import Blueprint, jsonify, request
from app import db
from app.models import User, PlayerProfile, RefereeProfile, CoachProfile, Sport
from flask_jwt_extended import jwt_required, current_user
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
    if not current_user:
        return jsonify({"msg": "User not found or invalid token"}), 404
    include_teams_param = request.args.get('include_teams', 'false').lower() == 'true'
    include_follows_param = request.args.get('include_follows', 'false').lower() == 'true'
    return jsonify(current_user.to_dict(include_teams=include_teams_param, include_follows=include_follows_param)), 200

@users_bp.route('/users/me', methods=['PUT'])
@jwt_required()
def update_me():
    """
    Update current user
    ---
    tags:
      - Users
    security:
      - bearerAuth: []
    # ... (swagger docs)
    """
    if not current_user:
        return jsonify({"msg": "User not found or invalid token"}), 404
    
    user = current_user
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

@users_bp.route('/users/me/avatar', methods=['POST'])
@jwt_required()
def upload_my_avatar():
    """
    Upload an avatar for the current user
    ---
    tags:
      - Users
    security:
      - bearerAuth: []
    # ... (swagger docs)
    """
    if 'avatar' not in request.files:
        return jsonify({'error': 'No avatar file provided'}), 400
    
    file: FileStorage = request.files['avatar']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if not current_user:
        return jsonify({"msg": "User not found or invalid token"}), 404

    try:
        supabase = _get_supabase_client()
        user = current_user
        bucket_name = "avatars"

        _delete_old_file_from_storage(supabase, bucket_name, user.avatarUrl)

        file_bytes = file.read()
        file_ext = file.filename.rsplit('.', 1)[-1].lower()
        file_name = f"{user.id}_{uuid.uuid4()}.{file_ext}"
        
        supabase.storage.from_(bucket_name).upload(
            path=file_name,
            file=file_bytes,
            file_options={"content-type": file.content_type}
        )

        public_url = supabase.storage.from_(bucket_name).get_public_url(file_name)

        user.avatarUrl = public_url
        db.session.commit()

        print(f"--- Successfully uploaded avatar for user {user.id}. URL: {public_url} ---")
        return jsonify(user.to_dict()), 200

    except Exception as e:
        print(f"--- ERROR during avatar upload for user {user.id}: ---")
        traceback.print_exc()
        return jsonify({'error': 'An internal error occurred during avatar upload.', 'details': str(e)}), 500

@users_bp.route('/users/me/cover', methods=['POST'])
@jwt_required()
def upload_my_cover():
    """
    Upload a cover image for the current user
    ---
    # ... (swagger docs)
    """
    if 'cover' not in request.files:
        return jsonify({'error': 'No cover file provided'}), 400

    file: FileStorage = request.files['cover']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if not current_user:
        return jsonify({"msg": "User not found or invalid token"}), 404

    try:
        supabase = _get_supabase_client()
        user = current_user
        bucket_name = "covers"

        _delete_old_file_from_storage(supabase, bucket_name, user.coverImageUrl)

        file_bytes = file.read()
        file_ext = file.filename.rsplit('.', 1)[-1].lower()
        file_name = f"{user.id}_{uuid.uuid4()}.{file_ext}"
        
        supabase.storage.from_(bucket_name).upload(
            path=file_name,
            file=file_bytes,
            file_options={"content-type": file.content_type}
        )

        public_url = supabase.storage.from_(bucket_name).get_public_url(file_name)

        user.coverImageUrl = public_url
        db.session.commit()

        print(f"--- Successfully uploaded cover for user {user.id}. URL: {public_url} ---")
        return jsonify(user.to_dict()), 200

    except Exception as e:
        print(f"--- ERROR during cover upload for user {user.id}: ---")
        traceback.print_exc()
        return jsonify({'error': 'An internal error occurred during cover upload.', 'details': str(e)}), 500


# --- Публичные эндпоинты --- 

@users_bp.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@users_bp.route('/users/<string:user_id>', methods=['GET'])
def get_user(user_id):
    if user_id.isdigit():
        user = db.get_or_404(User, int(user_id))
    else:
        # Оставляем возможность поиска по строковому ID, если такая логика где-то нужна
        user = User.query.filter_by(id=user_id).first_or_404()
    include_teams_param = request.args.get('include_teams', 'false').lower() == 'true'
    include_follows_param = request.args.get('include_follows', 'false').lower() == 'true'
    return jsonify(user.to_dict(include_teams=include_teams_param, include_follows=include_follows_param))

@users_bp.route('/users', methods=['POST'])
def create_user():
    # Этот эндпоинт, вероятно, должен быть публичным (регистрация) или только для админов
    # Оставляю как есть, но это требует внимания в будущем
    data = request.get_json()
    # ... (логика создания пользователя) 
    # ...
    pass # Сокращено для краткости
