import hashlib

def hash_token(token):
    """Создает SHA-256 хеш из строки токена."""
    return hashlib.sha256(token.encode()).hexdigest()
