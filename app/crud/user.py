from sqlalchemy.orm import Session
from sqlalchemy import Table, MetaData
from app.db.session import engine

# Используем рефлексию для получения метаданных таблицы user
meta = MetaData()
# Убираем `autoload=True`, так как `autoload_with` уже активирует рефлексию
user = Table('user', meta, autoload_with=engine)

def get_by_email(db: Session, email: str):
    """
    Получает пользователя по email, используя SQLAlchemy Core и рефлексию.
    Возвращает объект RowProxy, а не ORM-модель.
    """
    query = user.select().where(user.c.email == email)
    result = db.execute(query)
    return result.first()
