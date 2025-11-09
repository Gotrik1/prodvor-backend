
from apiflask import APIBlueprint
from flask import jsonify, request
from app.models import Sponsor
from app.routes.users import serialize_pagination

sponsors_bp = APIBlueprint('sponsors', __name__)

@sponsors_bp.route('/sponsors', methods=['GET'])
def get_sponsors():
    """
    Get all sponsors
    ---
    tags:
      - Sponsors
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
      '200':
        description: A paginated list of sponsors.
        content:
          application/json:
            schema:
              type: object
              properties:
                data:
                  type: array
                  items:
                    $ref: '#/components/schemas/Sponsor'
                meta:
                  $ref: '#/components/schemas/Pagination'
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    sponsors_pagination = Sponsor.query.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify(serialize_pagination(sponsors_pagination, 'data', lambda s: s.to_dict()))
