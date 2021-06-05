from sql_alchemy import db


class SiteTable(db.Model):
    __tablename__ = 'sites'

    site_id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(80))
    hotels = db.relationship("HotelTable")   # list of objects hotels


    def __init__(self, url):
        self.url = url

    def json(self):
        return {
            "site_id": self.site_id,
            "url": self.url,
            "hotels": [hotels.json() for hotels in self.hotels] 
        }
    @classmethod
    def find_site(cls, url):
        site = cls.query.filter_by(url=url).first()
        if site:
            return site
        return None


    @classmethod
    def find_by_id(cls, site_id):
        site = cls.query.filter_by(site_id=site_id).first()
        if site:
            return site
        return None


    def save_site(self):
        db.session.add(self)
        db.session.commit()


    def delete_site(self):
        # deleting all hotels associeted to a site
        [hotel.delete_hotel() for hotel in self.hotels]
        db.session.delete(self)
        db.session.commit()