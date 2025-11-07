from flask import Blueprint, jsonify, request
from app import db
from app.models import Sport

sports_bp = Blueprint('sports', __name__)

@sports_bp.route('/sports/', methods=['GET'])
def get_sports():
    """
    Get all sports
    ---
    tags:
        - Sports
    responses:
        '200':
            description: A list of sports.
            schema:
                type: array
                items:
                    type: object
                    properties:
                        id:
                            type: string
                        name:
                            type: string
                        isTeamSport:
                            type: boolean
    """
    sports = Sport.query.all()
    return jsonify([s.to_dict() for s in sports])

@sports_bp.route('/sports', methods=['POST'])
def create_sport():
    """
    Create a new sport
    ---
    tags:
        - Sports
    parameters:
        -   in: body
            name: body
            required: true
            schema:
                type: object
                required:
                    - name
                    - isTeamSport
                properties:
                    name:
                        type: string
                    isTeamSport:
                        type: boolean
    responses:
        '201':
            description: Sport created successfully
        '400':
            description: Missing name or isTeamSport, or sport with this name already exists
    """
    data = request.get_json()
    if not data or not all(k in data for k in ('name', 'isTeamSport')):
        return jsonify({'error': 'Missing name or isTeamSport'}), 400

    # Check for duplicate sport name
    if Sport.query.filter_by(name=data['name']).first():
        return jsonify({'error': 'Sport with this name already exists'}), 400

    new_sport_id = f"sport-{Sport.query.count() + 1}"
    new_sport = Sport(
        id=new_sport_id,
        name=data['name'],
        isTeamSport=data['isTeamSport']
    )

    db.session.add(new_sport)
    db.session.commit()

    return jsonify(new_sport.to_dict()), 201
