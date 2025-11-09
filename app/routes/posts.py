
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
    summary: Get all posts
    description: Retrieves a list of all posts in descending order of creation time.
    responses:
      200:
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
    summary: Create a new post
    description: Creates a new post. The author ID is taken from the authentication token.
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
                example: "This is a new post!"
              teamId:
                type: string
                description: The ID of the team to associate the post with (optional).
                example: "123e4567-e89b-12d3-a456-426614174000"
    responses:
      201:
        description: Post created successfully.
      400:
        description: Bad request (missing content).
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
