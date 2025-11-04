
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app import db
from app.models import UserSession
import hashlib

sessions_bp = Blueprint('sessions', __name__)

def hash_token(token):
    return hashlib.sha256(token.encode()).hexdigest()

@sessions_bp.route('/me/sessions', methods=['GET'])
@jwt_required()
def get_my_sessions():
    """
    Get all active sessions for the current user
    ---
    tags:
      - Sessions
    security:
      - Bearer: []
    responses:
      200:
        description: A list of active user sessions.
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              userAgent:
                type: string
              ipAddress:
                type: string
              lastActiveAt:
                type: string
                format: date-time
              createdAt:
                type: string
                format: date-time
              isCurrent:
                type: boolean
    """
    current_user_id = get_jwt_identity()
    
    jti = get_jwt()['jti']
    
    sessions = UserSession.query.filter_by(userId=current_user_id).order_by(UserSession.lastActiveAt.desc()).all()

    return jsonify([session.to_dict() for session in sessions])


@sessions_bp.route('/me/sessions/<int:session_id>', methods=['DELETE'])
@jwt_required()
def delete_session(session_id):
    """
    Delete a specific session
    ---
    tags:
      - Sessions
    security:
      - Bearer: []
    parameters:
      - name: session_id
        in: path
        type: integer
        required: true
        description: The ID of the session to delete.
    responses:
      200:
        description: Session deleted successfully.
      400:
        description: Cannot delete the currently active session.
      404:
        description: Session not found or permission denied.
    """
    current_user_id = int(get_jwt_identity())
    
    session_to_delete = UserSession.query.filter_by(id=session_id, userId=current_user_id).first()

    if not session_to_delete:
        return jsonify({'error': 'Session not found or you do not have permission to delete it'}), 404

    most_recent_session = UserSession.query.filter_by(userId=current_user_id).order_by(UserSession.lastActiveAt.desc()).first()
    if session_to_delete.id == most_recent_session.id:
         return jsonify({'error': 'Cannot delete the currently active session'}), 400

    db.session.delete(session_to_delete)
    db.session.commit()
    return jsonify({'success': True}), 200


@sessions_bp.route('/me/sessions/all-except-current', methods=['DELETE'])
@jwt_required()
def delete_all_other_sessions():
    """
    Delete all sessions except the current one
    ---
    tags:
      - Sessions
    security:
      - Bearer: []
    responses:
      200:
        description: All other sessions have been deleted.
    """
    current_user_id = int(get_jwt_identity())

    sessions = UserSession.query.filter_by(userId=current_user_id).order_by(UserSession.lastActiveAt.desc()).all()
    
    if not sessions:
        return jsonify({'success': True}), 200 # No sessions to delete

    # Keep the most recent session
    current_session = sessions.pop(0)

    for session in sessions:
        db.session.delete(session)
    
    db.session.commit()
    return jsonify({'success': True}), 200
