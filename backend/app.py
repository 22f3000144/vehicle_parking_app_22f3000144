import os
from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from flask_security import Security, SQLAlchemySessionUserDatastore
from controllers.settings import LocalDevelopmentConfig, Config
from data.models import *
from flask_jwt_extended import JWTManager
from flask_caching import Cache
from werkzeug.security import generate_password_hash
from jobs import workers
from jobs.tasks import *
from flask_cors import CORS

app = None
api = None
celery = None
cache = None


def create_admin_user(app, user_datastore):
    """Ensure admin role and user exist."""
    with app.app_context():
        # Create 'admin' role if not exists
        admin_role = Role.query.filter_by(name='admin').first()
        if not admin_role:
            admin_role = Role(name='admin', description='Administrator role')
            db.session.add(admin_role)
            db.session.commit()

        # Create admin user if not exists
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='Ayush',
                email='my@gmail.com',
                model='Bogati',  # optional placeholder
                password='my_app',  # hashed password
                unique_id='admin-uuid',
                token_id='admin-token'
            )
            db.session.add(admin_user)
            db.session.commit()

        # Link user with role
        user_role = UserRole(user_id=admin_user.id, role_id=admin_role.id)
        db.session.add(user_role)
        db.session.commit()


def create_app():
    app = Flask(__name__)
    app.config.from_object(LocalDevelopmentConfig)

    # Initialize extensions
    db.init_app(app)
    api = Api(app)
    jwt = JWTManager(app)
    cache = Cache(app)

    CORS(app, resources={
        r"/api/*": {
            "origins": [
                "http://localhost:5173",
                "http://127.0.0.1:5173"
            ]
        }
    })

    # Flask-Security setup
    user_datastore = SQLAlchemySessionUserDatastore(db.session, User, Role)
    app.security = Security(app, user_datastore)

    # Create DB and admin user
    with app.app_context():
        db.create_all()
        create_admin_user(app, user_datastore)

    return app, api, celery, cache


app, api, celery, cache = create_app()


@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    model = data.get("model")
    password = data.get("password")

    if not all([username, email, password]):
        return jsonify({"message": "Missing required fields"}), 400

    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({"message": "User already exists"}), 409

    hashed_pw = generate_password_hash(password)
    new_user = User(username=username, email=email, model=model, password=hashed_pw)

    # Attach 'user' role automatically if exists
    user_role = Role.query.filter_by(name='user').first()
    if user_role:
        new_user.roles.append(user_role)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201


@app.route("/check")
def is_run():
    return {"message": "Backend is running"}, 200


# ------------------------
# API Resource Routes
# ------------------------
from controllers.auth_api import *
api.add_resource(Index, "/api")
api.add_resource(LoginAPI, "/api/login")
api.add_resource(RegisterAPI, "/api/register")
api.add_resource(ProfileAPI, "/api/profile")

# ------------------------
# CRUD Routes
# ------------------------
from controllers.crud_api import *

# ---------- USER MANAGEMENT (Admin only) ----------
api.add_resource(UserListAPI, '/api/users')                     # GET all users / POST create user
api.add_resource(UserAPI, '/api/users/<int:user_id>')           # GET, PUT, DELETE user

# ---------- ROLE MANAGEMENT (Admin only) ----------
api.add_resource(RoleListAPI, '/api/roles')                     # GET all roles / POST create role
api.add_resource(RoleAPI, '/api/roles/<int:role_id>')           # GET, PUT, DELETE role

# ---------- PARKING LOT MANAGEMENT (Admin only) ----------
api.add_resource(ParkingLotListAPI, '/api/lots')                # GET all lots / POST create lot
api.add_resource(ParkingLotAPI, '/api/lots/<int:lot_id>')       # GET, PUT, DELETE lot

# ---------- PARKING SPOT MANAGEMENT (Admin + User) ----------
api.add_resource(ParkingSpotListAPI, '/api/spots')              # GET all spots / POST add spot (auto-generated)
api.add_resource(ParkingSpotAPI, '/api/spots/<int:spot_id>')    # GET, PUT, DELETE spot

# ---------- RESERVATION ACTIONS (User actions) ----------
api.add_resource(ReserveParkingAPI, '/api/reserve')             # POST reserve a spot
api.add_resource(ReleaseParkingAPI, '/api/release')             # POST release a spot
api.add_resource(ReserveHistoryAPI, '/api/reservations')        # GET user reservation history
api.add_resource(ReserveDetailAPI, '/api/reservations/<int:reservation_id>')  # GET specific reservation detail

# ---------- ADMIN DASHBOARD DATA ----------
api.add_resource(AdminSummaryChartAPI, '/api/admin/summary')    # GET admin summary data
api.add_resource(AdminParkingStatsAPI, '/api/admin/parkingstats') # GET lot/spot statistics

# ---------- USER DASHBOARD DATA ----------
api.add_resource(UserSummaryChartAPI, '/api/user/summary')      # GET user summary data
api.add_resource(UserParkingStatusAPI, '/api/user/status')      # GET current user spot/reservation status

# ---------- REPORTS & EXPORTS ----------
api.add_resource(ExportUserHistoryAPI, '/api/export/history')   # Async CSV export trigger
api.add_resource(MonthlyReportAPI, '/api/reports/monthly')      # Monthly auto-report endpoint (admin only)

if __name__ == "__main__":
    app.run(debug=True)
