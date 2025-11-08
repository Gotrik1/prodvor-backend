
from flask import request, jsonify, Blueprint
from app import db
from app.models import Post
from flask_jwt_extended import jwt_required, get_jwt_identity

posts_bp = Blueprint('posts', __name__)

@posts_bp.route('/posts', methods=['GET'])
def get_posts():
    """
    Get all posts
    ---
    tags:
        - Posts
    responses:
        '200':
            description: A list of posts.
    """
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return jsonify([p.to_dict() for p in posts])

@posts_bp.route('/posts', methods=['POST'])
@jwt_required()
def create_post():
    """
    Create a new post
    ---
    tags:
        - Posts
    security:
        - bearerAuth: []
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required: [content]
            properties:
              content:
                type: string
              teamId:
                type: integer
    responses:
        '201':
            description: Post created successfully.
        '400':
            description: Missing content.
    """
    data = request.get_json()
    if not data or not data.get('content'):
        return jsonify({"error": "Missing content"}), 400

    current_user_id = get_jwt_identity()
    
    new_post = Post(
        authorId=current_user_id,
        content=data['content'],
        teamId=data.get('teamId')
    )
    db.session.add(new_post)
    db.session.commit()

    return jsonify(new_post.to_dict()), 201
