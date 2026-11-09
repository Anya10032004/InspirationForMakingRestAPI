from flask import jsonify
from werkzeug.exceptions import HTTPException


def register_error_handlers(app):
    """Keep common error responses consistent across all routes."""

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        return jsonify({
            "message": error.description,
            "status": error.code,
        }), error.code

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        app.logger.exception("Unexpected application error")
        return jsonify({
            "message": "An unexpected server error occurred",
            "status": 500,
        }), 500
