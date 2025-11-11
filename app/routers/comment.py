from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import crud, models, schemas
from app.dependencies import get_db, get_current_user

router = APIRouter()

@router.post("", response_model=schemas.Comment, dependencies=[Depends(get_current_user)])
def create_comment(
    *, 
    db: Session = Depends(get_db),
    comment_in: schemas.CommentCreate,
    current_user: models.User = Depends(get_current_user)
):
    return crud.comment.create_with_user_and_post(db=db, obj_in=comment_in, user_id=current_user.id, post_id=comment_in.post_id)

@router.get("/{comment_id}", response_model=schemas.Comment)
def read_comment(
    comment_id: int,
    db: Session = Depends(get_db)
):
    return crud.comment.get(db=db, id=comment_id)

@router.get("/post/{post_id}", response_model=list[schemas.Comment])
def read_comments_for_post(
    post_id: int,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    return crud.comment.get_multi_by_post(db, post_id=post_id, skip=skip, limit=limit)

@router.put("/{comment_id}", response_model=schemas.Comment, dependencies=[Depends(get_current_user)])
def update_comment(
    *,
    db: Session = Depends(get_db),
    comment_id: int,
    comment_in: schemas.CommentUpdate,
    current_user: models.User = Depends(get_current_user)
):
    comment = crud.comment.get(db=db, id=comment_id)
    # Add authorization check here if needed
    return crud.comment.update(db=db, db_obj=comment, obj_in=comment_in)

@router.delete("/{comment_id}", response_model=schemas.Comment, dependencies=[Depends(get_current_user)])
def delete_comment(
    *,
    db: Session = Depends(get_db),
    comment_id: int,
    current_user: models.User = Depends(get_current_user)
):
    comment = crud.comment.get(db=db, id=comment_id)
    # Add authorization check here if needed
    return crud.comment.remove(db=db, id=comment_id)
