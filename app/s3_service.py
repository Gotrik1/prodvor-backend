import boto3
from botocore.exceptions import ClientError
from botocore.config import Config
from flask import current_app
import logging
import uuid

def get_s3_client():
    """Создает и возвращает клиент boto3 для работы с S3-хранилищем."""
    return boto3.client(
        's3',
        endpoint_url=current_app.config['S3_ENDPOINT_URL'],
        aws_access_key_id=current_app.config['S3_ACCESS_KEY_ID'],
        aws_secret_access_key=current_app.config['S3_SECRET_ACCESS_KEY'],
        config=Config(signature_version='s3v4')
    )

def generate_presigned_put_url(bucket_name, object_key, content_type, expiration=3600):
    """
    Генерирует presigned URL для загрузки файла методом PUT.
    Возвращает URL-строку или None в случае ошибки.
    """
    s3_client = get_s3_client()
    try:
        url = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': bucket_name,
                'Key': object_key,
                'ContentType': content_type
            },
            ExpiresIn=expiration
        )
    except ClientError as e:
        logging.error(f"Ошибка генерации presigned PUT URL: {e}")
        return None
    return url

def verify_upload(bucket_name, object_key, expected_size):
    """
    Проверяет существование и размер объекта в S3.
    Возвращает True, если проверка прошла, иначе False.
    """
    s3_client = get_s3_client()
    try:
        response = s3_client.head_object(Bucket=bucket_name, Key=object_key)
        
        # Проверяем, совпадает ли реальный размер файла с ожидаемым
        if response['ContentLength'] != expected_size:
            logging.error(f"Размер файла {object_key} не совпадает: "
                          f"ожидался {expected_size}, получен {response['ContentLength']}")
            return False
            
        return True
    except ClientError as e:
        # Если объект не найден, head_object выдаст ошибку 404, которая попадет сюда
        logging.error(f"Ошибка проверки файла {object_key} в S3: {e}")
        return False

def create_presigned_post_url(user_id, file_type='image/jpeg', expiration=3600):
    """
    Генерирует presigned URL для загрузки файла методом POST.
    Возвращает словарь с URL и полями для формы, или None в случае ошибки.
    (Оставлено для обратной совместимости)
    """
    s3_client = get_s3_client()
    bucket_name = current_app.config['S3_BUCKET_NAME']
    
    # Генерируем уникальное имя файла, чтобы избежать конфликтов
    file_key = f"users/{user_id}/uploads/{uuid.uuid4().hex}.jpg"

    try:
        response = s3_client.generate_presigned_post(
            Bucket=bucket_name,
            Key=file_key,
            Fields={"Content-Type": file_type},
            Conditions=[["content-length-range", 100, 10485760]], # от 100 байт до 10 МБ
            ExpiresIn=expiration
        )
        # Добавляем к ответу полный URL файла, который будет после загрузки
        response['fileUrl'] = f"{current_app.config['S3_ENDPOINT_URL']}/{bucket_name}/{file_key}"
        response['fileKey'] = file_key

    except ClientError as e:
        logging.error(f"Ошибка генерации presigned POST URL: {e}")
        return None

    return response
