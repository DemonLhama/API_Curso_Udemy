from sql_alchemy import db


class HotelTable(db.Model):
    __tablename__ = 'hotels'

    hotel_id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String(80))
    stars = db.Column(db.Float(precision=1))
    price = db.Column(db.Float(precision=2))
    city = db.Column(db.String(40))
    site_id = db.Column(db.Integer, db.ForeignKey("sites.site_id"))



    def __init__(self, hotel_id, name, stars, price, city, site_id):
        self.hotel_id = hotel_id
        self.name = name
        self.stars = stars
        self.price = price
        self.city = city
        self.site_id = site_id

    def json(self):
        return {
            "hotel_id": self.hotel_id,
            "name": self.name, 
            "stars": self.stars,
            "price": self.price,
            "city": self.city,
            "site_id": self.site_id
        }
    @classmethod
    def find_hotel(cls, hotel_id):
        hotel = cls.query.filter_by(hotel_id=hotel_id).first()
        if hotel:
            return hotel
        return None

    def save_hotel(self):
        db.session.add(self)
        db.session.commit()

    def update_hotel(self, name, stars, price, city):
        self.name = name
        self.stars = stars
        self.price = price
        self.city = city

    def delete_hotel(self):
        db.session.delete(self)
        db.session.commit()