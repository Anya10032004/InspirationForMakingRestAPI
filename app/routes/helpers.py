from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt


def role_required(required_role):
    """Protect a route so only users with the specified JWT role can access it."""
    def decorator(view_function):
        @wraps(view_function)
        def wrapped(*args, **kwargs):
            claims = get_jwt()
            if claims.get("role") != required_role:
                return jsonify({
                    "message": f"Only {required_role}s can access this endpoint",
                    "status": 403,
                }), 403
            return view_function(*args, **kwargs)
        return wrapped
    return decorator


def json_body():
    """Return the request JSON object, or an empty dictionary for invalid/missing JSON."""
    from flask import request
    return request.get_json(silent=True) or {}
