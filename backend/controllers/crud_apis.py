


from flask_restful import Resource
from flask import request, jsonify, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity
from data.models import db, User, Role, UserRole, ParkingLot, ParkingSpot, ReserveParking
from datetime import datetime
from sqlalchemy import func


# Helper: Check if current user is admin

def require_admin():
    uid = get_jwt_identity()
    user = User.query.get(uid)
    if not user or not any(r.name == 'admin' for r in user.roles):
        return None
    return user

# Helper: convert DB status (A/O) to API label and vice versa
def db_status_to_label(db_status):
    return "available" if db_status == "A" else "occupied"

def label_to_db_status(label):
    if label == "available":
        return "A"
    return "O"


# USER CRUD (Admin-only)

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



# ROLE CRUD (Admin-only)

class RoleListAPI(Resource):
    @jwt_required()
    def get(self):
        admin = require_admin()
        if not admin:
            return {"message": "Admin access required"}, 403

        roles = Role.query.all()
        data = [{"id": r.id, "name": r.name, "description": r.description} for r in roles]
        return make_response(jsonify(data), 200)

    @jwt_required()
    def post(self):
        admin = require_admin()
        if not admin:
            return {"message": "Admin access required"}, 403

        data = request.get_json()
        name = data.get("name")
        description = data.get("description", "")

        if not name:
            return make_response(jsonify({"message": "Role name required"}), 400)

        if Role.query.filter_by(name=name).first():
            return make_response(jsonify({"message": "Role already exists"}), 409)

        new_role = Role(name=name, description=description)
        db.session.add(new_role)
        db.session.commit()
        return make_response(jsonify({"message": "Role created"}), 201)


class RoleAPI(Resource):
    @jwt_required()
    def get(self, role_id):
        admin = require_admin()
        if not admin:
            return {"message": "Admin access required"}, 403
        role = Role.query.get_or_404(role_id)
        return make_response(jsonify({"id": role.id, "name": role.name, "description": role.description}), 200)

    @jwt_required()
    def put(self, role_id):
        admin = require_admin()
        if not admin:
            return {"message": "Admin access required"}, 403
        data = request.get_json()
        role = Role.query.get_or_404(role_id)
        role.name = data.get("name", role.name)
        role.description = data.get("description", role.description)
        db.session.commit()
        return make_response(jsonify({"message": "Role updated"}), 200)

    @jwt_required()
    def delete(self, role_id):
        admin = require_admin()
        if not admin:
            return {"message": "Admin access required"}, 403
        role = Role.query.get_or_404(role_id)
        db.session.delete(role)
        db.session.commit()
        return make_response(jsonify({"message": "Role deleted"}), 200)



# PARKING LOT CRUD (Admin-only)

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

        # Auto-generate parking spots with sequential spot_number
        for i in range(new_lot.max_spot):
            spot = ParkingSpot(lot_id=new_lot.id, spot_number=i + 1, status='A')
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
                {"id": s.id, "spot_number": s.spot_number, "status": db_status_to_label(s.status)}
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

        # updating fields
        lot.prime_location_name = data.get('prime_location_name', lot.prime_location_name)
        lot.price = data.get('price', lot.price)
        lot.address = data.get('address', lot.address)
        lot.pin_code = data.get('pin_code', lot.pin_code)
        new_max = data.get('max_spot', lot.max_spot)

        # If max_spot changed, handle add/remove spots
        if int(new_max) != lot.max_spot:
            # if reducing, ensure removable spots are available
            if int(new_max) < lot.max_spot:
                removable = ParkingSpot.query.filter_by(lot_id=lot.id, status='A').order_by(ParkingSpot.spot_number.desc()).all()
                remove_count = lot.max_spot - int(new_max)
                if len(removable) < remove_count:
                    return make_response(jsonify({"message": "Cannot reduce spots: some spots are occupied"}), 400)
                for s in removable[:remove_count]:
                    db.session.delete(s)
            else:
                # add new spots with next spot_number sequence
                start = db.session.query(func.max(ParkingSpot.spot_number)).filter_by(lot_id=lot.id).scalar() or 0
                for i in range(1, int(new_max) - lot.max_spot + 1):
                    spot = ParkingSpot(lot_id=lot.id, spot_number=start + i, status='A')
                    db.session.add(spot)
            lot.max_spot = int(new_max)

        db.session.commit()
        return make_response(jsonify({"message": "Parking lot updated successfully"}), 200)

    @jwt_required()
    def delete(self, lot_id):
        admin = require_admin()
        if not admin:
            return {"message": "Admin access required"}, 403

        lot = ParkingLot.query.get_or_404(lot_id)
        spots = ParkingSpot.query.filter_by(lot_id=lot.id).all()
        if any(s.status == "O" for s in spots):
            return make_response(jsonify({"message": "Cannot delete lot with occupied spots"}), 400)

        for s in spots:
            db.session.delete(s)
        db.session.delete(lot)
        db.session.commit()

        return make_response(jsonify({"message": "Parking lot deleted successfully"}), 200)



