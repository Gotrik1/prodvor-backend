
from apiflask import APIBlueprint
from flask import jsonify, request, abort
from app import db
from app.models import Sport
from app.routes.users import serialize_pagination
import uuid

sports_bp = APIBlueprint('sports', __name__)

@sports_bp.route('/sports/', methods=['GET'])
def get_sports():
    """
    Get all sports
    ---
    tags:
      - Sports
    summary: Get all sports
    description: Retrieves a paginated list of all available sports.
    parameters:
      - in: query
        name: page
        schema:
          type: integer
          default: 1
      - in: query
        name: per_page
        schema:
          type: integer
          default: 10
    responses:
      200:
        description: A paginated list of sports.
        content:
          application/json:
            schema:
              type: object
              properties:
                data:
                  type: array
                  items:
                    $ref: '#/components/schemas/Sport'
                meta:
                  $ref: '#/components/schemas/Pagination'
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    sports_pagination = Sport.query.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify(serialize_pagination(sports_pagination, 'data', lambda s: s.to_dict()))

@sports_bp.route('/sports', methods=['POST'])
def create_sport():
    """
    Create a new sport
    ---
    tags:
      - Sports
    summary: Create a new sport
    description: Creates a new sport.
    requestBody:
      required: true
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Sport'
    responses:
      201:
        description: Sport created successfully.
      400:
        description: Bad request (missing fields or sport with this name already exists).
    """
    data = request.get_json()
    if not data or not all(k in data for k in ('name', 'isTeamSport')):
        abort(400, description='Missing name or isTeamSport')

    if Sport.query.filter_by(name=data['name']).first():
        abort(400, description='Sport with this name already exists')

    # Using UUID for consistency with other models
    new_sport = Sport(
        id=str(uuid.uuid4()),
        name=data['name'],
        isTeamSport=data['isTeamSport']
    )

    db.session.add(new_sport)
    db.session.commit()

    return jsonify(new_sport.to_dict()), 201
