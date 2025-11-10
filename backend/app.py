import os
from flask import Flask
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
                username='admin',
                email='admin@example.com',
                model='Admin Car',  # optional placeholder
                password='admin123',  # hashed password
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

    # Flask-Security setup
    user_datastore = SQLAlchemySessionUserDatastore(db.session, User, Role)
    app.security = Security(app, user_datastore)



    # Create DB and admin user
    with app.app_context():
        db.create_all()
        create_admin_user(app, user_datastore)

    return app, api, celery, cache

      
app, api, celery, cache = create_app()
CORS(app)

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    address = data.get('address')
    password = data.get('password')

    if not username or not password or not email:
        return jsonify({"message": "Missing required fields"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"message": "User already exists"}), 400

    hashed_pw = generate_password_hash(password)
    new_user = User(username=username, email=email, address=address, password=hashed_pw, role='user')
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully!"}), 201
    
@app.route("/check")
def is_run():
    return {
        "message": "Backend is running"
    }, 200

from controllers.auth_apis import *

api.add_resource(Index, "/")
api.add_resource(LoginAPI, "/api/login")
api.add_resource(RegisterAPI, "/api/register")
api.add_resource(ProfileAPI, "/api/profile")

# ------------------------
# CRUD Routes
# ------------------------
from controllers.crud_apis import *

# User Management (Admin only)
api.add_resource(UserListAPI, '/api/users')
api.add_resource(UserAPI, '/api/users/<int:user_id>')

# Parking Lots (Admin only)
api.add_resource(ParkingLotListAPI, '/api/lots')
api.add_resource(ParkingLotAPI, '/api/lots/<int:lot_id>')

# Parking Spots (Admin + Users)
api.add_resource(ParkingSpotListAPI, '/api/spots')
api.add_resource(ParkingSpotAPI, '/api/spots/<int:spot_id>')

# Reservation and Release (User actions)
api.add_resource(ReserveParkingAPI, '/api/reserve')
api.add_resource(ReleaseParkingAPI, '/api/release')

if __name__ == "__main__":
    app.run(debug=True)