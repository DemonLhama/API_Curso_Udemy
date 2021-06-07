from flask_jwt_extended.view_decorators import jwt_required
from flask_restful import Resource, reqparse
from flask_jwt_extended import create_access_token, jwt_required, get_jwt
from werkzeug.security import safe_str_cmp
from db.user_model import UserTable
from blacklist import BLACKLIST


attributes = reqparse.RequestParser()
attributes.add_argument("login", type=str, required=True, help="This field cannot be left blank.")
attributes.add_argument("password", type=str, required=True, help="This field cannot be left blank.")
attributes.add_argument("activated", type=bool)



class User(Resource):
    def get(self, user_id):
        user = UserTable.find_user(user_id)
        if user:
            return user.json()
        return {"message": "User not found."}, 404


    @jwt_required()
    def delete(self, user_id):
        user = UserTable.find_user(user_id)
        if user:
            try:
                user.delete_user()
            except:
                return {"message": "An error has ocurred when trying to delete the user."}, 500  # INTERNAL SERVER ERROR
            return {"message": "User deleted."}
        return {"message": "User not found."}, 404


class UserRegister(Resource):
    def post(self):
        data = attributes.parse_args()

        if UserTable.find_by_login(data['login']):
            return {"message": "The login '{}' already exists.".format(data['login'])}

        user = UserTable(**data)
        user.activated = False
        user.save_user()
        return {"message": "User sucesfully created"}, 201  # CREATED


class UserLogin(Resource):

    # When the user make the login the token will be generated, so with that the @jwtrequired will allow 
    # the user to make the changes.
    # DONT FORGET TO COPY THE TOKEN GENERATED WHEN U GONNA MAKE REQUIRES IN POSTMAN!!


    @classmethod
    def post(cls):
        data = attributes.parse_args()

        user = UserTable.find_by_login(data["login"])

        if user and safe_str_cmp(user.password, data["password"]):
            if user.activated:
                token = create_access_token(identity=user.user_id)
                return {"access_token": token}, 200
            return {"message": "User not confirmed"}, 400
        return {"message": "The username or password incorrect."}, 401  #UNAUTHORIZED


class UserLogout(Resource):

    @jwt_required()
    def post(self):
        jwt_id = get_jwt()['jti']  # JWT Token Identifier
        BLACKLIST.add(jwt_id)
        return {"message": "Logged out successfully."}, 200


class UserConfirm(Resource):
    # /confirmation/{user_id}
    @classmethod
    def get(cls, user_id):
        user = UserTable.find_user(user_id)

        if not user:
            return {"message": "User id '{}' not found.".format(user_id)}

        user.activated = True
        user.save_user()
        return {"message": "User id '{}' confirmed successfully".format(user_id)}, 200


