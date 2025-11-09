
from flask import request, jsonify, Blueprint
from app import db
from app.models import Playground
from flask_jwt_extended import jwt_required

playgrounds_bp = Blueprint('playgrounds', __name__)

@playgrounds_bp.route('/playgrounds', methods=['GET'])
def get_playgrounds():
    """
    Get all playgrounds
    ---
    tags:
      - Playgrounds
    summary: Get all playgrounds
    description: Retrieves a list of all available playgrounds.
    responses:
      200:
        description: A list of playgrounds.
    """
    playgrounds = Playground.query.all()
    return jsonify([p.to_dict() for p in playgrounds])

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
            type: object
            required: [name, address]
            properties:
              name:
                type: string
                example: "Central Park Field"
              address:
                type: string
                example: "123 Main St, Anytown"
              type:
                type: string
                example: "Football Pitch"
              surface:
                type: string
                example: "Artificial Turf"
    responses:
      201:
        description: Playground created successfully.
      400:
        description: Bad request (missing required fields).
    """
    data = request.get_json()
    if not data or not data.get('name') or not data.get('address'):
        return jsonify({"error": "Missing required fields: name, address"}), 400

    new_playground = Playground(
        name=data['name'],
        address=data['address'],
        type=data.get('type'),
        surface=data.get('surface')
    )
    db.session.add(new_playground)
    db.session.commit()
    
    return jsonify(new_playground.to_dict()), 201