# PARKING SPOT CRUD (Admin + User)

class ParkingSpotListAPI(Resource):
    @jwt_required()
    def get(self):
        spots = ParkingSpot.query.all()
        data = [{
            "id": s.id,
            "lot_id": s.lot_id,
            "spot_number": s.spot_number,
            "status": db_status_to_label(s.status)
        } for s in spots]
        return make_response(jsonify(data), 200)

    @jwt_required()
    def post(self):
        admin = require_admin()
        if not admin:
            return {"message": "Admin access required"}, 403

        data = request.get_json()
        lot_id = data.get('lot_id')
        if not lot_id:
            return make_response(jsonify({"message": "lot_id is required"}), 400)
        lot = ParkingLot.query.get(lot_id)
        if not lot:
            return make_response(jsonify({"message": "Invalid lot"}), 404)

        # compute next spot number
        start = db.session.query(func.max(ParkingSpot.spot_number)).filter_by(lot_id=lot.id).scalar() or 0
        spot = ParkingSpot(lot_id=lot.id, spot_number=start + 1, status='A')
        db.session.add(spot)
        lot.max_spot = lot.max_spot + 1
        db.session.commit()

        return make_response(jsonify({"message": "Spot added", "spot_id": spot.id}), 201)


class ParkingSpotAPI(Resource):
    @jwt_required()
    def get(self, spot_id):
        spot = ParkingSpot.query.get_or_404(spot_id)
        data = {
            "id": spot.id,
            "lot_id": spot.lot_id,
            "spot_number": spot.spot_number,
            "status": db_status_to_label(spot.status),
            "user_id": spot.user_id,
            "entry_time": spot.entry_time.strftime("%Y-%m-%d %H:%M:%S") if spot.entry_time else None
        }
        return make_response(jsonify(data), 200)

    @jwt_required()
    def put(self, spot_id):
        uid = get_jwt_identity()
        user = User.query.get(uid)
        data = request.get_json()
        spot = ParkingSpot.query.get_or_404(spot_id)

        if not data or 'status' not in data:
            return {"message": "Status is required"}, 400

        # Accept friendly labels ("available"/"occupied")
        new_label = data['status']
        if new_label not in ['available', 'occupied']:
            return {"message": "Invalid status"}, 400

        # Users can toggle their own spot status between available/occupied if needed
        if any(r.name == 'user' for r in user.roles):
            # allow changing only if they own the spot or it's a toggle to release
            if spot.user_id and spot.user_id != user.id and new_label == 'occupied':
                return {"message": "Cannot occupy another user's spot"}, 403

        spot.status = label_to_db_status(new_label)
        if new_label == 'occupied':
            spot.user_id = uid
            spot.entry_time = datetime.now()
        else:
            # releasing
            spot.user_id = None
            spot.exit_time = datetime.now()

        db.session.commit()
        return make_response(jsonify({"message": "Spot updated"}), 200)



# RESERVE & RELEASE PARKING (User actions)

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

        # find first available spot
        spot = ParkingSpot.query.filter_by(lot_id=lot.id, status='A').order_by(ParkingSpot.spot_number).first()
        if not spot:
            return make_response(jsonify({"message": "No available spots in this lot"}), 400)

        spot.status = 'O'
        spot.user_id = user.id
        spot.entry_time = datetime.now()

        reservation = ReserveParking(user_id=user.id, spot_id=spot.id, parking_timestamp=spot.entry_time)
        db.session.add(reservation)
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

        spot = ParkingSpot.query.filter_by(user_id=user.id, status='O').first()
        if not spot:
            return make_response(jsonify({"message": "No active reservation found"}), 404)

        spot.status = 'A'
        spot.exit_time = datetime.now()
        # find latest reservation for this spot and user that does not have leaving_timestamp
        reservation = ReserveParking.query.filter_by(spot_id=spot.id, user_id=user.id).order_by(ReserveParking.parking_timestamp.desc()).first()
        if reservation:
            reservation.leaving_timestamp = spot.exit_time
            duration = int((reservation.leaving_timestamp - reservation.parking_timestamp).total_seconds() / 60)
            lot = ParkingLot.query.get(spot.lot_id)
            rate = lot.price if lot else 1.5
            cost = round(duration * rate, 2)
            reservation.parking_cost = cost
        else:
            duration = 0
            cost = 0.0

        spot.user_id = None
        spot.entry_time = None

        db.session.commit()

        return make_response(jsonify({
            "message": "Spot released successfully",
            "spot_number": spot.spot_number,
            "exit_time": spot.exit_time.strftime("%Y-%m-%d %H:%M:%S"),
            "duration_minutes": duration,
            "cost": cost
        }), 200)



