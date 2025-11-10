from pydantic import BaseModel, Field
from typing import List, TypeVar, Generic

# Это позволяет нам использовать дженерики в Pydantic
T = TypeVar('T')

class PaginationMeta(BaseModel):
    page: int = Field(..., description="Текущая страница")
    per_page: int = Field(..., description="Элементов на странице")
    total: int = Field(..., description="Всего элементов")
    pages: int = Field(..., description="Всего страниц")

class PaginatedResponse(Generic[T], BaseModel):
    data: List[T] = Field(..., description="Список элементов")
    meta: PaginationMeta = Field(..., description="Мета-информация о пагинации")
