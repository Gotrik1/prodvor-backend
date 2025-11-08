import os
from minio import Minio
from datetime import timedelta
import uuid

class S3Service:
    def __init__(self):
        self.minio_client = Minio(
            os.getenv('MINIO_ENDPOINT'),
            access_key=os.getenv('MINIO_ACCESS_KEY'),
            secret_key=os.getenv('MINIO_SECRET_KEY'),
            secure=True # Или False, если вы не используете HTTPS
        )
        self.bucket_name = os.getenv('MINIO_BUCKET_NAME')

    def generate_presigned_post_url(self, user_id, content_type):
        object_name = f"uploads/{user_id}/{uuid.uuid4()}"

        post_policy = self.minio_client.presigned_post_policy(
            self.bucket_name,
            object_name,
            expires=timedelta(hours=1),
            # Ограничения на загружаемый файл
            # condition=["content-length-range", 1024, 10485760] # от 1KB до 10MB
        )

        file_url = f"https://{os.getenv('MINIO_ENDPOINT')}/{self.bucket_name}/{object_name}"

        return {
            "url": post_policy['url'],
            "fields": post_policy['form_data'],
            "fileUrl": file_url
        }

s3_service = S3Service()
