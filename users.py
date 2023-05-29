from flask import request
from werkzeug.exceptions import Forbidden, Unauthorized
from flask_restful import Api, Resource
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from models import *
from schema import *

userapi = Api()

user_schema = UserSchema()

class GetUsers(Resource):
    @jwt_required()
    def get(self):
        userid = get_jwt_identity()
        user = db.session.get(User, userid)
        if user and not user.is_admin:
            raise Forbidden("You need administrative privileges to access this resource")
        users = User.query.all()
        response = user_schema.dump(users, many=True)
        return response, 201

class Register(Resource):
    def post(self):
        data = request.get_json()
        user = User(
            firstname=data.get("firstname"), lastname=data.get("lastname"), birthday=data.get("birthday"),
            username=data.get("username"), email=data.get("email"), password=data.get("password")
        )
        user.is_admin = data.get('is_admin', False)
        db.session.add(user)
        db.session.commit()
        response = {
            "crated_user": user_schema.dump(user),
            "message": "Successfully registered user",
            "status": "201 Created"
        }
        return response, 201

class Login(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.decrypt(password):
            access_token = create_access_token(identity=user.id)
            response = {
                "logged_as": user_schema.dump(user),
                "access_token": str(access_token)
            }
            return response, 200
        else:
            raise Unauthorized("Invalid access or Bad credentials, please check and try again")

userapi.add_resource(GetUsers, '/v1/auth/users')
userapi.add_resource(Register, '/v1/auth/signup')
userapi.add_resource(Login, '/v1/auth/login')