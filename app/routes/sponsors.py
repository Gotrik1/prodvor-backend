from flask import Blueprint, jsonify
from app.models import Sponsor

sponsors_bp = Blueprint('sponsors', __name__)

@sponsors_bp.route('/sponsors', methods=['GET'])
def get_sponsors():
    """
    Get all sponsors
    ---
    tags:
      - Sponsors
    responses:
      '200':
        description: A list of sponsors.
    """
    sponsors = Sponsor.query.all()
    return jsonify([s.to_dict() for s in sponsors])
