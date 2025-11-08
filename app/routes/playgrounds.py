
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
    responses:
        '200':
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
              address:
                type: string
              type:
                type: string
              surface:
                type: string
    responses:
        '201':
            description: Playground created successfully.
        '400':
            description: Missing required fields.
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
