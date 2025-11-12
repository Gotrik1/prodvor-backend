from passlib.context import CryptContext

# Временный in-memory черный список для jti токенов
# В продакшене лучше использовать Redis или другую быструю БД
BLACKLIST = set()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def add_to_blacklist(jti: str):
    BLACKLIST.add(jti)

def is_blacklisted(jti: str) -> bool:
    return jti in BLACKLIST
