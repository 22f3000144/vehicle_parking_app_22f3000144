# routes/auth_apis.py
from flask_restful import Resource
from flask import request, jsonify, make_response, current_app
from flask_security import utils
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from data.models import db, User, Role

def get_datastore():
    return current_app.security.datastore


class Index(Resource):
    def get(self):
        return {"message": "Authentication API is active"}, 200


class RegisterAPI(Resource):
    def post(self):
        data = request.get_json()
        if not data:
            return {"message": "Credentials required."}, 400

        username = data.get("username")
        email = data.get("email")
        model = data.get("model")
        password = data.get("password")

        if not username or not email or not password:
            return {"message": "All fields are required."}, 400

        datastore = get_datastore()
        if datastore.find_user(email=email):
            return {"message": "User already registered."}, 409

        # Ensure 'user' role exists
        role = datastore.find_role("user")
        if not role:
            role = datastore.create_role(name="user", description="Regular User")
            db.session.commit()

        # Create user (must set active=True for Flask-Security)
        user = datastore.create_user(
            username=username,
            email=email,
            model=model,
            password=password,
            roles=[role],
            active=True,
        )
        db.session.commit()

        return {"message": "User registered successfully."}, 201


class LoginAPI(Resource):
    def post(self):
        data = request.get_json()
        if not data:
            return {"message": "Invalid input."}, 400

        email = data.get("email")
        password = data.get("password")

        datastore = get_datastore()
        user = datastore.find_user(email=email)

        if not user or not utils.verify_password(password, user.password):
            return {"message": "Invalid credentials."}, 401

        token = create_access_token(identity=user.id)
        role = user.roles[0].name if user.roles else "user"

        return {
            "message": "Login successful.",
            "access_token": token,
            "role": role,
            "username": user.username,
            "email": user.email
        }, 200


class ProfileAPI(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return {"message": "User not found"}, 404

        return {
            "username": user.username,
            "email": user.email,
            "model": user.model,
            "roles": [r.name for r in user.roles]
        }, 200
