import os
from minio import Minio
from minio.error import S3Error
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class S3Service:
    """Сервис для взаимодействия с S3-совместимым хранилищем (Minio)."""
    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Инициализирует сервис с конфигурацией из Flask приложения."""
        try:
            endpoint = app.config['S3_ENDPOINT']
            access_key = app.config['S3_ACCESS_KEY']
            secret_key = app.config['S3_SECRET_KEY']
            secure = app.config.get('S3_SECURE', False)

            self.minio_client = Minio(
                endpoint=endpoint,
                access_key=access_key,
                secret_key=secret_key,
                secure=secure
            )
            self.bucket_name = app.config['S3_BUCKET_NAME']
            
            # Проверка существования бакета и его создание при необходимости
            found = self.minio_client.bucket_exists(self.bucket_name)
            if not found:
                self.minio_client.make_bucket(self.bucket_name)
                logger.info(f"Bucket '{self.bucket_name}' created.")
            else:
                logger.info(f"Bucket '{self.bucket_name}' already exists.")

        except S3Error as e:
            logger.error(f"Error initializing Minio client or bucket: {e}")
            # В случае ошибки инициализации, можно либо выбросить исключение,
            # либо оставить self.minio_client = None, чтобы приложение могло запуститься
            # для выполнения других команд (например, db миграций).
            self.minio_client = None
            self.bucket_name = None
        except KeyError as e:
            logger.error(f"Missing S3 configuration in Flask app config: {e}")
            self.minio_client = None
            self.bucket_name = None

    def generate_presigned_post_url(self, object_name):
        """Генерирует presigned URL для загрузки (POST) объекта."""
        if not self.minio_client:
            logger.error("Minio client not initialized. Cannot generate URL.")
            return None
        try:
            # Устанавливаем политику для presigned POST URL
            # В данном случае, разрешаем загрузку объекта с указанным именем
            response = self.minio_client.presigned_post_policy(
                self.bucket_name,
                object_name,
                expires=3600  # 1 час
            )
            return response
        except S3Error as e:
            logger.error(f"Error generating presigned POST URL: {e}")
            return None
