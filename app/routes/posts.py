
from apiflask import APIBlueprint
from flask import request, jsonify, abort
from app import db
from app.models import Post
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..utils.decorators import jwt_required
from app.routes.users import serialize_pagination

posts_bp = APIBlueprint('posts', __name__)

@posts_bp.route('/posts', methods=['GET'])
def get_posts():
    """
    Get all posts
    ---
    tags:
      - Posts
    summary: Get all posts
    description: Retrieves a paginated list of all posts in descending order of creation time.
    parameters:
      - in: query
        name: page
        schema:
          type: integer
          default: 1
        description: The page number to retrieve.
      - in: query
        name: per_page
        schema:
          type: integer
          default: 10
        description: The number of posts to retrieve per page.
    responses:
      200:
        description: A paginated list of posts.
        content:
          application/json:
            schema:
              type: object
              properties:
                data:
                  type: array
                  items:
                    $ref: '#/components/schemas/Post'
                meta:
                  $ref: '#/components/schemas/Pagination'
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    posts_pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify(serialize_pagination(posts_pagination, 'data', lambda p: p.to_dict()))

@posts_bp.route('/posts', methods=['POST'])
@jwt_required
def create_post(current_user):
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
        abort(400, description="Missing content")

    new_post = Post(
        authorId=current_user.id,
        content=data['content'],
        teamId=data.get('teamId')
    )
    db.session.add(new_post)
    db.session.commit()

    return jsonify(new_post.to_dict()), 201
