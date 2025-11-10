from apiflask import APIBlueprint
from flask import request, jsonify
from app.models import LfgPost, db, User, Team, Sport
from flask_jwt_extended import jwt_required, current_user

lfg_bp = APIBlueprint('lfg_bp', __name__)

@lfg_bp.route('/lfg', methods=['GET'])
@lfg_bp.doc(operation_id='listLfgPosts')
def list_lfg_posts():
    """
    Get all LFG posts with optional filters
    """
    args = request.args
    query = LfgPost.query

    if 'type' in args:
        query = query.filter_by(type=args['type'])
    if 'sportId' in args:
        query = query.filter_by(sportId=args['sportId'])
    if 'role' in args:
        query = query.filter(LfgPost.requiredRole.ilike(f"%{args['role']}%"))

    posts = query.order_by(LfgPost.createdAt.desc()).all()
    return jsonify([post.to_dict() for post in posts]), 200


@lfg_bp.route('/lfg', methods=['POST'])
@lfg_bp.doc(operation_id='createLfgPost')
@jwt_required()
def create_lfg_post():
    """
    Create a new LFG post
    """
    data = request.get_json()

    if not all(key in data for key in ['type', 'sportId', 'requiredRole', 'message']):
        return jsonify({"error": "Missing required fields"}), 400

    if data['type'] not in ['player', 'team']:
        return jsonify({"error": "Invalid type specified"}), 400
        
    sport = Sport.query.get(data['sportId'])
    if not sport:
        return jsonify({"error": "Sport not found"}), 404

    team = None
    if data['type'] == 'team':
        if 'teamId' not in data:
            return jsonify({"error": "teamId is required for type 'team'"}), 400
        team = Team.query.get(data['teamId'])
        if not team:
            return jsonify({"error": "Team not found"}), 404
        if str(team.captainId) != str(current_user.id):
            return jsonify({"error": "Only the team captain can create a 'team' LFG post"}), 403


    new_post = LfgPost(
        type=data['type'],
        authorId=current_user.id,
        teamId=data.get('teamId'),
        sportId=data['sportId'],
        requiredRole=data['requiredRole'],
        message=data['message']
    )

    db.session.add(new_post)
    db.session.commit()

    return jsonify(new_post.to_dict()), 201
