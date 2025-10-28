# routes/crud_apis.py
from flask_restful import Resource
from flask import request, jsonify, make_response
from flask_security import auth_required, roles_required, current_user
from data.models import db, User, ParkingLot, ParkingSpot

# -----------------------------
# USER CRUD (Admin-only)
# -----------------------------
class UserListAPI(Resource):
    @roles_required('admin')
    def get(self):
        users = User.query.all()
        data = [{
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "model": u.model,
            "roles": [r.name for r in u.roles]
        } for u in users]
        return make_response(jsonify(data), 200)

    @roles_required('admin')
    def post(self):
        data = request.get_json()
        if not data:
            return make_response(jsonify({"message": "Missing data"}), 400)

        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        model = data.get('model', '')

        if not username or not email or not password:
            return make_response(jsonify({"message": "All fields are required"}), 400)

        if User.query.filter_by(email=email).first():
            return make_response(jsonify({"message": "User already exists"}), 409)

        new_user = User(username=username, email=email, model=model, password=password)
        db.session.add(new_user)
        db.session.commit()

        return make_response(jsonify({"message": "User created successfully"}), 201)


class UserAPI(Resource):
    @roles_required('admin')
    def get(self, user_id):
        user = User.query.get_or_404(user_id)
        data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "model": user.model,
            "roles": [r.name for r in user.roles]
        }
        return make_response(jsonify(data), 200)

    @roles_required('admin')
    def put(self, user_id):
        data = request.get_json()
        user = User.query.get_or_404(user_id)

        user.username = data.get('username', user.username)
        user.email = data.get('email', user.email)
        user.model = data.get('model', user.model)

        db.session.commit()
        return make_response(jsonify({"message": "User updated"}), 200)

    @roles_required('admin')
    def delete(self, user_id):
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return make_response(jsonify({"message": "User deleted"}), 200)


# -----------------------------
# PARKING LOT CRUD (Admin-only)
# -----------------------------
class ParkingLotListAPI(Resource):
    @roles_required('admin')
    def get(self):
        lots = ParkingLot.query.all()
        data = [{
            "id": lot.id,
            "name": lot.name,
            "location": lot.location,
            "capacity": lot.capacity
        } for lot in lots]
        return make_response(jsonify(data), 200)

    @roles_required('admin')
    def post(self):
        data = request.get_json()
        if not data:
            return make_response(jsonify({"message": "Missing data"}), 400)

        name = data.get('name')
        location = data.get('location')
        capacity = data.get('capacity', 0)

        if not name or not location:
            return make_response(jsonify({"message": "Name and location required"}), 400)

        new_lot = ParkingLot(name=name, location=location, capacity=capacity)
        db.session.add(new_lot)
        db.session.commit()

        # Auto-generate parking spots
        for i in range(capacity):
            spot = ParkingSpot(lot_id=new_lot.id, spot_number=i + 1, status="available")
            db.session.add(spot)
        db.session.commit()

        return make_response(jsonify({"message": "Parking lot created with spots"}), 201)


class ParkingLotAPI(Resource):
    @roles_required('admin')
    def get(self, lot_id):
        lot = ParkingLot.query.get_or_404(lot_id)
        spots = ParkingSpot.query.filter_by(lot_id=lot.id).all()
        data = {
            "id": lot.id,
            "name": lot.name,
            "location": lot.location,
            "capacity": lot.capacity,
            "spots": [{"id": s.id, "spot_number": s.spot_number, "status": s.status} for s in spots]
        }
        return make_response(jsonify(data), 200)

    @roles_required('admin')
    def put(self, lot_id):
        data = request.get_json()
        lot = ParkingLot.query.get_or_404(lot_id)

        lot.name = data.get('name', lot.name)
        lot.location = data.get('location', lot.location)
        lot.capacity = data.get('capacity', lot.capacity)
        db.session.commit()

        return make_response(jsonify({"message": "Parking lot updated"}), 200)

    @roles_required('admin')
    def delete(self, lot_id):
        lot = ParkingLot.query.get_or_404(lot_id)
        spots = ParkingSpot.query.filter_by(lot_id=lot.id).all()
        if any(s.status == "occupied" for s in spots):
            return make_response(jsonify({"message": "Cannot delete lot with occupied spots"}), 400)
        for s in spots:
            db.session.delete(s)
        db.session.delete(lot)
        db.session.commit()
        return make_response(jsonify({"message": "Parking lot deleted"}), 200)


# -----------------------------
# PARKING SPOT CRUD (Admin + User)
# -----------------------------
class ParkingSpotListAPI(Resource):
    @auth_required("token")
    def get(self):
        spots = ParkingSpot.query.all()
        data = [{
            "id": s.id,
            "lot_id": s.lot_id,
            "spot_number": s.spot_number,
            "status": s.status
        } for s in spots]
        return make_response(jsonify(data), 200)


class ParkingSpotAPI(Resource):
    @auth_required("token")
    def put(self, spot_id):
        data = request.get_json()
        spot = ParkingSpot.query.get_or_404(spot_id)

        # Allow users to occupy/release only their own assigned spot
        if current_user.has_role('user'):
            if data.get('status') not in ['available', 'occupied']:
                return make_response(jsonify({"message": "Invalid status"}), 400)
            spot.status = data.get('status')
        else:
            # Admin can force status change
            spot.status = data.get('status', spot.status)

        db.session.commit()
        return make_response(jsonify({"message": "Spot updated"}), 200)

from datetime import datetime

class ReserveParkingAPI(Resource):
    @auth_required("token")
    def post(self):
        """
        Reserve the first available parking spot in a given lot.
        """
        data = request.get_json()
        lot_id = data.get('lot_id')

        if not lot_id:
            return make_response(jsonify({"message": "lot_id is required"}), 400)

        lot = ParkingLot.query.get(lot_id)
        if not lot:
            return make_response(jsonify({"message": "Invalid parking lot"}), 404)

        # Find first available spot
        spot = ParkingSpot.query.filter_by(lot_id=lot.id, status="available").first()
        if not spot:
            return make_response(jsonify({"message": "No available spots in this lot"}), 400)

        # Mark the spot as occupied
        spot.status = "occupied"
        spot.user_id = current_user.id
        spot.entry_time = datetime.now()

        db.session.commit()

        return make_response(jsonify({
            "message": "Parking spot reserved successfully",
            "lot_name": lot.name,
            "spot_number": spot.spot_number,
            "entry_time": spot.entry_time.strftime("%Y-%m-%d %H:%M:%S")
        }), 200)


class ReleaseParkingAPI(Resource):
    @auth_required("token")
    def post(self):
        """
        Release a user's currently occupied parking spot.
        """
        # Find user's occupied spot
        spot = ParkingSpot.query.filter_by(user_id=current_user.id, status="occupied").first()
        if not spot:
            return make_response(jsonify({"message": "No active reservation found"}), 404)

        # Update timestamps and status
        spot.status = "available"
        spot.exit_time = datetime.now()
        spot.user_id = None

        # Calculate parking duration (in minutes)
        duration = int((spot.exit_time - spot.entry_time).total_seconds() / 60)
        cost = round(duration * 1.5, 2)  # simple rate per minute

        db.session.commit()

        return make_response(jsonify({
            "message": "Spot released successfully",
            "spot_number": spot.spot_number,
            "exit_time": spot.exit_time.strftime("%Y-%m-%d %H:%M:%S"),
            "duration_minutes": duration,
            "cost": cost
        }), 200)