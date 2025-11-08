
from flask import request, jsonify, Blueprint
from app import db
from app.models import Tournament
from flask_jwt_extended import jwt_required

tournaments_bp = Blueprint('tournaments', __name__)

@tournaments_bp.route('/tournaments', methods=['GET'])
def get_tournaments():
    """
    Get all tournaments
    """
    tournaments = Tournament.query.all()
    return jsonify([t.to_dict() for t in tournaments])

@tournaments_bp.route('/tournaments/<tournament_id>', methods=['GET'])
def get_tournament(tournament_id):
    """
    Get a tournament by ID
    """
    tournament = Tournament.query.get_or_404(tournament_id)
    return jsonify(tournament.to_dict())

@tournaments_bp.route('/tournaments', methods=['POST'])
@jwt_required()
def create_tournament():
    """
    Create a new tournament
    """
    data = request.get_json()
    if not data or not data.get('name'):
        return jsonify({"error": "Missing required field: name"}), 400

    new_tournament = Tournament(
        name=data['name'],
        game=data.get('game'),
        status=data.get('status', 'planned'),
        prizePool=data.get('prizePool'),
        maxParticipants=data.get('maxParticipants'),
        startDate=data.get('startDate')
    )
    db.session.add(new_tournament)
    db.session.commit()
    
    return jsonify(new_tournament.to_dict()), 201
