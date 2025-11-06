
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, current_user
from app import db
from app.models import UserSession
from app.utils import hash_token # <<< Импортируем централизованную функцию

sessions_bp = Blueprint('sessions', __name__)

# --- Функция hash_token удалена --- 

@sessions_bp.route('/me/sessions', methods=['GET'])
@jwt_required()
def get_my_sessions():
    """
    Get all active sessions for the current user
    ---
    # ... (swagger docs)
    """
    if not current_user:
        return jsonify({"msg": "User not found or invalid token"}), 404

    sessions = UserSession.query.filter_by(userId=current_user.id).order_by(UserSession.lastActiveAt.desc()).all()

    return jsonify([session.to_dict() for session in sessions])


@sessions_bp.route('/me/sessions/<int:session_id>', methods=['DELETE'])
@jwt_required()
def delete_session(session_id):
    """
    Delete a specific session for the current user
    ---
    # ... (swagger docs)
    """
    if not current_user:
        return jsonify({"msg": "User not found or invalid token"}), 404
    
    session_to_delete = UserSession.query.filter_by(id=session_id, userId=current_user.id).first()

    if not session_to_delete:
        return jsonify({'error': 'Session not found or you do not have permission to delete it'}), 404

    most_recent_session = UserSession.query.filter_by(userId=current_user.id).order_by(UserSession.lastActiveAt.desc()).first()
    if session_to_delete.id == most_recent_session.id:
         return jsonify({'error': 'Cannot delete the currently active session'}), 400

    db.session.delete(session_to_delete)
    db.session.commit()
    return jsonify({'success': True}), 200


@sessions_bp.route('/me/sessions/all-except-current', methods=['DELETE'])
@jwt_required()
def delete_all_other_sessions():
    """
    Delete all sessions for the current user except the current one
    ---
    # ... (swagger docs)
    """
    if not current_user:
        return jsonify({"msg": "User not found or invalid token"}), 404

    sessions = UserSession.query.filter_by(userId=current_user.id).order_by(UserSession.lastActiveAt.desc()).all()
    
    if not sessions:
        return jsonify({'success': True}), 200

    current_session = sessions.pop(0)

    for session in sessions:
        db.session.delete(session)
    
    db.session.commit()
    return jsonify({'success': True}), 200
