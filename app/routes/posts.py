
from apiflask import APIBlueprint
from flask import request, jsonify, abort
from app import db
from app.models import Post
from flask_jwt_extended import jwt_required, current_user
from app.routes.users import serialize_pagination

posts_bp = APIBlueprint('posts', __name__)

@posts_bp.route('/posts', methods=['GET'])
@posts_bp.doc(operation_id='listPosts')
def get_posts():
    """
    Get all posts
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    posts_pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify(serialize_pagination(posts_pagination, 'data', lambda p: p.to_dict()))

@posts_bp.route('/posts', methods=['POST'])
@posts_bp.doc(operation_id='createPost')
@jwt_required()
def create_post():
    """
    Create a new post
    """
    data = request.get_json()
    if not data or not data.get('content'):
        abort(400, description="Missing content")

    new_post = Post(
        authorId=current_user.id,
        content=data['content'],
        teamId=data.get('teamId')
    )
    db.session.add(new_post)
    db.session.commit()

    return jsonify(new_post.to_dict()), 201
