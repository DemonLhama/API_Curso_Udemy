from blacklist import BLACKLIST
from resources.user import User, UserLogin
from flask import Flask, jsonify
from flask_restful import Api
from sql_alchemy import db
from resources.hotels import Hotels, Hotel
from resources.user import User, UserRegister, UserLogin, UserLogout
from flask_jwt_extended import JWTManager


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hotels.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = "Somethinghard"
app.config['JWT_BLACKLIST_ENABLE'] = True
api = Api(app)
jwt = JWTManager(app)


@app.before_first_request
def create_db():
    db.create_all()

@jwt.token_in_blocklist_loader
def blacklist_verification(self,token):
    return token["jti"] in BLACKLIST

@jwt.revoked_token_loader
def access_token_invalid(jwt_header, jwt_loader):
    return jsonify({"message": "You have been logged out."}), 401  # UNAUTHORIZED


api.add_resource(Hotels, '/hotels')

api.add_resource(Hotel, '/hotels/<string:hotel_id>')

api.add_resource(User, '/users/<int:user_id>')

api.add_resource(UserRegister, '/registrate')

api.add_resource(UserLogin, '/login')

api.add_resource(UserLogout, '/logout')


db.init_app(app)
