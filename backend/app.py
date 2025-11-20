import os
from flask import Flask
from flask_restful import Api
from flask_security import Security, SQLAlchemyUserDatastore
from data.models import *
from controllers.settings import LocalDevelopmentConfig
from controllers.User_Datastore import user_datastore
from flask_jwt_extended import JWTManager
from flask_caching import Cache
from werkzeug.security import generate_password_hash
from flask_mail import Mail
from flask_cors import CORS
from celery import Celery

# Globals
app = None
api = None
celery = None
cache = None
mail = None



# Celery Initialization (Corrected)

def init_celery(flask_app):
    celery_app = Celery(
        flask_app.import_name,
        broker=flask_app.config["CELERY_BROKER_URL"],
        backend=flask_app.config["CELERY_RESULT_BACKEND"]
    )
    celery_app.conf.update(flask_app.config)

    class ContextTask(celery_app.Task):
        def __call__(self, *args, **kwargs):
            with flask_app.app_context():
                return super().__call__(*args, **kwargs)

    celery_app.Task = ContextTask
    return celery_app



# Admin Creation

import uuid


def create_admin_user(app, user_datastore):
    with app.app_context():

        admin_role = Role.query.filter_by(name='admin').first()
        if not admin_role:
            admin_role = Role(name='admin', description='Administrator role')
            db.session.add(admin_role)
            db.session.commit()

        # Use email to check if admin exists
        admin_user = User.query.filter_by(email='admin@gmail.com').first()

        if not admin_user:
            admin_user = User(
                username='admin',
                email='admin@gmail.com',
                model='System',
                password="admin123",
                fs_uniquifier=str(uuid.uuid4()),
                active=True
            )
            db.session.add(admin_user)
            db.session.commit()

        # Attach role safely
        if admin_role not in admin_user.roles:
            admin_user.roles.append(admin_role)
            db.session.commit() 


# Application Factory

def create_app():
    global celery, cache, mail

    app = Flask(__name__)
    app.config.from_object(LocalDevelopmentConfig)

    # Map config for Celery auto usage
    app.config["broker_url"] = app.config["CELERY_BROKER_URL"]
    app.config["result_backend"] = app.config["CELERY_RESULT_BACKEND"]

    # Init extensions
    db.init_app(app)
    security = Security(app, user_datastore)
    api = Api(app)
    jwt = JWTManager(app)
    cache = Cache(app)
    mail = Mail(app)

    # CORS for Vue Frontend
    CORS(app, resources={
        r"/*": {
            "origins": [
                "http://localhost:5173",
                "http://127.0.0.1:5173"
            ],
            "supports_credentials": True
        }
    })


    # Celery
    celery = init_celery(app)

    # DB initialization + admin creation
    with app.app_context():
        db.create_all()
        create_admin_user(app, user_datastore)

    return app, api, celery, cache, mail


# Call Factory
app, api, celery, cache, mail = create_app()



# Importing routes AFTER app is created


from controllers.auth_apis import *
from controllers.crud_apis import *

@app.route("/check")
def is_run():
    return "Backend is Running"

# Registering API Routes

# Authentication
api.add_resource(Index, "/api")
api.add_resource(LoginAPI, "/api/login")
api.add_resource(RegisterAPI, "/api/register")
api.add_resource(ProfileAPI, "/api/profile")


# User CRUD
api.add_resource(UserListAPI, '/api/users')
api.add_resource(UserAPI, '/api/users/<int:user_id>')


# Parking Lot CRUD (combined)
api.add_resource(ParkingLotAPI, '/api/lots', '/api/lots/<int:lot_id>')

# Parking Spot CRUD (combined)
api.add_resource(ParkingSpotAPI, '/api/spots', '/api/spots/<int:spot_id>')

# Reservation actions & history & detail
api.add_resource(ReserveParkingAPI, '/api/reserve')
api.add_resource(ReleaseParkingAPI, '/api/release')
api.add_resource(ReserveHistoryAPI, '/api/reservations')
api.add_resource(ReserveDetailAPI, '/api/reservations/<int:reservation_id>')

# Admin analytics
api.add_resource(AdminSummaryChartAPI, '/api/admin/summary')
api.add_resource(AdminParkingStatsAPI, '/api/admin/parkingstats')

# User analytics
api.add_resource(UserSummaryChartAPI, '/api/user/summary')
api.add_resource(UserParkingStatusAPI, '/api/user/status')

# Async CSV Export
api.add_resource(ExportHistoryAPI, '/api/export/history')
api.add_resource(ExportStatusAPI, '/api/export/status')

# MAIN

if __name__ == "__main__":
    app.run(debug=True)
