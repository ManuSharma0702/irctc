from app.models import db, User, Train, Booking
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from datetime import datetime

# User Services
class UserService:
    @staticmethod
    def register_user(username, password, role):
        try:
            hashed_password = generate_password_hash(password)
            user = User(username=username, password=hashed_password, role=role)
            db.session.add(user)
            db.session.commit()
            return {"message": "User registered successfully."}, 201
        except IntegrityError:
            db.session.rollback()
            return {"error": "Username already exists."}, 400

    @staticmethod
    def login_user(username, password):
        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password, password):
            return {"error": "Invalid credentials."}, 401
        token = create_access_token(identity={"id": user.id, "role": user.role})
        return {"token": token}, 200

# Admin Services
class AdminService:
    @staticmethod
    def add_train(name, source, destination, total_seats):
        try:
            train = Train(name=name, source=source, destination=destination, total_seats=total_seats, available_seats=total_seats)
            db.session.add(train)
            db.session.commit()
            return {"message": "Train added successfully."}, 201
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

# Train Services
class TrainService:
    @staticmethod
    def get_trains_between_stations(source, destination):
        trains = Train.query.filter_by(source=source, destination=destination).all()
        return [{"id": train.id, "name": train.name, "available_seats": train.available_seats} for train in trains]

# Booking Services
class BookingService:
    @staticmethod
    def book_seat(user_id, train_id):
        train = Train.query.get(train_id)
        if not train:
            return {"error": "Train not found."}, 404

        if train.available_seats <= 0:
            return {"error": "No seats available."}, 400

        try:
            # Atomic transaction to prevent race condition
            train.available_seats -= 1
            db.session.add(Booking(user_id=user_id, train_id=train_id, booking_time=datetime.now()))
            db.session.commit()
            return {"message": "Seat booked successfully."}, 200
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

    @staticmethod
    def get_booking_details(user_id):
        bookings = Booking.query.filter_by(user_id=user_id).all()
        return [
            {
                "booking_id": booking.id,
                "train_name": booking.train.name,
                "booking_time": booking.booking_time.strftime("%Y-%m-%d %H:%M:%S"),
            }
            for booking in bookings
        ]
