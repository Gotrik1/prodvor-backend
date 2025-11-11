from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import crud, models, schemas
from app.dependencies import get_db, get_current_user

router = APIRouter()

@router.post("", response_model=schemas.Post, dependencies=[Depends(get_current_user)])
async def create_post(
    *, 
    db: Session = Depends(get_db),
    post_in: schemas.PostCreate,
    current_user: models.User = Depends(get_current_user)
):
    # The author_id is already in post_in from the request
    return await crud.post.create(db=db, obj_in=post_in)

@router.get("/{post_id}", response_model=schemas.Post)
def read_post(
    post_id: int,
    db: Session = Depends(get_db)
):
    return crud.post.get(db=db, id=post_id)

@router.get("", response_model=list[schemas.Post])
def read_posts(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    return crud.post.get_multi(db, skip=skip, limit=limit)

@router.put("/{post_id}", response_model=schemas.Post, dependencies=[Depends(get_current_user)])
async def update_post(
    *,
    db: Session = Depends(get_db),
    post_id: int,
    post_in: schemas.PostUpdate,
    current_user: models.User = Depends(get_current_user)
):
    post = await crud.post.get(db=db, id=post_id)
    # Add authorization check here if needed
    return await crud.post.update(db=db, db_obj=post, obj_in=post_in)

@router.delete("/{post_id}", response_model=schemas.Post, dependencies=[Depends(get_current_user)])
async def delete_post(
    *,
    db: Session = Depends(get_db),
    post_id: int,
    current_user: models.User = Depends(get_current_user)
):
    post = await crud.post.get(db=db, id=post_id)
    # Add authorization check here if needed
    return await crud.post.remove(db=db, id=post_id)
