from flask import Blueprint, request, jsonify
from app.models import Train, db
from functools import wraps

admin_bp = Blueprint("admin", __name__)

API_KEY = "your_admin_api_key"

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get("x-api-key")
        if api_key != API_KEY:
            return jsonify({"message": "Unauthorized"}), 403
        return f(*args, **kwargs)
    return decorated

@admin_bp.route("/add-train", methods=["POST"])
@admin_required
def add_train():
    data = request.json
    train = Train(
        name=data["name"],
        source=data["source"],
        destination=data["destination"],
        total_seats=data["total_seats"],
        available_seats=data["total_seats"],
    )
    db.session.add(train)
    db.session.commit()
    return jsonify({"message": "Train added successfully"}), 201
