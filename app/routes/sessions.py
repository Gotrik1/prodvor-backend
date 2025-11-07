
from flask import request, jsonify, Blueprint
from app import db
from app.models import UserSession
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

sessions_bp = Blueprint('sessions', __name__)

@sessions_bp.route('/users/me/sessions', methods=['GET'])
@jwt_required(refresh=True)
def get_user_sessions():
    """
    Get all active sessions for the current user
    ---
    tags:
        - Sessions
    security:
        - bearerAuth: []
    responses:
        '200':
            description: A list of active sessions.
    """
    user_id = get_jwt_identity()
    jti = get_jwt()['jti']
    current_session = UserSession.query.filter_by(refreshToken=jti).first()

    sessions = UserSession.query.filter_by(userId=user_id).all()
    
    def session_to_dict(session, current_jti):
        return {
            "id": session.id,
            "isCurrent": session.refreshToken == current_jti,
            "userAgent": session.userAgent,
            "ipAddress": session.ipAddress,
            "lastActiveAt": session.lastActiveAt.isoformat(),
            "createdAt": session.createdAt.isoformat()
        }

    return jsonify([session_to_dict(s, jti) for s in sessions])

@sessions_bp.route('/users/me/sessions/<int:session_id>', methods=['DELETE'])
@jwt_required(refresh=True)
def delete_session(session_id):
    """
    Delete a specific session
    ---
    tags:
        - Sessions
    security:
        - bearerAuth: []
    parameters:
        -   name: session_id
            in: path
            required: true
            type: integer
    responses:
        '200':
            description: Session deleted successfully.
        '403':
            description: Cannot delete the current session.
        '404':
            description: Session not found.
    """
    user_id = get_jwt_identity()
    jti = get_jwt()['jti']

    session_to_delete = UserSession.query.filter_by(id=session_id, userId=user_id).first_or_404()

    if session_to_delete.refreshToken == jti:
        return jsonify({"error": "Cannot delete the current session."}), 403

    db.session.delete(session_to_delete)
    db.session.commit()
    return jsonify({"success": True, "message": "Session deleted successfully."})

@sessions_bp.route('/users/me/sessions/all-except-current', methods=['DELETE'])
@jwt_required(refresh=True)
def delete_all_other_sessions():
    """
    Delete all sessions except the current one
    ---
    tags:
        - Sessions
    security:
        - bearerAuth: []
    responses:
        '200':
            description: Sessions deleted successfully.
    """
    user_id = get_jwt_identity()
    jti = get_jwt()['jti']

    sessions_to_delete = UserSession.query.filter(
        UserSession.userId == user_id,
        UserSession.refreshToken != jti
    ).all()

    for session in sessions_to_delete:
        db.session.delete(session)
    
    db.session.commit()
    return jsonify({"success": True, "message": f"{len(sessions_to_delete)} sessions deleted."})


