"""/app/routes/blog_api.py"""

from typing import Union, Optional
from datetime import datetime
from sqlmodel import Session, select, update, delete

from fastapi import APIRouter, Depends, HTTPException

from models import Post
from database import get_session
from schemas import PostCreate, PostResponse, UserResponse
from security import current_class

route = APIRouter(prefix="/posts", tags=["Posts"])


@route.post("/", response_model=PostResponse)
async def create_post(
    post: PostCreate,
    db: Session = Depends(get_session),
    current_user: UserResponse = Depends(current_class.get_current_data)
):
    """Create a new post"""
    if current_user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")

    new_post = Post(**post.model_dump(), user_id=current_user.id)

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post

@route.get("/{field}/", response_model=list[PostResponse, UserResponse])
async def read_posts(
    field: str,
    q: Union[int, str, None] = None,
    # id: Optional[int] = None,
    # user_id: Optional[int] = None,
    # title: Optional[str] = None,
    # content: Optional[str] = None,
    db: Session = Depends(get_session)
):
    """Read all posts"""
    match field:
        case "all":
            return db.exec(select(Post)).all()
        case "id" if q.isdigit():
            return db.exec(select(Post).where(Post.id == int(q))).all()
        case "user_id" if q.isdigit():
            return db.exec(select(Post).where(Post.user_id == int(q))).all()
        case "title":
            return db.exec(select(Post).where(Post.title == q)).all()
        case "content":
            return db.exec(select(Post).where(Post.content == q)).all()
        case _:
            raise HTTPException(status_code=400, detail="Invalid field")

@route.put("/{id}")
async def update_post(id: int, post: PostCreate, db: Session = Depends(get_session)):
    """Update a post by id"""
    updated_post = post.model_dump()

    db.exec(update(Post).where(Post.id == id).values(
        **updated_post,
        edited_at = datetime.utcnow()
    ))
    db.commit()

    return updated_post

@route.delete("/{id}")
async def delete_post(
    id: int,
    db: Session = Depends(get_session),
    current_user: UserResponse = Depends(current_class.get_current_data)
):
    """Delete a post by id"""
    post_exists = db.get(Post, id)

    if not post_exists:
        raise HTTPException(status_code=404, detail="Post not found")

    if post_exists.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="You don't have permission to delete this post")

    db.delete(post_exists)
    db.commit()

    return {"message": "Post deleted successfully"}
