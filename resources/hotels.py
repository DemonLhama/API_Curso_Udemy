from db.site import SiteTable
from flask_restful import Resource, reqparse
from db.models import HotelTable
from flask_jwt_extended import jwt_required
from resources.filters import *
import sqlite3



path_params = reqparse.RequestParser()
path_params.add_argument("city", type=str)
path_params.add_argument("stars_min", type=float)
path_params.add_argument("stars_max", type=float)
path_params.add_argument("price_min", type=float)
path_params.add_argument("price_max", type=float)
path_params.add_argument("limit", type=float)   # quantity of items to show in the query
path_params.add_argument("offset", type=float)   # quantity of elements to jump



# In the GET resquest when the user apply a filter and don't specify the city, for example:
# data = {"stars_min": 4.0, "city": None}
# the result for city will be None, and that may cause a problem within the results.
# that's why valid_data will only show the keys that have a value != than None

class Hotels(Resource):
    def get(self):
        connection = sqlite3.connect("hotels.db")  
        cursor = connection.cursor()

        data = path_params.parse_args()
        valid_data = {key:data[key] for key in data if data[key] is not None}  
        params = normalize_path_params(**valid_data)

        if not params.get("city"):
            # in params the result is a dict, but a tuple is necessary
            # using list comprehension we can get the values for each key
            # in combine with tuple() the required tuple will be generated.

            tupla = tuple([params[keys] for keys in params])
            results = cursor.execute(no_city_consult, tupla)

        else:
            
            tupla = tuple([params[keys] for keys in params])
            results = cursor.execute(city_consult, tupla)

        hotels = []
        for line in results:
            hotels.append({
                "hotel_id": line[0],
                "name": line[1],
                "stars": line[2],
                "price": line[3],
                "city": line[4],
                "site_id": line[5]
            })

        return {"hotels": hotels}


class Hotel(Resource):
    arguments = reqparse.RequestParser()
    arguments.add_argument("name", type=str, required=True, help="This field cannot be left blank")
    arguments.add_argument("stars", type=float, required=True, help="This field cannot be left blank")
    arguments.add_argument("price")
    arguments.add_argument("city")
    arguments.add_argument("site_id", type=int, required=True, help="Every hotel must have a linked site")


    def get(self, hotel_id):
        hotel = HotelTable.find_hotel(hotel_id)
        if hotel:
            return hotel.json()
        return {"message": "Hotel not found."}, 404

    @jwt_required()   # will require token generated when login to do this request
    def post(self, hotel_id):
        if HotelTable.find_hotel(hotel_id):
            return {"message": "Hotel id '{}' already exists.".format(hotel_id)}, 400    # BAD REQUEST

        data = Hotel.arguments.parse_args()
        hotel = HotelTable(hotel_id, **data)

        if not SiteTable.find_by_id(data.get('site_id')):
            return {"message": "The hotel must be associated to a valid site id"}, 400

        try:
            hotel.save_hotel()
        except:
            return {"message": "An internal error has ocurred."}, 500    # INTERNAL SERVER ERROR 

        return hotel.json()


    @jwt_required()
    def put(self, hotel_id):
        data = Hotel.arguments.parse_args()
        hotel_result = HotelTable.find_hotel(hotel_id)

        if hotel_result:
            hotel_result.update_hotel(**data)
            hotel_result.save_hotel()
            return hotel_result.json(), 200

        hotel = HotelTable(hotel_id, **data)

        try:
            hotel.save_hotel()
        except:
            return {"message": "An internal error has ocurred."}, 500    # INTERNAL SERVER ERROR 

        return hotel.json(), 201 

    @jwt_required()
    def delete(self, hotel_id):
        hotel = HotelTable.find_hotel(hotel_id)
        if hotel:
            try:
                hotel.delete_hotel()
            except:
                return {"message": "An error has ocurred when trying to delete the hotel."}, 500  # INTERNAL SERVER ERROR
            return {"message": "Hotel deleted."}
        return {"message": "Hotel not found."}, 404
