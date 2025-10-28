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
                password=generate_password_hash('admin123'),  # hashed password
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
    api = Api(app, prefix="/api")
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

@app.route("/")
def is_run():
    return {
        "message": "Backend is running"
    }, 200

from controllers.auth_apis import *


api.add_resource(Index, "/")
api.add_resource(LoginAPI, "/login")
api.add_resource(RegisterAPI, "/resitration")
api.add_resource(ProfileAPI, "/profile")

from controllers.crud_apis import *
# User
api.add_resource(UserListAPI, '/api/users')
api.add_resource(UserAPI, '/api/users/<int:user_id>')

# Parking Lots
api.add_resource(ParkingLotListAPI, '/api/lots')
api.add_resource(ParkingLotAPI, '/api/lots/<int:lot_id>')

# Parking Spots
api.add_resource(ParkingSpotListAPI, '/api/spots')
api.add_resource(ParkingSpotAPI, '/api/spots/<int:spot_id>')

# Realese and occupied
api.add_resource(ReserveParkingAPI, '/api/reserve')
api.add_resource(ReleaseParkingAPI, '/api/release')

if __name__ == "__main__":

    app.run(debug=True)
