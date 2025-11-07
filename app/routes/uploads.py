
import os
import uuid
from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from minio import Minio
from datetime import timedelta

uploads_bp = Blueprint('uploads', __name__)

# MinIO Client Initialization
minio_client = Minio(
    os.environ.get("MINIO_ENDPOINT"),
    access_key=os.environ.get("MINIO_ACCESS_KEY"),
    secret_key=os.environ.get("MINIO_SECRET_KEY"),
    secure=os.environ.get("MINIO_SECURE", "true").lower() == "true"
)

@uploads_bp.route('/uploads/request-url', methods=['POST'])
@jwt_required()
def request_upload_url():
    user_id = get_jwt_identity()
    content_type = request.json.get('contentType', 'application/octet-stream')
    bucket_name = os.environ.get("MINIO_BUCKET")
    
    if not bucket_name:
        return jsonify({"error": "MinIO bucket not configured"}), 500

    # Generate a unique object name
    object_name = f"uploads/{user_id}/{uuid.uuid4()}-{content_type.split('/')[-1]}"

    try:
        # Check if bucket exists, create if not
        found = minio_client.bucket_exists(bucket_name)
        if not found:
            minio_client.make_bucket(bucket_name)

        # Generate presigned POST policy
        post_policy = minio_client.presigned_post_policy(
            bucket_name,
            object_name,
            expires=timedelta(minutes=15),
            conditions=None, # You can add conditions here
            user_metadata=None,
        )

        # Construct the final file URL
        file_url = f"https://{os.environ.get('MINIO_ENDPOINT')}/{bucket_name}/{object_name}"

        return jsonify({
            "url": post_policy['url'],
            "fields": post_policy['form_data'],
            "fileUrl": file_url
        })

    except Exception as e:
        print(f"Error generating presigned URL: {e}")
        return jsonify({"error": "Could not generate upload URL."}), 500
