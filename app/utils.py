from flask import request
from functools import wraps
from flask_jwt_extended import get_jwt_identity
import os

ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "default_admin_key")

# Utility to check API key
def require_admin_api_key(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get("x-api-key")
        if api_key != ADMIN_API_KEY:
            return {"error": "Unauthorized. Invalid API key."}, 403
        return func(*args, **kwargs)
    return decorated_function

# Utility to check user roles
def require_user_role(required_role):
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            current_user = get_jwt_identity()
            if not current_user or current_user["role"] != required_role:
                return {"error": "Forbidden. Insufficient permissions."}, 403
            return func(*args, **kwargs)
        return decorated_function
    return decorator
