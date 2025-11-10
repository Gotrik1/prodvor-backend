
from apiflask import APIBlueprint
from flask import request, jsonify, abort
from flask_jwt_extended import jwt_required, current_user
from app import s3_service
import uuid

uploads_bp = APIBlueprint('uploads', __name__, url_prefix='/api/v1/uploads')

@uploads_bp.route('/request-url', methods=['POST'])
@uploads_bp.doc(operation_id='createUploadUrl')
@jwt_required()
def request_upload_url():
    """Создает presigned URL для прямой загрузки файла в S3-совместимое хранилище."""
    # Используем current_user, предоставленный flask-jwt-extended
    data = request.get_json()
    filename = data.get('filename')

    if not filename:
        abort(400, description="filename is required")

    object_name = f"uploads/{current_user.id}/{uuid.uuid4()}-{filename}"

    try:
        response_data = s3_service.generate_presigned_post_url(object_name)
        if response_data is None:
            abort(500, description="Failed to generate presigned URL")

        response_data['object_name'] = object_name

        return jsonify(response_data)
    except Exception as e:
        abort(500, description=f"An internal error occurred: {str(e)}")
