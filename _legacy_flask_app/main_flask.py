
from app import create_app
from flask import jsonify
from sqlalchemy.exc import SQLAlchemyError

app = create_app()

@app.errorhandler(SQLAlchemyError)
def handle_sqlalchemy_error(e):
    """Global error handler for all SQLAlchemy errors."""
    # For debugging purposes, you might want to log the error.
    # For now, we'll return a generic 500 error.
    response = {
        "error": "Database Error",
        "message": "An internal error related to the database occurred."
    }
    return jsonify(response), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
