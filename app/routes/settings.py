
from flask import Blueprint, jsonify, request
from ..models import db, User, UserSettings, UserPrivacySettings
from ..utils.decorators import jwt_required

settings_bp = Blueprint('settings', __name__, url_prefix='/api/v1/users/me')

@settings_bp.route('/settings', methods=['PUT'])
@jwt_required
def update_user_settings(current_user):
    data = request.get_json()

    user_settings = UserSettings.query.filter_by(user_id=current_user.id).first()
    if not user_settings:
        user_settings = UserSettings(user_id=current_user.id)
        db.session.add(user_settings)

    # Обновляем только те поля, которые были переданы
    if 'theme' in data:
        user_settings.theme = data['theme']
    if 'language' in data:
        user_settings.language = data['language']
    
    db.session.commit()
    return jsonify(user_settings.to_dict())

@settings_bp.route('/privacy', methods=['PUT'])
@jwt_required
def update_user_privacy_settings(current_user):
    data = request.get_json()

    privacy_settings = UserPrivacySettings.query.filter_by(user_id=current_user.id).first()
    if not privacy_settings:
        privacy_settings = UserPrivacySettings(user_id=current_user.id)
        db.session.add(privacy_settings)

    # Обновляем только те поля, которые были переданы
    if 'profile_visibility' in data:
        privacy_settings.profile_visibility = data['profile_visibility']
    if 'teams_visibility' in data:
        privacy_settings.teams_visibility = data['teams_visibility']
    if 'messages_privacy' in data:
        privacy_settings.messages_privacy = data['messages_privacy']

    db.session.commit()
    return jsonify(privacy_settings.to_dict())
