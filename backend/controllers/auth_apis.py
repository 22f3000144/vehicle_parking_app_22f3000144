

from flask_restful import Resource

from flask import request, jsonify, make_response



class Index(Resource):
    def get(self):
        return {
            "message": "routes of API"
        }, 200


class LoginAPI(Resource):
    def post(self):
        login_verification = request.get_json()

        if not login_verification:
            result = {
                "message": "Verification Failed!!"
            }
            return make_response(jsonify(result), 400)
        
        email = login_verification.get('email', None)
        password = login_verification.get('password', None)

        if not email or not password:
            result = {
                "massage" : "Fill the Requirements"
            }
            return make_response(jsonify(result), 400)
        
        user = user_datastore.find_user(email=email)

        if not user:
            result = {
                "massage" : "User is not resitered"
            }
            return make_response(jsonify(result), 400) 

        if not utils.verify_password(password, user.password):
            result = {
                "massage" : "Invalid Password"
            }
            return make_response(jsonify(result), 401)

        auth_token = user.get_auth_token()

        utils.login_user(user)

        response = {
            "message": "Login Sussesfull.",
            "user_details" : {
                "email" : user.email,
                "model" : user.model,
                "roles" : [role.name for role in user.roles],
                "Authentication" : auth_token 
            }
        }                      

        return make_response(jsonify(response), 200)

class 