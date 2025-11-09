from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import s3_service # Изменено: импорт из пакета app
import uuid

uploads_bp = Blueprint('uploads', __name__)

@uploads_bp.route('/request-url', methods=['POST'])
@jwt_required()
def request_upload_url():
    """Создает presigned URL для прямой загрузки файла в S3-совместимое хранилище."""
    user_id = get_jwt_identity()
    data = request.get_json()
    filename = data.get('filename')

    if not filename:
        return jsonify({"error": "filename is required"}), 400

    # Создаем уникальное имя объекта для хранения в S3
    object_name = f"uploads/{user_id}/{uuid.uuid4()}-{filename}"

    try:
        # Вызываем обновленный метод сервиса
        response_data = s3_service.generate_presigned_post_url(object_name)
        if response_data is None:
            # Логирование происходит внутри сервиса
            return jsonify({"error": "Failed to generate presigned URL"}), 500

        # Возвращаем URL и имя объекта клиенту
        response_data['object_name'] = object_name

        return jsonify(response_data)
    except Exception as e:
        # Логирование ошибок здесь также важно
        return jsonify({"error": "An internal error occurred", "message": str(e)}), 500
