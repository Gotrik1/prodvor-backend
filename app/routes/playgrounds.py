
from flask import request, jsonify, Blueprint, abort
from app import db
from app.models import Playground
from flask_jwt_extended import jwt_required
from app.routes.users import serialize_pagination # Импортируем утилиту пагинации

playgrounds_bp = Blueprint('playgrounds', __name__)

@playgrounds_bp.route('/playgrounds', methods=['GET'])
def get_playgrounds():
    """
    Get all playgrounds
    ---
    tags:
      - Playgrounds
    summary: Get all playgrounds
    description: Retrieves a paginated list of all available playgrounds.
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
        description: The number of playgrounds to retrieve per page.
    responses:
      200:
        description: A paginated list of playgrounds.
        content:
          application/json:
            schema:
              type: object
              properties:
                data:
                  type: array
                  items:
                    $ref: '#/components/schemas/Playground'
                meta:
                  $ref: '#/components/schemas/Pagination'
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    playgrounds_pagination = Playground.query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify(serialize_pagination(playgrounds_pagination, 'data', lambda p: p.to_dict()))

@playgrounds_bp.route('/playgrounds', methods=['POST'])
@jwt_required()
def create_playground():
    """
    Create a new playground
    ---
    tags:
      - Playgrounds
    summary: Create a new playground
    description: Creates a new playground. Requires authentication.
    security:
      - bearerAuth: []
    requestBody:
      required: true
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Playground' # Предполагаем, что схема определена
    responses:
      201:
        description: Playground created successfully.
      400:
        description: Bad request (missing required fields).
    """
    data = request.get_json()
    if not data or not data.get('name') or not data.get('address'):
        abort(400, description="Missing required fields: name, address")

    new_playground = Playground(
        name=data['name'],
        address=data['address'],
        type=data.get('type'),
        surface=data.get('surface')
    )
    db.session.add(new_playground)
    db.session.commit()
    
    return jsonify(new_playground.to_dict()), 201
