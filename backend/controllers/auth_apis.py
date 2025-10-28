# routes/auth_apis.py
from flask_restful import Resource
from flask import request, jsonify, make_response
from flask_security import utils, login_user, auth_token_required
from data.models import db


class Index(Resource):
    def get(self):
        return {"message": "Authentication API is active"}, 200


class RegisterAPI(Resource):
    def post(self):
        user_data = request.get_json()

        if not user_data:
            return make_response(jsonify({"message": "Credentials required."}), 400)

        username = user_data.get('username')
        email = user_data.get('email')
        model = user_data.get('model')
        password = user_data.get('password')

        # Check all required fields
        if not username or not email or not password:
            return make_response(jsonify({"message": "All fields are required."}), 400)

        # Check if already exists
        if user_datastore.find_user(email=email):
            return make_response(jsonify({"message": "User already registered. Please login."}), 409)

        # Assign default role
        user_role = user_datastore.find_role('user')
        if not user_role:
            user_role = user_datastore.create_role(name='user', description='Regular User')

        # Create and save new user
        new_user = user_datastore.create_user(
            username=username,
            email=email,
            model=model,
            password=utils.hash_password(password),
            roles=[user_role]
        )

        db.session.commit()

        return make_response(jsonify({
            "message": "User registered successfully.",
            "user": {"username": username, "email": email}
        }), 201)


class LoginAPI(Resource):
    def post(self):
        login_data = request.get_json()

        if not login_data:
            return make_response(jsonify({"message": "Verification failed!"}), 400)

        email = login_data.get('email')
        password = login_data.get('password')

        if not email or not password:
            return make_response(jsonify({"message": "Email and password required."}), 400)

        user = user_datastore.find_user(email=email)
        if not user:
            return make_response(jsonify({"message": "User not registered."}), 404)

        if not utils.verify_password(password, user.password):
            return make_response(jsonify({"message": "Invalid password."}), 401)

        # Generate authentication token
        auth_token = user.get_auth_token()
        login_user(user)

        response = {
            "message": "Login successful.",
            "user_details": {
                "email": user.email,
                "username": user.username,
                "model": user.model,
                "roles": [role.name for role in user.roles],
                "auth_token": auth_token
            }
        }

        return make_response(jsonify(response), 200)


class ProfileAPI(Resource):
    @auth_token_required
    def get(self):
        from flask_security import current_user
        if not current_user.is_authenticated:
            return make_response(jsonify({"message": "Invalid or expired token."}), 401)

        return make_response(jsonify({
            "username": current_user.username,
            "email": current_user.email,
            "model": current_user.model,
            "roles": [role.name for role in current_user.roles]
        }), 200)