# RESERVATION HISTORY (User / Admin)

class ReserveHistoryAPI(Resource):
    @jwt_required()
    def get(self):
        uid = get_jwt_identity()
        user = User.query.get(uid)
        admin = require_admin()

        if admin:
            # admin can see all reservations
            reservations = ReserveParking.query.order_by(ReserveParking.parking_timestamp.desc()).all()
        else:
            reservations = ReserveParking.query.filter_by(user_id=uid).order_by(ReserveParking.parking_timestamp.desc()).all()

        data = []
        for r in reservations:
            spot = ParkingSpot.query.get(r.spot_id)
            lot = ParkingLot.query.get(spot.lot_id) if spot else None
            data.append({
                "id": r.id,
                "user_id": r.user_id,
                "spot_id": r.spot_id,
                "lot_id": lot.id if lot else None,
                "lot_name": lot.prime_location_name if lot else None,
                "spot_number": spot.spot_number if spot else None,
                "parking_timestamp": r.parking_timestamp.strftime("%Y-%m-%d %H:%M:%S") if r.parking_timestamp else None,
                "leaving_timestamp": r.leaving_timestamp.strftime("%Y-%m-%d %H:%M:%S") if r.leaving_timestamp else None,
                "parking_cost": float(r.parking_cost) if r.parking_cost is not None else None
            })
        return make_response(jsonify(data), 200)


class ReserveDetailAPI(Resource):
    @jwt_required()
    def get(self, reservation_id):
        uid = get_jwt_identity()
        admin = require_admin()

        reservation = ReserveParking.query.get_or_404(reservation_id)
        if not admin and reservation.user_id != uid:
            return {"message": "Access denied"}, 403

        spot = ParkingSpot.query.get(reservation.spot_id)
        lot = ParkingLot.query.get(spot.lot_id) if spot else None
        data = {
            "id": reservation.id,
            "user_id": reservation.user_id,
            "spot_id": reservation.spot_id,
            "lot_id": lot.id if lot else None,
            "lot_name": lot.prime_location_name if lot else None,
            "spot_number": spot.spot_number if spot else None,
            "parking_timestamp": reservation.parking_timestamp.strftime("%Y-%m-%d %H:%M:%S") if reservation.parking_timestamp else None,
            "leaving_timestamp": reservation.leaving_timestamp.strftime("%Y-%m-%d %H:%M:%S") if reservation.leaving_timestamp else None,
            "parking_cost": float(reservation.parking_cost) if reservation.parking_cost is not None else None
        }
        return make_response(jsonify(data), 200)



# CHARTS & ADMIN STATS

class UserSummaryChartAPI(Resource):
    """User dashboard: monthly parking cost summary"""
    @jwt_required()
    def get(self):
        """
        Return JSON suitable for charting for the current user
        /api/user/summary  (no user_id param; uses token identity)
        """
        uid = get_jwt_identity()
        user = User.query.get_or_404(uid)

        results = db.session.query(
            func.strftime("%Y-%m", ReserveParking.parking_timestamp),
            func.sum(ReserveParking.parking_cost)
        ).filter(ReserveParking.user_id == user.id).group_by(func.strftime("%Y-%m", ReserveParking.parking_timestamp)).all()

        months = [r[0] for r in results]
        costs = [float(r[1] or 0) for r in results]

        return make_response(jsonify({"months": months, "costs": costs}), 200)


