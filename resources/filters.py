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


no_city_consult = "SELECT * FROM hotels \
                WHERE (stars >= ? and stars <= ?) \
                and (price >= ? and price <= ?) \
                LIMIT ? OFFSET ?"


city_consult = "SELECT * FROM hotels \
                WHERE (stars >= ? and stars <= ?) \
                and (price >= ? and price <= ?) \
                and city = ? LIMIT ? OFFSET ?"