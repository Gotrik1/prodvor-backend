
# from flask import Blueprint, request, jsonify
# from minio import Minio
# from minio.error import S3Error
# import os
# from dotenv import load_dotenv
# from datetime import timedelta
# from app.models import Upload
# from app import db
# from flask_jwt_extended import jwt_required, get_jwt_identity

# load_dotenv()

# uploads_bp = Blueprint('uploads', __name__)

# # Инициализация MinIO клиента
# minio_client = None
# # try:
# #     minio_client = Minio(
# #         os.getenv("S3_ENDPOINT_URL"),
# #         access_key=os.getenv("S3_ACCESS_KEY"),
# #         secret_key=os.getenv("S3_SECRET_KEY"),
# #         secure=os.getenv("S3_SECURE", "true").lower() == "true"
# #     )
# # except Exception as e:
# #     print(f"Error initializing MinIO client: {e}")


# @uploads_bp.route('/uploads/request-url', methods=['POST'])
# @jwt_required()
# def request_upload_url():
#     # if not minio_client:
#     #     return jsonify({"error": "S3 storage is not configured"}), 500

#     # data = request.get_json()
#     # filename = data.get('filename')
#     # folder = data.get('folder', 'general') 
#     # content_type = data.get('contentType', 'application/octet-stream')
#     # userId = get_jwt_identity()

#     # if not filename:
#     #     return jsonify({"error": "Filename is required"}), 400

#     # bucket_name = os.getenv("S3_BUCKET_NAME")
#     # object_name = f"{folder}/{userId}/{filename}"

#     # try:
#     #     # Проверяем, существует ли бакет, и создаем его, если нет
#     #     found = minio_client.bucket_exists(bucket_name)
#     #     if not found:
#     #         minio_client.make_bucket(bucket_name)

#     #     # Генерируем presigned URL для загрузки
#     #     presigned_url = minio_client.presigned_put_object(
#     #         bucket_name,
#     #         object_name,
#     #         expires=timedelta(hours=1),
#     #     )

#     #     # Сохраняем информацию о файле в БД
#     #     new_upload = Upload(
#     #         userId=userId,
#     #         bucket=bucket_name,
#     #         objectName=object_name,
#     #         status='pending'
#     #     )
#     #     db.session.add(new_upload)
#     #     db.session.commit()

#     #     return jsonify({
#     #         "uploadUrl": presigned_url,
#     #         "fileId": new_upload.id,
#     #         "objectName": object_name
#     #     })

#     # except S3Error as exc:
#     #     return jsonify({"error": str(exc)}), 500
#     pass
