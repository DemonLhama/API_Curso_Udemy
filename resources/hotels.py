from flask_restful import Resource, reqparse
from db.models import HotelTable
from flask_jwt_extended import jwt_required
import sqlite3

# normalize_path_params will set a default search, so if the user try to search for hotels 
# the pre set search must show results within the most vast range.


def normalize_path_params(city=None,
                        stars_min = 0,
                        stars_max = 5,
                        price_min = 0,
                        price_max = 10000,
                        limit = 50,
                        offset = 0, **data):
    if city:
        return {
            "stars_min": stars_min,
            "stars_max": stars_max,
            "price_min": price_min,
            "price_max": price_max,
            "city": city,
            "limit": limit,
            "offset": offset
            }

    return {"stars_min": stars_min,
            "stars_max": stars_max,
            "price_min": price_min,
            "price_max": price_max,
            "limit": limit,
            "offset": offset
            }
    

# path /hotels?city=city&stars_min=4&price_max=500 => example of the querys that we want.

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
# 


class Hotels(Resource):
    def get(self):
        connection = sqlite3.connect("hotels.db")  
        cursor = connection.cursor()

        data = path_params.parse_args()
        valid_data = {key:data[key] for key in data if data[key] is not None}  
        params = normalize_path_params(**valid_data)

        if not params.get("city"):
            consult = "SELECT * FROM hotels \
                WHERE (stars > ? and stars < ?) \
                and (price > ? and price < ?) \
                LIMIT ? OFFSET ?"
            
            # in params the result is a dict, but a tuple is necessary
            # using list comprehension we can get the values for each key
            # in combine with tuple() the required tuple will be generated.

            tupla = tuple([params[keys] for keys in params])
            results = cursor.execute(consult, tupla)

        else:
            consult = "SELECT * FROM hotels \
                WHERE (stars > ? and stars < ?) \
                and (price > ? and price < ?) \
                and city = ? LIMIT ? OFFSET ?"
            
            tupla = tuple([params[keys] for keys in params])
            results = cursor.execute(consult, tupla)

        hotels = []
        for line in results:
            hotels.append({
                "hotel_id": line[0],
                "name": line[1],
                "stars": line[2],
                "price": line[3],
                "city": line[4]
            })

        return {"hotels": hotels}


class Hotel(Resource):
    arguments = reqparse.RequestParser()
    arguments.add_argument("name", type=str, required=True, help="This field cannot be left blank")
    arguments.add_argument("stars", type=float, required=True, help="This field cannot be left blank")
    arguments.add_argument("price")
    arguments.add_argument("city")


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
