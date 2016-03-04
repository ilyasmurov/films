import tornado.ioloop
import tornado.web
import json
import time
from pprint import pprint
from datetime import datetime

from lib.app_mysql import DB
_db = {
    'user': 'root',
    'password': '***',
    'table': 'okko'
}

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Api v.0")

class getFilm(tornado.web.RequestHandler):
    def get(self, *args):
    
        db = DB(_db['table'], _db['user'], _db['password'])
    
        #for cross domain requests
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Content-Type', 'application/json')
        
        try:
            title = self.get_argument('title')
            year = self.get_argument('year')
            date_from = self.get_argument('date_from')
            date_to = self.get_argument('date_to') + ' 23:59:59'
        
            df = datetime.strptime(date_from, '%d-%m-%Y').strftime("%s")
            dt = datetime.strptime(date_to, '%d-%m-%Y %H:%M:%S').strftime("%s")
                
            if df > dt or int(year) > int(datetime.now().strftime('%Y')) or len(title) < 1:
                _json = {
                    'error': 'INVALID_FORMAT'
                }
            else:
            
                sql = """SELECT 
                            films.titleRu,
                            films.titleEn,
                            films.year,
                            films.description,
                            films.genre,
                            films.country,
                            films.kp_poster,
                            stats.kp_rating,
                            stats.vk_views,
                            unix_timestamp(stats.up)
                        FROM films 
                        RIGHT JOIN stats 
                        ON films.id = stats.film_id 
                        WHERE (films.titleRu like '%(title)s' or films.titleEn like '%(title)s') 
                            and films.year = %(year)s 
                            and (%(date_from)s <= unix_timestamp(stats.up) and %(date_to)s >= unix_timestamp(stats.up)) 
                        ORDER BY stats.up DESC 
                        LIMIT 1""" % {
                            'title': title,
                            'year': year,
                            'date_from': df,
                            'date_to': dt}  

                data_to = db.select(sql)
                
                sql = """SELECT 
                            stats.kp_rating,
                            stats.vk_views,
                            unix_timestamp(stats.up)
                        FROM films 
                        RIGHT JOIN stats 
                        ON films.id = stats.film_id 
                        WHERE (films.titleRu like '%(title)s' or films.titleEn like '%(title)s') 
                            and films.year = %(year)s 
                            and (%(date_from)s <= unix_timestamp(stats.up) and %(date_to)s >= unix_timestamp(stats.up)) 
                        ORDER BY stats.up ASC 
                        LIMIT 1""" % {
                            'title': title,
                            'year': year,
                            'date_from': df,
                            'date_to': dt}  

                data_from = db.select(sql)

                if data_to == False or data_from == False:
                    _json = {
                        'error': 'NOT_FOUND'
                    }
                else:
                    for row in data_from:
                        _json = {
                            'kp_rating_prev': row[0],
                            'vk_views_prev': row[1],
                        }
                    for row in data_to:
                        _json.update({
                            'titleRu': row[0],
                            'titleEn': row[1],
                            'year': row[2],
                            'description': row[3],
                            'genre': row[4],
                            'country': row[5],
                            'kp_poster': row[6],
                            'kp_rating': row[7],
                            'vk_views': row[8],
                            'up': row[9]})
                            
        except args:
            _json = {
                'error': 'MISSING_PARAMS'
            }

        self.write(json.dumps(_json, ensure_ascii=False).encode('utf8'))
        self.finish()
        
class getTop(tornado.web.RequestHandler):
    def get(self, *args):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Content-Type', 'application/json')
        
        db = DB(_db['table'], _db['user'], _db['password'])

        try:
            count = self.get_argument('count')
            date_from = self.get_argument('date_from')
            date_to = self.get_argument('date_to') + ' 23:59:59'
        
            df = datetime.strptime(date_from, '%d-%m-%Y').strftime("%s")
            dt = datetime.strptime(date_to, '%d-%m-%Y %H:%M:%S').strftime("%s")
            
            sql = """SELECT * FROM (
                        SELECT 
                            titleRu,
                            titleEn,
                            year,
                            description,
                            country,
                            genre,
                            kp_poster,
                            kp_rating,
                            vk_views,
                            unix_timestamp(up),
                            kp_id,
                            f.id
                        FROM films as f 
                        INNER JOIN stats as s
                        ON s.film_id=f.id 
                        WHERE %(date_from)s <= unix_timestamp(s.up) 
                            and %(date_to)s >= unix_timestamp(s.up) 
                        ORDER BY timestamp(up) DESC) 
                    t GROUP BY titleRu 
                    ORDER BY vk_views DESC, kp_rating DESC 
                    LIMIT %(count)s""" % {
                        'count': count,
                        'date_from': df,
                        'date_to': dt}

            data_to= db.select(sql)
            ids = []
            for row in data_to:
                ids.append(row[11])
            
            sql = """SELECT * FROM (
                        SELECT 
                            titleRu,
                            kp_rating,
                            vk_views,
                            unix_timestamp(up),
                            f.id
                        FROM films as f 
                        INNER JOIN stats as s
                        ON s.film_id=f.id 
                        WHERE %(date_from)s <= unix_timestamp(s.up) 
                            and %(date_to)s >= unix_timestamp(s.up) 
                            and f.id in (%(ids)s) 
                        ORDER BY timestamp(up)) 
                    t GROUP BY titleRu 
                    ORDER BY vk_views DESC, kp_rating DESC 
                    LIMIT %(count)s""" % {
                        'ids': ','.join(map(str,ids)),
                        'count': count,
                        'date_from': df,
                        'date_to': dt}

            data_from = db.select(sql)
                            
            if data_to == False or data_from == False:
                _json = {
                    'error': 'NOT_FOUND'
                }
            else:
                _json = []

                for row in data_to:
                    vk_view_prev = row[8]
                    kp_rating_prev = row[7]
                    for _row in data_from:
                        if _row[4] == row[11]:
                            vk_view_prev = _row[2]
                            kp_rating_prev = _row[1]
                            break
                    _json.append({
                        'titleRu': row[0],
                        'titleEn': row[1],
                        'year': row[2],
                        'description': row[3],
                        'genre': row[5],
                        'country': row[4],
                        'kp_poster': row[6],
                        'kp_rating': row[7],
                        'vk_views': row[8],
                        'up': row[9],
                        'kp_id': row[10],
                        'vk_views_prev': vk_view_prev,
                        'kp_rating_prev': kp_rating_prev})
                        
                vmax = 0
                for row in _json:
                    vc = row['vk_views'] - row['vk_views_prev']
                    if vmax < vc:
                        vmax = vc
                _json = {
                    'films': _json,
                    'normal': vmax / 2
                }
            
        except args:
            _json = {
                'error': 'MISSING_PARAMS'
            }
    
        self.write(json.dumps(_json, ensure_ascii=False).encode('utf8'))
        self.finish()
        
def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/api/getFilm", getFilm),
        (r"/api/getTop", getTop)
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
    db.close()