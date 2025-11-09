
from flask import jsonify
from werkzeug.exceptions import HTTPException

def handle_http_exception(e):
    """
    Handles HTTP exceptions raised by Flask/Werkzeug.
    """
    return jsonify({
        "code": e.name.replace(" ", "_").upper(),
        "error": e.description,
    }), e.code

def init_app(app):
    """
    Registers the error handlers on the Flask app.
    """
    app.register_error_handler(HTTPException, handle_http_exception)

