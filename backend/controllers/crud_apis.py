# routes/crud_apis.py
from flask_restful import Resource
from flask import request, jsonify, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity
from data.models import db, User, ParkingLot, ParkingSpot
from datetime import datetime

# ---------------------------------------
# Helper: Check if current user is admin
# ---------------------------------------
def require_admin():
    uid = get_jwt_identity()
    user = User.query.get(uid)
    if not user or not any(r.name == 'admin' for r in user.roles):
        return None
    return user

# =======================================================
# USER CRUD (Admin-only)
# =======================================================
class UserListAPI(Resource):
    @jwt_required()
    def get(self):
        admin = require_admin()
        if not admin:
            return {"message": "Admin access required"}, 403

        users = User.query.all()
        data = [{
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "model": u.model,
            "roles": [r.name for r in u.roles]
        } for u in users]
        return make_response(jsonify(data), 200)

    @jwt_required()
    def post(self):
        admin = require_admin()
        if not admin:
            return {"message": "Admin access required"}, 403

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
    @jwt_required()
    def get(self, user_id):
        admin = require_admin()
        if not admin:
            return {"message": "Admin access required"}, 403

        user = User.query.get_or_404(user_id)
        data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "model": user.model,
            "roles": [r.name for r in user.roles]
        }
        return make_response(jsonify(data), 200)

    @jwt_required()
    def put(self, user_id):
        admin = require_admin()
        if not admin:
            return {"message": "Admin access required"}, 403

        data = request.get_json()
        user = User.query.get_or_404(user_id)

        user.username = data.get('username', user.username)
        user.email = data.get('email', user.email)
        user.model = data.get('model', user.model)
        db.session.commit()

        return make_response(jsonify({"message": "User updated"}), 200)

    @jwt_required()
    def delete(self, user_id):
        admin = require_admin()
        if not admin:
            return {"message": "Admin access required"}, 403

        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return make_response(jsonify({"message": "User deleted"}), 200)


# =======================================================
# PARKING LOT CRUD (Admin-only)
# =======================================================
class ParkingLotListAPI(Resource):
    @jwt_required()
    def get(self):
        admin = require_admin()
        if not admin:
            return {"message": "Admin access required"}, 403

        lots = ParkingLot.query.all()
        data = [{
            "id": lot.id,
            "prime_location_name": lot.prime_location_name,
            "price": lot.price,
            "address": lot.address,
            "pin_code": lot.pin_code,
            "max_spot": lot.max_spot
        } for lot in lots]
        return make_response(jsonify(data), 200)

    @jwt_required()
    def post(self):
        admin = require_admin()
        if not admin:
            return {"message": "Admin access required"}, 403

        data = request.get_json()
        if not data:
            return make_response(jsonify({"message": "Missing data"}), 400)

        prime_location_name = data.get('prime_location_name')
        price = data.get('price')
        address = data.get('address')
        pin_code = data.get('pin_code')
        max_spot = data.get('max_spot')

        if not prime_location_name or not price or not address or not pin_code or not max_spot:
            return make_response(jsonify({"message": "All fields are required"}), 400)

        new_lot = ParkingLot(
            prime_location_name=prime_location_name,
            price=price,
            address=address,
            pin_code=pin_code,
            max_spot=max_spot
        )
        db.session.add(new_lot)
        db.session.commit()

        # Auto-generate parking spots
        for i in range(new_lot.max_spot):
            spot = ParkingSpot(lot_id=new_lot.id, spot_number=i + 1, status="available")
            db.session.add(spot)
        db.session.commit()

        return make_response(jsonify({"message": "Parking lot created successfully"}), 201)


class ParkingLotAPI(Resource):
    @jwt_required()
    def get(self, lot_id):
        admin = require_admin()
        if not admin:
            return {"message": "Admin access required"}, 403

        lot = ParkingLot.query.get_or_404(lot_id)
        spots = ParkingSpot.query.filter_by(lot_id=lot.id).all()
        data = {
            "id": lot.id,
            "prime_location_name": lot.prime_location_name,
            "price": lot.price,
            "address": lot.address,
            "pin_code": lot.pin_code,
            "max_spot": lot.max_spot,
            "spots": [
                {"id": s.id, "spot_number": s.spot_number, "status": s.status}
                for s in spots
            ]
        }
        return make_response(jsonify(data), 200)

    @jwt_required()
    def put(self, lot_id):
        admin = require_admin()
        if not admin:
            return {"message": "Admin access required"}, 403

        data = request.get_json()
        lot = ParkingLot.query.get_or_404(lot_id)

        lot.prime_location_name = data.get('prime_location_name', lot.prime_location_name)
        lot.price = data.get('price', lot.price)
        lot.address = data.get('address', lot.address)
        lot.pin_code = data.get('pin_code', lot.pin_code)
        lot.max_spot = data.get('max_spot', lot.max_spot)

        db.session.commit()
        return make_response(jsonify({"message": "Parking lot updated successfully"}), 200)

    @jwt_required()
    def delete(self, lot_id):
        admin = require_admin()
        if not admin:
            return {"message": "Admin access required"}, 403

        lot = ParkingLot.query.get_or_404(lot_id)
        spots = ParkingSpot.query.filter_by(lot_id=lot.id).all()
        if any(s.status == "occupied" for s in spots):
            return make_response(jsonify({"message": "Cannot delete lot with occupied spots"}), 400)

        for s in spots:
            db.session.delete(s)
        db.session.delete(lot)
        db.session.commit()

        return make_response(jsonify({"message": "Parking lot deleted successfully"}), 200)


# =======================================================
# PARKING SPOT CRUD (Admin + User)
# =======================================================
class ParkingSpotListAPI(Resource):
    @jwt_required()
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
    @jwt_required()
    def put(self, spot_id):
        uid = get_jwt_identity()
        user = User.query.get(uid)
        data = request.get_json()
        spot = ParkingSpot.query.get_or_404(spot_id)

        if not data or 'status' not in data:
            return {"message": "Status is required"}, 400

        if any(r.name == 'user' for r in user.roles):
            if data['status'] not in ['available', 'occupied']:
                return {"message": "Invalid status"}, 400
            spot.status = data['status']
        else:
            spot.status = data.get('status', spot.status)

        db.session.commit()
        return make_response(jsonify({"message": "Spot updated"}), 200)


# =======================================================
# RESERVE & RELEASE PARKING (User actions)
# =======================================================
class ReserveParkingAPI(Resource):
    @jwt_required()
    def post(self):
        uid = get_jwt_identity()
        user = User.query.get(uid)
        data = request.get_json()
        lot_id = data.get('lot_id')

        if not lot_id:
            return make_response(jsonify({"message": "lot_id is required"}), 400)

        lot = ParkingLot.query.get(lot_id)
        if not lot:
            return make_response(jsonify({"message": "Invalid parking lot"}), 404)

        spot = ParkingSpot.query.filter_by(lot_id=lot.id, status="available").first()
        if not spot:
            return make_response(jsonify({"message": "No available spots in this lot"}), 400)

        spot.status = "occupied"
        spot.user_id = user.id
        spot.entry_time = datetime.now()

        db.session.commit()

        return make_response(jsonify({
            "message": "Parking spot reserved successfully",
            "lot_name": lot.prime_location_name,
            "spot_number": spot.spot_number,
            "entry_time": spot.entry_time.strftime("%Y-%m-%d %H:%M:%S")
        }), 200)


class ReleaseParkingAPI(Resource):
    @jwt_required()
    def post(self):
        uid = get_jwt_identity()
        user = User.query.get(uid)

        spot = ParkingSpot.query.filter_by(user_id=user.id, status="occupied").first()
        if not spot:
            return make_response(jsonify({"message": "No active reservation found"}), 404)

        spot.status = "available"
        spot.exit_time = datetime.now()
        spot.user_id = None

        duration = int((spot.exit_time - spot.entry_time).total_seconds() / 60)
        lot = ParkingLot.query.get(spot.lot_id)
        rate = lot.price if lot else 1.5
        cost = round(duration * rate, 2)

        db.session.commit()

        return make_response(jsonify({
            "message": "Spot released successfully",
            "spot_number": spot.spot_number,
            "exit_time": spot.exit_time.strftime("%Y-%m-%d %H:%M:%S"),
            "duration_minutes": duration,
            "cost": cost
        }), 200)
