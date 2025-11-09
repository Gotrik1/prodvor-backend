from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity
from app.models import User

def jwt_required(fn):
    """
    A decorator to protect routes with JWT authentication.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            current_user = User.query.get(user_id)
            if not current_user:
                return jsonify({"error": "User not found"}), 404
            return fn(current_user, *args, **kwargs)
        except Exception as e:
            return jsonify({"error": str(e)}), 401
    return wrapper
