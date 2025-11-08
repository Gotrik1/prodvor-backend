from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.s3_service import s3_service

uploads_bp = Blueprint('uploads', __name__)

@uploads_bp.route('/request-url', methods=['POST'])
@jwt_required()
def request_upload_url():
    """Создает presigned URL для прямой загрузки файла в S3-совместимое хранилище."""
    user_id = get_jwt_identity()
    data = request.get_json()
    content_type = data.get('contentType')

    if not content_type:
        return jsonify({"error": "contentType is required"}), 400

    try:
        response_data = s3_service.generate_presigned_post_url(user_id, content_type)
        return jsonify(response_data)
    except Exception as e:
        # Здесь хорошо бы логировать ошибку
        return jsonify({"error": str(e)}), 500
