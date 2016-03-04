import vk_auth
import vkontakte
import json
import codecs
from pprint import pprint
import time
from urllib2 import Request, urlopen

from lib.app_mysql import DB
from lib.app_films import FM

_vk = {
    login: 'vk_login',
    password: 'vk_password',
    key: 'vk_app_key'
}
_db = {
    'user': 'root',
    'password': '***',
    'table': 'okko'
}

# vk results count of each film
count = 5

# kinopoisk api            
class KP:
    def get(self, film):
        request = Request('http://api.kinopoisk.cf/searchFilms?keyword=' + film)
        response_body = urlopen(request).read()
        data = json.loads(response_body.decode('utf-8-sig'))
        return data['searchFilms'][0]
        
# VK api
class VK:
    def get(self, film):
        (token,user_id) = vk_auth.auth(
            _vk['login'],
            _vk['password'],
            _vk['key'],
            'video,offline')
        vk = vkontakte.API(token=token)
        
        data = vk.get(
            'video.search',
            q=film,
            count=count,
            filters='long',
            extended=1,
            v=5.45);
            
        return data['items']
        
db = DB(_db['table'], _db['user'], _db['password'])
films = FM(db)
kinopoisk = KP()
vk = VK()     

def main():

    # films list json
    data = json.loads(open('data.json').read().decode('utf-8-sig'))
    
    titles = {}
    up = time.strftime('%Y-%m-%d %H:%M:%S')
    
    for index, film in enumerate(data['films']):
        
        id = None
        year = data['films'][index]['year']
        
        views_tmp = []
        film_views = {0: 0, 1: 0}
        
        for title_index, lang in enumerate(data['films'][index]['title']):

            titles[lang] = film['title'][lang] + ' ' + year
            
            # VK
            result = vk.get(titles[lang])
            for result_index in range(count):
            
                    flag = True
                    
                    # if results < 5 then break
                    try:
                
                        # check same id from film titles
                        if title_index > 0:
                            for prev_index, prev_film in enumerate(views_tmp):
                                if result[result_index]['id'] == prev_film['id']:
                                    flag = False
                                    break

                            # add views if id not exist
                            if flag:
                                film_views[1] += result[result_index]['id']
                            
                            views_tmp = []

                        views_tmp.append({
                            'id': result[result_index]['id']
                        })
                        film_views[0] += result[result_index]['views']
                        
                    except IndexError:
                        break
                        
        # KINOPOISK
        kp_data = kinopoisk.get(
            data['films'][index]['title']['ru'].replace(' ',',').encode('utf-8')
                +','
                +data['films'][index]['title']['en'].replace(' ',',').encode('utf-8'))
        if 'rating' in kp_data:
            kp_rating = kp_data['rating'].split(' ') 
            kp_rating = kp_rating[0]
        else:
            kp_rating = 0
            
        data['films'][index].update({
            'description': kp_data['description'],
            'country': kp_data['country'],
            'genre': kp_data['genre'],
            'kp_rating': kp_rating,
            'kp_id': kp_data['id'],
            'kp_poster': kp_data['posterURL']
        })
 
        id = films.getId(
            data['films'][index]['title']['ru'],
            data['films'][index]['title']['en'],
            data['films'][index]['year'])
            
        if id == False:
            id = films.add(data['films'][index])
            
        films.updateStat(
            id,
            film_views[0] + film_views[1],
            data['films'][index]['kp_rating'],
            up)
        
        #time.sleep(1)
    
    return 0
 
if __name__ == '__main__':
    main()
    db.close()
