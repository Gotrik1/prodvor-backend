from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.s3_service import create_presigned_post_url
from app.models import User
from app import db

uploads_bp = Blueprint('uploads', __name__)

@uploads_bp.route('/uploads/request-url', methods=['POST'])
@jwt_required()
def get_upload_url():
    """Генерирует presigned URL для загрузки файла напрямую в S3-хранилище."""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    file_type = data.get('contentType', 'image/jpeg')

    # Простые проверки
    if not file_type.startswith('image/'):
        return jsonify({"error": "Допускаются только изображения"}), 400

    response = create_presigned_post_url(user_id=current_user_id, file_type=file_type)

    if response:
        return jsonify(response), 200
    else:
        return jsonify({"error": "Не удалось сгенерировать URL для загрузки"}), 500

@uploads_bp.route('/users/avatar', methods=['POST'])
@jwt_required()
def update_avatar():
    """Обновляет URL аватара пользователя после успешной загрузки в S3."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    data = request.get_json()
    file_url = data.get('fileUrl')

    if not file_url:
        return jsonify({"error": "Отсутствует fileUrl"}), 400
    
    # Здесь можно добавить проверку, что домен в file_url соответствует S3_ENDPOINT_URL

    user.avatarUrl = file_url
    db.session.commit()

    return jsonify({"message": "Аватар успешно обновлен", "avatarUrl": user.avatarUrl}), 200
