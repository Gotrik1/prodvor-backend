from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Upload
from app.s3_service import generate_presigned_put_url, verify_upload
import uuid
from datetime import datetime, timedelta, timezone

uploads_bp = Blueprint('uploads', __name__, url_prefix='/api/v1/media/upload')

# --- Конфигурация (можно вынести в config.py) ---
ALLOWED_MIME_TYPES = {
    'image/jpeg': 'jpg',
    'image/png': 'png',
    'image/webp': 'webp',
    'video/mp4': 'mp4',
    'video/quicktime': 'mov'
}
MAX_FILE_SIZE_MB = 100
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
PRESIGNED_URL_TTL_SECONDS = 900  # 15 минут

@uploads_bp.route('/init', methods=['POST'])
@jwt_required()
def init_upload():
    """
    Этап 1: Инициализация сессии загрузки файла.
    Клиент запрашивает "разрешение" на загрузку, предоставляя метаданные файла.
    """
    current_user_id = get_jwt_identity()
    data = request.get_json()

    # 1. Валидация входных данных
    content_type = data.get('content_type')
    size = data.get('size')
    file_hash = data.get('hash') # SHA-256 хэш файла (опционально)

    if not all([content_type, size]):
        return jsonify({"msg": "Отсутствуют обязательные поля: content_type, size"}), 400

    if content_type not in ALLOWED_MIME_TYPES:
        return jsonify({"msg": f"Недопустимый тип файла: {content_type}"}), 400

    if not isinstance(size, int) or not (0 < size <= MAX_FILE_SIZE_BYTES):
        return jsonify({"msg": f"Недопустимый размер файла. Максимум: {MAX_FILE_SIZE_MB}MB"}), 400

    # 2. Формирование безопасного пути в S3
    file_extension = ALLOWED_MIME_TYPES[content_type]
    file_key = f"users/{current_user_id}/uploads/{uuid.uuid4().hex}.{file_extension}"
    
    # Можно использовать кастомное имя бакета или из конфига
    bucket_name = data.get('bucket', current_app.config['S3_BUCKET_NAME'])

    # 3. Создание "черновика" в базе данных
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=PRESIGNED_URL_TTL_SECONDS)
    
    new_upload = Upload(
        user_id=current_user_id,
        path=file_key,
        content_type=content_type,
        size=size,
        file_hash=file_hash,
        status='initiated',
        expires_at=expires_at
    )
    db.session.add(new_upload)
    db.session.commit()

    # 4. Генерация presigned URL для PUT-запроса
    upload_url = generate_presigned_put_url(
        bucket_name=bucket_name,
        object_key=file_key,
        content_type=content_type,
        expiration=PRESIGNED_URL_TTL_SECONDS
    )

    if not upload_url:
        new_upload.status = 'failed'
        db.session.commit()
        return jsonify({"msg": "Не удалось сгенерировать URL для загрузки"}), 500

    # 5. Возвращаем ответ клиенту
    return jsonify({
        "uploadId": new_upload.id,
        "uploadUrl": upload_url,
        "method": "PUT",
        "headers": {
            "Content-Type": content_type
        },
        "path": file_key,
        "expiresIn": PRESIGNED_URL_TTL_SECONDS
    }), 201


@uploads_bp.route('/complete', methods=['POST'])
@jwt_required()
def complete_upload():
    """
    Этап 3: Верификация и завершение загрузки.
    Клиент сообщает, что завершил прямую загрузку в S3.
    Бэкенд должен проверить этот факт, не доверяя клиенту.
    """
    current_user_id = get_jwt_identity()
    data = request.get_json()

    upload_id = data.get('uploadId')
    path = data.get('path')

    if not all([upload_id, path]):
        return jsonify({"msg": "Отсутствуют обязательные поля: uploadId, path"}), 400

    # 1. Находим "черновик" в базе данных
    upload_session = Upload.query.filter_by(id=upload_id, user_id=current_user_id, status='initiated').first()

    if not upload_session:
        # Проверяем, может уже завершили
        already_completed = Upload.query.filter_by(id=upload_id, status='uploaded').first()
        if already_completed:
             return jsonify({"msg": "Загрузка уже была успешно завершена"}), 200
        return jsonify({"msg": "Сессия загрузки не найдена или уже истекла"}), 404
        
    if upload_session.path != path:
         return jsonify({"msg": "Несоответствие пути файла"}), 400

    # 2. Не доверяем клиенту. Сами проверяем факт загрузки в S3.
    bucket_name = data.get('bucket', current_app.config['S3_BUCKET_NAME'])
    
    if not verify_upload(bucket_name, path, upload_session.size):
        upload_session.status = 'failed'
        db.session.commit()
        return jsonify({"msg": "Проверка файла в хранилище не удалась. Объект не найден или его размер не совпадает."}), 400

    # 3. Обновляем статус в БД - успех!
    upload_session.status = 'uploaded'
    db.session.commit()
    
    # 4. Формируем финальный ответ
    # В реальном приложении здесь можно создать запись в основной таблице media,
    # запустить обработку (ресайз, etc.) и вернуть постоянную ссылку.
    
    public_url = f"{current_app.config['S3_ENDPOINT_URL']}/{bucket_name}/{path}"
    
    return jsonify({
        "mediaId": upload_session.id, # В данном случае используем uploadId как mediaId
        "publicUrl": public_url,
        "path": path,
        "contentType": upload_session.content_type,
        "size": upload_session.size,
        "status": "completed"
    }), 200
