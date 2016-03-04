class FM:
    db = None

    def __init__(self, db):
        self.db = db

    def add(self, data):
        sql = """INSERT INTO films(
                    titleRu, 
                    titleEn, 
                    year, 
                    description, 
                    country, 
                    genre, 
                    kp_id, 
                    kp_poster)
                VALUES (
                    '%(titleRu)s',
                    '%(titleEn)s',
                    '%(year)s',
                    '%(description)s',
                    '%(country)s',
                    '%(genre)s',
                    '%(kp_id)s',
                    '%(kp_poster)s')
                """ % {
                    'titleRu': data['title']['ru'],
                    'titleEn': data['title']['en'],
                    'year': data['year'],
                    'description': data['description'],
                    'country': data['country'],
                    'genre': data['genre'],
                    'kp_id': data['kp_id'],
                    'kp_poster': data['kp_poster']}
        id = self.db.insert(sql)
        return id
        
    def updateStat(self, film_id, vk_views, kp_rating, up):
        sql = """INSERT INTO stats(film_id, vk_views, kp_rating, up)
                VALUES (
                    '%(film_id)s',
                    '%(vk_views)s',
                    '%(kp_rating)s',
                    '%(up)s')
                """ % {
                    'film_id': film_id,
                    'vk_views': vk_views,
                    'kp_rating': kp_rating,
                    'up': up}
        self.db.insert(sql)
        
    def getId(self, titleRu, titleEn, year):
        sql = """SELECT id, titleRu, titleEn, year FROM films 
                WHERE (titleRu = '%(titleRu)s' or titleEn = '%(titleRu)s') 
                    and year = '%(year)s'
                """ % {
                    'titleRu': titleRu,
                    'titleEn': titleEn,
                    'year': year}
        data = self.db.select(sql)
        if data == False:
            return data
        else:
            for rec in data:
                (id, titleRu, titleEn, year) = rec
                return id