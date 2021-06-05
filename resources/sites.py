from flask_restful import Resource
from db.site import SiteTable

class Sites(Resource):
    def get(self):
        # return a list of objects site_id, url and hotels (def json in db/site.py)
        return {"sites": [site.json() for site in SiteTable.query.all()]}

class Site(Resource):
    def get(self, url):
        site = SiteTable.find_site(url)
        if site:
            return site.json()
        return {"message": "Site not found"}, 404  # NOT FOUND

    def post(self, url):
        if SiteTable.find_site(url):
            return {"message": "The site {} already exists".format(url)}, 400 # BAD REQUEST
        site = SiteTable(url)
        try:
            site.save_site()
        except:
            return {"message": "An internal error has ocurred"}, 500
        
        return site.json()


    def delete(self, url):
        site = SiteTable.find_site(url)
        if site:
            site.delete_site()
            return {"message": "Site deleted"}
        return {"message": "Site not found"}, 404