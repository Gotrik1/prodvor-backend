from sqlalchemy.orm import Session
from sqlalchemy import text

def get_by_email(db: Session, email: str):
    # кавычки вокруг "user" — как во Flask/PG, т.к. имя зарезервировано
    q = text('SELECT * FROM "user" WHERE email = :email LIMIT 1')
    # mappings() → возвращает dict-like строки (не Row)
    row = db.execute(q, {"email": email}).mappings().first()
    return row  # None | dict с ключами как имена колонок