class AdminSummaryChartAPI(Resource):
    """Admin summary data for dashboard"""
    @jwt_required()
    def get(self):
        admin = require_admin()
        if not admin:
            return {"message": "Admin access required"}, 403

        total_users = User.query.count()
        total_lots = ParkingLot.query.count()
        total_spots = ParkingSpot.query.count()
        total_reservations = ReserveParking.query.count()

        occupied_spots = ParkingSpot.query.filter_by(status='O').count()
        available_spots = ParkingSpot.query.filter_by(status='A').count()

        data = {
            "total_users": total_users,
            "total_lots": total_lots,
            "total_spots": total_spots,
            "total_reservations": total_reservations,
            "occupied_spots": occupied_spots,
            "available_spots": available_spots
        }
        return make_response(jsonify(data), 200)


class AdminParkingStatsAPI(Resource):
    """Admin parking stats for charts (reservations per lot, occupancy rate, revenue per lot)"""
    @jwt_required()
    def get(self):
        admin = require_admin()
        if not admin:
            return {"message": "Admin access required"}, 403

        # reservations per lot
        res_per_lot = db.session.query(
            ParkingLot.prime_location_name,
            func.count(ReserveParking.id).label("reservations")
        ).join(ParkingLot.spots).join(ReserveParking, isouter=True).group_by(ParkingLot.id).all()

        # revenue per lot
        revenue_per_lot = db.session.query(
            ParkingLot.prime_location_name,
            func.coalesce(func.sum(ReserveParking.parking_cost), 0).label("revenue")
        ).join(ParkingLot.spots).join(ReserveParking, isouter=True).group_by(ParkingLot.id).all()

        lots = [r[0] for r in res_per_lot]
        reservations = [int(r[1]) for r in res_per_lot]
        revenues = [float(next((x[1] for x in revenue_per_lot if x[0] == r[0]), 0)) for r in res_per_lot]

        # occupancy rate per lot
        occupancy = []
        for lot in ParkingLot.query.all():
            total = ParkingSpot.query.filter_by(lot_id=lot.id).count()
            occupied = ParkingSpot.query.filter_by(lot_id=lot.id, status='O').count()
            rate = round((occupied / total) * 100, 2) if total > 0 else 0.0
            occupancy.append({"lot": lot.prime_location_name, "occupancy_rate": rate})

        data = {
            "lots": lots,
            "reservations": reservations,
            "revenues": revenues,
            "occupancy": occupancy
        }
        return make_response(jsonify(data), 200)



# USER PARKING STATUS

class UserParkingStatusAPI(Resource):
    """Return current user's active reservation/spot (if any)"""
    @jwt_required()
    def get(self):
        uid = get_jwt_identity()
        user = User.query.get_or_404(uid)

        spot = ParkingSpot.query.filter_by(user_id=user.id, status='O').first()
        if not spot:
            return make_response(jsonify({"active": False}), 200)

        lot = ParkingLot.query.get(spot.lot_id)
        reservation = ReserveParking.query.filter_by(user_id=user.id, spot_id=spot.id).order_by(ReserveParking.parking_timestamp.desc()).first()

        data = {
            "active": True,
            "spot_id": spot.id,
            "spot_number": spot.spot_number,
            "lot_id": lot.id if lot else None,
            "lot_name": lot.prime_location_name if lot else None,
            "entry_time": spot.entry_time.strftime("%Y-%m-%d %H:%M:%S") if spot.entry_time else None,
            "reservation_id": reservation.id if reservation else None
        }
        return make_response(jsonify(data), 200)



# EXPORTS / REPORT ENDPOINT (trigger async tasks)

class ExportUserHistoryAPI(Resource):
    """Trigger CSV export for a user's reservation history (fires Celery task)"""
    @jwt_required()
    def post(self):
        uid = get_jwt_identity()
        # here you can enqueue a celery task, e.g. export_user_history_csv.apply_async([uid])
        # to keep this file independent of Celery internals, we'll just simulate enqueueing
        try:
            from jobs.tasks import export_user_history_csv
            task = export_user_history_csv.apply_async(args=[uid])
            return make_response(jsonify({"message": "Export started", "task_id": task.id}), 202)
        except Exception as e:
            return make_response(jsonify({"message": f"Failed to start export: {str(e)}"}), 500)


class MonthlyReportAPI(Resource):
    """Endpoint to trigger monthly report generation (admin only)"""
    @jwt_required()
    def post(self):
        admin = require_admin()
        if not admin:
            return {"message": "Admin access required"}, 403
        try:
            from jobs.tasks import monthly_activity_report
            monthly_activity_report.apply_async()
            return make_response(jsonify({"message": "Monthly report scheduled"}), 202)
        except Exception as e:
            return make_response(jsonify({"message": f"Failed to schedule report: {str(e)}"}), 500)
