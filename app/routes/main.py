from flask import Blueprint, redirect, url_for, send_from_directory, current_app

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """
    Redirect to API docs
    ---
    tags:
        - Index
    responses:
        302:
            description: Redirect to /apidocs/
    """
    return redirect('/apidocs/')

@main_bp.route('/openapi.json')
def serve_openapi():
    """
    Serve the static openapi.json file
    ---
    tags:
        - Index
    responses:
        200:
            description: The openapi.json file
        404:
            description: File not found
    """
    return send_from_directory(current_app.static_folder, 'swagger.json')
