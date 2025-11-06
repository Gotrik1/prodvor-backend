def init_routes(app):
    from . import users, sports, legacy, teams, auth, sessions

    app.register_blueprint(auth.auth_bp, url_prefix='/api/v1') # ИЗМЕНЕНО
    app.register_blueprint(users.users_bp, url_prefix='/api/v1')
    app.register_blueprint(sports.sports_bp, url_prefix='/api/v1')
    app.register_blueprint(legacy.legacy_bp, url_prefix='/api/v1')
    app.register_blueprint(teams.teams_bp, url_prefix='/api/v1')
    app.register_blueprint(sessions.sessions_bp, url_prefix='/api/v1/users')
