from flask import Blueprint, request, jsonify
from app.models import Train, Booking, db
from functools import wraps
import jwt
from config import Config

user_bp = Blueprint("user", __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")
        try:
            jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
        except:
            return jsonify({"message": "Unauthorized"}), 403
        return f(*args, **kwargs)
    return decorated

@user_bp.route("/trains/availability", methods=["GET"])
def get_availability():
    source = request.args.get("source")
    destination = request.args.get("destination")
    trains = Train.query.filter_by(source=source, destination=destination).all()

    return jsonify(
        [{"id": train.id, "name": train.name, "available_seats": train.available_seats} for train in trains]
    )

@user_bp.route("/trains/book-seat", methods=["POST"])
@token_required
def book_seat():
    data = request.json
    train = Train.query.get(data["train_id"])

    if train.available_seats <= 0:
        return jsonify({"message": "No seats available"}), 400

    train.available_seats -= 1
    booking = Booking(user_id=data["user_id"], train_id=train.id, status="confirmed")
    db.session.add(booking)
    db.session.commit()
    
    return jsonify({"message": "Seat booked successfully"}), 200
