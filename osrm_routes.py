import requests
from urllib import request
from urllib.parse import urlparse,parse_qs


class osrm_routes():
    def main(self):
        points = ''
        #self.request = 'http://router.project-osrm.org/route/v1/driving/'+points+'?overview=false' #13.388860,52.517037;13.397634,52.529407;13.428555,52.523219
    def get_distante(points):
        url = 'http://router.project-osrm.org/route/v1/driving/' + points + '?overview=false'
        #responce = request.urlopen(url).read()
        responce = requests.get(url)
        data = responce.json()
        return data['routes'][0]['distance']



