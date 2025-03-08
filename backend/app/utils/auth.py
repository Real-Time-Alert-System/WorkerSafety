from functools import wraps
from flask import request, jsonify
from app import config

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.endpoint != 'views.dashboard':
            auth_header = request.headers.get('Authorization')
            if not auth_header or auth_header != f"Bearer {config.AUTH_TOKEN}":
                return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated
