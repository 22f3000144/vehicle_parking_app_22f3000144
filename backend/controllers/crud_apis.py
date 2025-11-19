# controllers/crud_api.py
from datetime import datetime, timedelta
from flask import request, jsonify, make_response
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import SQLAlchemyError
from celery import current_app as celery_app
from data.models import db, User, Role, UserRole, ParkingLot, ParkingSpot, ReserveParking
from sqlalchemy import func


# Helper: admin check (safe, simple)

def is_admin(user_id):
    if not user_id:
        return False
    user = User.query.get(user_id)
    if not user:
        return False
    return any(r.name == "admin" for r in user.roles)



# USER LIST (ADMIN ONLY)

class UserListAPI(Resource):

    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        if not is_admin(user_id):
            return make_response(jsonify({"message": "Admin only"}), 403)

        users = User.query.all()
        data = []
        for u in users:
            data.append({
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "model": u.model
            })
        return make_response(jsonify(data), 200)



# USER CRUD (combined: GET one, PUT full-update, DELETE)

class UserAPI(Resource):

    @jwt_required()
    def get(self, user_id):
        current = get_jwt_identity()
        # allow admin or owner
        if not (is_admin(current) or current == user_id):
            return make_response(jsonify({"message": "Unauthorized"}), 403)

        user = User.query.get(user_id)
        if not user:
            return make_response(jsonify({"message": "User not found"}), 404)

        data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "model": user.model,
            "active": user.active
        }
        return make_response(jsonify(data), 200)


    @jwt_required()
    def put(self, user_id):
        # strict full update: all required fields must be present
        current = get_jwt_identity()
        if not (is_admin(current) or current == user_id):
            return make_response(jsonify({"message": "Unauthorized"}), 403)

        payload = request.get_json()
        required = ["username", "email", "password", "model", "active"]
        for f in required:
            if f not in payload:
                return make_response(jsonify({"message": f"{f} is required"}), 400)

        user = User.query.get(user_id)
        if not user:
            return make_response(jsonify({"message": "User not found"}), 404)

        try:
            user.username = payload["username"]
            user.email = payload["email"]
            user.password = generate_password_hash(payload["password"])
            user.model = payload["model"]
            user.active = bool(payload["active"])
            db.session.commit()
            return make_response(jsonify({"message": "User updated"}), 200)
        except SQLAlchemyError as e:
            db.session.rollback()
            return make_response(jsonify({"message": str(e)}), 500)


    @jwt_required()
    def delete(self, user_id):
        current = get_jwt_identity()
        if not is_admin(current):
            return make_response(jsonify({"message": "Admin only"}), 403)

        user = User.query.get(user_id)
        if not user:
            return make_response(jsonify({"message": "User not found"}), 404)

        try:
            db.session.delete(user)
            db.session.commit()
            return make_response(jsonify({"message": "User deleted"}), 200)
        except SQLAlchemyError as e:
            db.session.rollback()
            return make_response(jsonify({"message": str(e)}), 500)



# PARKING LOTS (combined GET all/one, POST create, PUT full-update, DELETE safe)

class ParkingLotAPI(Resource):

    def get(self, lot_id=None):
        if lot_id:
            lot = ParkingLot.query.get(lot_id)
            if not lot:
                return make_response(jsonify({"message": "Parking lot not found."}), 404)

            response = {
                "id": lot.id,
                "prime_location_name": lot.prime_location_name,
                "price": float(lot.price) if lot.price is not None else None,
                "address": lot.address,
                "pin_code": lot.pin_code,
                "max_spot": lot.max_spot,
                "spots": [{"id": s.id, "spot_number": s.spot_number, "status": s.status} for s in lot.spots]
            }
            return make_response(jsonify(response), 200)

        lots = ParkingLot.query.all()
        response = []
        for lot in lots:
            lot_data = {
                "id": lot.id,
                "prime_location_name": lot.prime_location_name,
                "price": float(lot.price) if lot.price is not None else None,
                "address": lot.address,
                "pin_code": lot.pin_code,
                "max_spot": lot.max_spot,
                "spots": [{"id": s.id, "spot_number": s.spot_number, "status": s.status} for s in lot.spots]
            }
            response.append(lot_data)
        return make_response(jsonify(response), 200)


    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        if not is_admin(user_id):
            return make_response(jsonify({"message": "Admin only"}), 403)

        data = request.get_json()
        if not data:
            return make_response(jsonify({"message": "No data received"}), 400)

        required_fields = ["prime_location_name", "price", "address", "pin_code", "max_spot"]
        for field in required_fields:
            if field not in data or data[field] == "":
                return make_response(jsonify({"message": f"{field} is required"}), 400)

        try:
            new_lot = ParkingLot(
                prime_location_name=data["prime_location_name"],
                price=float(data["price"]),
                address=data["address"],
                pin_code=data["pin_code"],
                max_spot=int(data["max_spot"])
            )
            db.session.add(new_lot)
            db.session.commit()

            # Auto-generate spots
            for i in range(1, new_lot.max_spot + 1):
                db.session.add(ParkingSpot(lot_id=new_lot.id, spot_number=i, status='A'))
            db.session.commit()

            return make_response(jsonify({
                "message": "Parking lot created successfully",
                "lot": {
                    "id": new_lot.id,
                    "prime_location_name": new_lot.prime_location_name,
                    "price": new_lot.price,
                    "address": new_lot.address,
                    "pin_code": new_lot.pin_code,
                    "max_spot": new_lot.max_spot
                }
            }), 201)
        except SQLAlchemyError as e:
            db.session.rollback()
            return make_response(jsonify({"message": str(e)}), 500)


    @jwt_required()
    def put(self, lot_id):
        user_id = get_jwt_identity()
        if not is_admin(user_id):
            return make_response(jsonify({"message": "Admin only"}), 403)

        lot = ParkingLot.query.get(lot_id)
        if not lot:
            return make_response(jsonify({"message": "Parking lot not found"}), 404)

        data = request.get_json()
        required_fields = ["prime_location_name", "price", "address", "pin_code", "max_spot"]
        for field in required_fields:
            if field not in data:
                return make_response(jsonify({"message": f"{field} is required"}), 400)

        try:
            lot.prime_location_name = data["prime_location_name"]
            lot.price = float(data["price"])
            lot.address = data["address"]
            lot.pin_code = data["pin_code"]
            lot.max_spot = int(data["max_spot"])
            db.session.commit()
            return make_response(jsonify({"message": "Parking lot updated"}), 200)
        except SQLAlchemyError as e:
            db.session.rollback()
            return make_response(jsonify({"message": str(e)}), 500)


    @jwt_required()
    def delete(self, lot_id):
        user_id = get_jwt_identity()
        if not is_admin(user_id):
            return make_response(jsonify({"message": "Admin only"}), 403)

        lot = ParkingLot.query.get(lot_id)
        if not lot:
            return make_response(jsonify({"message": "Parking lot not found"}), 404)

        # only allow delete if all spots are available
        for spot in lot.spots:
            if spot.status != 'A':
                return make_response(jsonify({"message": f"Cannot delete: spot {spot.spot_number} is occupied."}), 400)

        try:
            db.session.delete(lot)
            db.session.commit()
            return make_response(jsonify({"message": "Parking lot deleted successfully"}), 200)
        except SQLAlchemyError as e:
            db.session.rollback()
            return make_response(jsonify({"message": str(e)}), 500)



# PARKING SPOT API (combined)

class ParkingSpotAPI(Resource):

    @jwt_required()
    def get(self, spot_id=None):
        if spot_id:
            s = ParkingSpot.query.get(spot_id)
            if not s:
                return make_response(jsonify({"message": "Spot not found"}), 404)
            data = {
                "id": s.id,
                "lot_id": s.lot_id,
                "spot_number": s.spot_number,
                "status": s.status,
                "user_id": s.user_id,
                "entry_time": s.entry_time,
                "exit_time": s.exit_time
            }
            return make_response(jsonify(data), 200)

        spots = ParkingSpot.query.all()
        data = []
        for s in spots:
            data.append({
                "id": s.id,
                "lot_id": s.lot_id,
                "spot_number": s.spot_number,
                "status": s.status,
                "user_id": s.user_id
            })
        return make_response(jsonify(data), 200)


    @jwt_required()
    def put(self, spot_id):
        # Admin-only full update
        user_id = get_jwt_identity()
        if not is_admin(user_id):
            return make_response(jsonify({"message": "Admin only"}), 403)

        spot = ParkingSpot.query.get(spot_id)
        if not spot:
            return make_response(jsonify({"message": "Spot not found"}), 404)

        data = request.get_json()
        required_fields = ["lot_id", "spot_number", "status", "user_id"]
        for field in required_fields:
            if field not in data:
                return make_response(jsonify({"message": f"{field} is required"}), 400)

        try:
            spot.lot_id = int(data["lot_id"])
            spot.spot_number = int(data["spot_number"])
            spot.status = data["status"]
            spot.user_id = int(data["user_id"]) if data["user_id"] is not None else None
            db.session.commit()
            return make_response(jsonify({"message": "Spot updated"}), 200)
        except SQLAlchemyError as e:
            db.session.rollback()
            return make_response(jsonify({"message": str(e)}), 500)



# RESERVATION APIs (reserve, release, history, detail)

class ReserveParkingAPI(Resource):

    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        data = request.get_json()
        if not data or "spot_id" not in data:
            return make_response(jsonify({"message": "spot_id is required"}), 400)

        spot = ParkingSpot.query.get(data["spot_id"])
        if not spot:
            return make_response(jsonify({"message": "Spot not found"}), 404)

        if spot.status != 'A':
            return make_response(jsonify({"message": "Spot already occupied"}), 400)

        try:
            spot.status = 'O'
            spot.user_id = user_id
            spot.entry_time = datetime.utcnow()

            reservation = ReserveParking(spot_id=spot.id, user_id=user_id)
            db.session.add(reservation)
            db.session.commit()
            return make_response(jsonify({"message": "Spot reserved", "reservation_id": reservation.id}), 201)
        except SQLAlchemyError as e:
            db.session.rollback()
            return make_response(jsonify({"message": str(e)}), 500)


class ReleaseParkingAPI(Resource):

    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        data = request.get_json()
        if not data or "spot_id" not in data:
            return make_response(jsonify({"message": "spot_id is required"}), 400)

        spot = ParkingSpot.query.get(data["spot_id"])
        if not spot:
            return make_response(jsonify({"message": "Spot not found"}), 404)

        if spot.user_id != user_id and not is_admin(user_id):
            return make_response(jsonify({"message": "You do not own this reservation"}), 403)

        try:
            spot.status = 'A'
            spot.user_id = None
            spot.exit_time = datetime.utcnow()

            reservation = ReserveParking.query.filter_by(spot_id=spot.id, user_id=user_id, leaving_timestamp=None).first()
            if reservation:
                reservation.leaving_timestamp = datetime.utcnow()
                # Calculate parking cost if needed (example: simple duration * lot price)
                lot = ParkingLot.query.get(spot.lot_id)
                if lot and reservation.parking_timestamp:
                    seconds = (reservation.leaving_timestamp - reservation.parking_timestamp).total_seconds()
                    hours = max(1, int(seconds // 3600))  # basic rounding up
                    reservation.parking_cost = hours * lot.price

            db.session.commit()
            return make_response(jsonify({"message": "Spot released"}), 200)
        except SQLAlchemyError as e:
            db.session.rollback()
            return make_response(jsonify({"message": str(e)}), 500)


class ReserveHistoryAPI(Resource):

    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        history = ReserveParking.query.filter_by(user_id=user_id).order_by(ReserveParking.parking_timestamp.desc()).all()
        data = []
        for h in history:
            data.append({
                "id": h.id,
                "spot_id": h.spot_id,
                "parking_timestamp": h.parking_timestamp,
                "leaving_timestamp": h.leaving_timestamp,
                "parking_cost": h.parking_cost
            })
        return make_response(jsonify(data), 200)


class ReserveDetailAPI(Resource):

    @jwt_required()
    def get(self, reservation_id):
        user_id = get_jwt_identity()
        res = ReserveParking.query.get(reservation_id)
        if not res:
            return make_response(jsonify({"message": "Reservation not found"}), 404)

        if res.user_id != user_id and not is_admin(user_id):
            return make_response(jsonify({"message": "Unauthorized"}), 403)

        data = {
            "id": res.id,
            "spot_id": res.spot_id,
            "user_id": res.user_id,
            "parking_timestamp": res.parking_timestamp,
            "leaving_timestamp": res.leaving_timestamp,
            "parking_cost": res.parking_cost
        }
        return make_response(jsonify(data), 200)



# ADMIN & USER DASHBOARDS (combined endpoints)

class AdminSummaryChartAPI(Resource):

    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        if not is_admin(user_id):
            return make_response(jsonify({"message": "Admin only"}), 403)

        total_lots = ParkingLot.query.count()
        total_spots = ParkingSpot.query.count()
        occupied_spots = ParkingSpot.query.filter_by(status='O').count()
        available_spots = total_spots - occupied_spots

        lot_usage = []
        lots = ParkingLot.query.all()
        for lot in lots:
            used = ParkingSpot.query.filter_by(lot_id=lot.id, status='O').count()
            lot_usage.append({"lot_id": lot.id, "lot_name": lot.prime_location_name, "used": used, "total": lot.max_spot})

        # daily reservations last 7 days
        daily_data = []
        today = datetime.utcnow().date()
        for i in range(7):
            day = today - timedelta(days=i)
            count = ReserveParking.query.filter(func.date(ReserveParking.parking_timestamp) == day).count()
            daily_data.append({"date": day.strftime("%Y-%m-%d"), "reservations": count})

        return make_response(jsonify({
            "total_lots": total_lots,
            "total_spots": total_spots,
            "occupied_spots": occupied_spots,
            "available_spots": available_spots,
            "lot_usage": lot_usage,
            "daily_reservations": list(reversed(daily_data))
        }), 200)


class AdminParkingStatsAPI(Resource):

    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        if not is_admin(user_id):
            return make_response(jsonify({"message": "Admin only"}), 403)

        stats = []
        lots = ParkingLot.query.all()
        for lot in lots:
            total = ParkingSpot.query.filter_by(lot_id=lot.id).count()
            occupied = ParkingSpot.query.filter_by(lot_id=lot.id, status='O').count()
            stats.append({"lot_id": lot.id, "lot_name": lot.prime_location_name, "total_spots": total, "occupied_spots": occupied, "available_spots": total - occupied})

        return make_response(jsonify({"data": stats}), 200)


class UserSummaryChartAPI(Resource):

    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        total_reservations = ReserveParking.query.filter_by(user_id=user_id).count()
        active_res = ReserveParking.query.filter_by(user_id=user_id, leaving_timestamp=None).first()

        active_data = None
        if active_res:
            active_data = {"spot_id": active_res.spot_id, "parking_timestamp": active_res.parking_timestamp}

        monthly = []
        today = datetime.utcnow().date()
        for i in range(6):
            month_date = (today.replace(day=1) - timedelta(days=30*i))
            month_str = month_date.strftime("%Y-%m")
            count = ReserveParking.query.filter(ReserveParking.user_id == user_id, func.strftime("%Y-%m", ReserveParking.parking_timestamp) == month_str).count()
            monthly.append({"month": month_str, "count": count})

        return make_response(jsonify({"total_reservations": total_reservations, "active_reservation": active_data, "monthly_usage": list(reversed(monthly))}), 200)


class UserParkingStatusAPI(Resource):

    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        spot = ParkingSpot.query.filter_by(user_id=user_id, status='O').first()
        if not spot:
            return make_response(jsonify({"active": False}), 200)

        lot = ParkingLot.query.get(spot.lot_id)
        return make_response(jsonify({"active": True, "spot_number": spot.spot_number, "lot_name": lot.prime_location_name, "entry_time": spot.entry_time}), 200)



# EXPORT APIs (trigger celery export jobs, check status)

class ExportHistoryAPI(Resource):

    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        # Kick off celery task named "tasks.export_parking_history"
        try:
            task = celery_app.send_task("tasks.export_parking_history", args=[user_id])
            return make_response(jsonify({"message": "Export started", "task_id": task.id}), 202)
        except Exception as e:
            return make_response(jsonify({"message": str(e)}), 500)


class ExportStatusAPI(Resource):

    @jwt_required()
    def get(self):
        task_id = request.args.get("task_id")
        if not task_id:
            return make_response(jsonify({"message": "task_id is required"}), 400)

        res = celery_app.AsyncResult(task_id)
        return make_response(jsonify({"task_id": task_id, "status": res.status, "ready": res.ready(), "result": res.result if res.ready() else None}), 200)
