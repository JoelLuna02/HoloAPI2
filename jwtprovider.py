from flask_jwt_extended import JWTManager
from flask import jsonify

def jwtProviders(jwt: JWTManager):
    # JWT Extended errorhandlers
    @jwt.unauthorized_loader
    def unauthorized(err):
        response = {
            "code": 401,
            "error": "Unauthorized",
            "message": "You must be logged in to access this resource"
        }
        return jsonify(response), 401

    @jwt.invalid_token_loader
    def invalid_token(err):
        response = {
            "code": 401,
            "error": "Unauthorized",
            "message": "Invalid token. Please check and try again."
        }
        return jsonify(response), 401

    @jwt.expired_token_loader
    def expired_token(err):
        response = {
            "code": 401,
            "error": "Unauthorized",
            "message": "The token has expired. Please try again later"
        }
        return jsonify(response), 401

    @jwt.needs_fresh_token_loader
    def needsfresh(err):
        response = {
            "code": 401,
            "error": "Unauthorized",
            "message": "Invalid signature. Please try again later"
        }
        return jsonify(response), 401