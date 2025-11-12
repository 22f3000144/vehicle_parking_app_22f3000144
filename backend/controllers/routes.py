from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Role, ParkingLot, ParkingSpot, ReserveParking
from datetime import datetime



@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    model_name = data.get("model")
    password = data.get("password")

    if not all([username, email, password]):
        return jsonify({"message": "Missing required fields"}), 400

    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({"message": "User already exists"}), 409

    hashed_pw = generate_password_hash(password)
    new_user = User(username=username, email=email, model=model_name, password=hashed_pw)

    # Attach 'user' role automatically if exists
    user_role = Role.query.filter_by(name='user').first()
    if user_role:
        new_user.roles.append(user_role)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({"message": "Invalid credentials"}), 401

    token = user.token_id  # or generate JWT if needed
    roles = [role.name for role in user.roles]

    return jsonify({"user_details": {"auth_token": token, "roles": roles}}), 200


@app.route("/api/profile", methods=["GET"])
def profile():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = User.query.filter_by(token_id=token).first()
    if not user:
        return jsonify({"message": "Unauthorized"}), 401

    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "model": user.model,
        "roles": [role.name for role in user.roles]
    })


# -----------------------
# USER MANAGEMENT (ADMIN)
# -----------------------

@app.route("/api/users", methods=["GET"])
def list_users():
    users = User.query.all()
    return jsonify([
        {
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "model": u.model,
            "roles": [r.name for r in u.roles]
        } for u in users
    ])


@app.route("/api/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "model": user.model,
        "roles": [r.name for r in user.roles]
    })


# -----------------------
# PARKING LOTS
# -----------------------

@app.route("/api/lots", methods=["GET"])
def list_lots():
    lots = ParkingLot.query.all()
    return jsonify([
        {
            "id": lot.id,
            "prime_location_name": lot.prime_location_name,
            "price": lot.price,
            "address": lot.address,
            "pin_code": lot.pin_code,
            "max_spot": lot.max_spot
        } for lot in lots
    ])


@app.route("/api/lots/<int:lot_id>", methods=["GET"])
def get_lot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    return jsonify({
        "id": lot.id,
        "prime_location_name": lot.prime_location_name,
        "price": lot.price,
        "address": lot.address,
        "pin_code": lot.pin_code,
        "max_spot": lot.max_spot
    })


# -----------------------
# PARKING SPOTS
# -----------------------

@app.route("/api/spots", methods=["GET"])
def list_spots():
    spots = ParkingSpot.query.all()
    return jsonify([
        {
            "id": s.id,
            "lot_id": s.lot_id,
            "status": s.status,
            "user_id": s.user_id
        } for s in spots
    ])


@app.route("/api/spots/<int:spot_id>", methods=["GET"])
def get_spot(spot_id):
    spot = ParkingSpot.query.get_or_404(spot_id)
    return jsonify({
        "id": spot.id,
        "lot_id": spot.lot_id,
        "status": spot.status,
        "user_id": spot.user_id
    })


# -----------------------
# RESERVATION ROUTES (USER)
# -----------------------

@app.route("/api/reserve", methods=["POST"])
def reserve_spot():
    data = request.get_json()
    lot_id = data.get("lot_id")
    user_token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = User.query.filter_by(token_id=user_token).first()

    if not user:
        return jsonify({"message": "Unauthorized"}), 401

    available_spot = ParkingSpot.query.filter_by(lot_id=lot_id, status="A").first()
    if not available_spot:
        return jsonify({"message": "No available spots"}), 400

    available_spot.status = "O"
    available_spot.user_id = user.id
    available_spot.entry_time = datetime.utcnow()

    reservation = ReserveParking(user_id=user.id, spot_id=available_spot.id)
    db.session.add(reservation)
    db.session.commit()

    return jsonify({
        "message": "Spot reserved successfully",
        "spot_number": available_spot.id,
        "lot_name": available_spot.lot.prime_location_name,
        "entry_time": available_spot.entry_time
    })


@app.route("/api/release", methods=["POST"])
def release_spot():
    user_token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = User.query.filter_by(token_id=user_token).first()

    if not user:
        return jsonify({"message": "Unauthorized"}), 401

    spot = ParkingSpot.query.filter_by(user_id=user.id, status="O").first()
    if not spot:
        return jsonify({"message": "No reserved spot found"}), 400

    spot.status = "A"
    spot.exit_time = datetime.utcnow()
    reservation = ReserveParking.query.filter_by(spot_id=spot.id, user_id=user.id).first()
    duration_minutes = int((spot.exit_time - spot.entry_time).total_seconds() / 60)
    cost = duration_minutes * spot.lot.price

    reservation.leaving_timestamp = spot.exit_time
    reservation.parking_cost = cost
    spot.user_id = None
    spot.entry_time = None
    spot.exit_time = None

    db.session.commit()

    return jsonify({
        "message": "Spot released successfully",
        "duration_minutes": duration_minutes,
        "cost": cost
    })
from flask import jsonify
from models import db, ReserveParking, ParkingLot, User
from sqlalchemy import func
from datetime import datetime
import matplotlib.pyplot as plt
import io
import base64

# -----------------------
# USER CHARTS
# -----------------------

@app.route("/api/user/<int:user_id>/summary-chart", methods=["GET"])
def user_summary_chart(user_id):
    """
    Returns a base64 PNG chart of user's parking costs per month
    """
    user = User.query.get_or_404(user_id)

    # Aggregate parking cost per month
    results = db.session.query(
        func.strftime("%Y-%m", ReserveParking.parking_timestamp),
        func.sum(ReserveParking.parking_cost)
    ).filter_by(user_id=user.id).group_by(func.strftime("%Y-%m", ReserveParking.parking_timestamp)).all()

    months = [r[0] for r in results]
    costs = [r[1] or 0 for r in results]

    # Generate chart
    plt.figure(figsize=(8, 4))
    plt.bar(months, costs, color='teal')
    plt.title(f"{user.username} Parking Cost Summary")
    plt.xlabel("Month")
    plt.ylabel("Total Cost")
    plt.tight_layout()

    img = io.BytesIO()
    plt.savefig(img, format="png")
    img.seek(0)
    chart_url = "data:image/png;base64," + base64.b64encode(img.getvalue()).decode()
    plt.close()

    return jsonify({"chart_url": chart_url})


# -----------------------
# ADMIN CHARTS
# -----------------------

@app.route("/api/admin/reservation-chart", methods=["GET"])
def admin_reservation_chart():
    """
    Returns a base64 PNG chart of reservations per parking lot
    """
    results = db.session.query(
        ParkingLot.prime_location_name,
        func.count(ReserveParking.id)
    ).join(ParkingLot.spots).join(ReserveParking, isouter=True).group_by(ParkingLot.id).all()

    lots = [r[0] for r in results]
    reservations = [r[1] for r in results]

    # Generate chart
    plt.figure(figsize=(8, 4))
    plt.bar(lots, reservations, color='orange')
    plt.title("Reservation Records per Parking Lot")
    plt.xlabel("Parking Lot")
    plt.ylabel("Number of Reservations")
    plt.xticks(rotation=45)
    plt.tight_layout()

    img = io.BytesIO()
    plt.savefig(img, format="png")
    img.seek(0)
    chart_url = "data:image/png;base64," + base64.b64encode(img.getvalue()).decode()
    plt.close()

    return jsonify({"chart_url": chart_url})
