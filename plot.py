import folium
import re
import psycopg2 as psql
import psycopg2.extras as ex
import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon
import string
import pygeoj as pgj
from geographiclib.geodesic import Geodesic
from shapely.geometry import Point, Polygon
import matplotlib.pyplot as plt
import numpy as np
from threading import Thread

# x = np.zeros(5)
# y = np.zeros(5)
# class RequesterThread(Thread):
#     def __init__(self, data, size,index,range):
#         #Инициализация потока
#         Thread.__init__(self)
#         self.data = data
#         self.size = size
#         self.index = index
#         self.range = range
#
#     def run(self):
#         print(Thread.getName(self), "start")
#         #Запуск потока
#         length = self.data.__len__()
#         max = self.index+self.range
#         if self.index+self.range > length*length:
#             max = length*length
#         i = int(self.index/length)
#         j = self.index - length*i

class Plot():

    def road_lenght(self,coords):
        # p2 = [82.7511322, 54.7996311993747], [82.7511322, 55.13473551670991], [83.16091036697941, 55.13473551670991], [83.16091036697941, 54.7996311993747], [82.7511322, 54.7996311993747]
        p2 = [coords[0],coords[1],coords[2],coords[3],coords[0]]
        p_t = str(p2)
        p_t = p_t.replace(",", "")
        p_t = p_t.replace("]", ",")
        p_t = p_t.replace("[", "")
        p_t = p_t.replace("(", "")
        p_t = p_t.replace(")", "")
        p_t = p_t[0:len(p_t) - 2]
        # print(p_t)
        db = psql.connect(dbname='postgis_db', user='postgis_db', password='postgis_db', host='localhost')
        curr = db.cursor()
        name = 'Новосибирск'
        # request = "SELECT way_area FROM planet_osm_polygon WHERE name = '" + name + "'"
        # request = "SELECT st_astext(st_transform(way, 4326)),name FROM planet_osm_polygon WHERE name= '" + name + "'" координаты границ города
        request = "SELECT st_transform(way, 4326) as POLYGON ,name FROM planet_osm_polygon WHERE name= '" + name + "'"
        # r = "SELECT osm_id, name, ST_AsText(ST_Transform(way,4326)) FROM planet_osm_roads WHERE ST_Intersects(ST_GeomFromText('POLYGON(("+p_t+"))',4326), ST_Transform(way,4326));"
        r = "SELECT SUM(ST_LENGTH(ST_Intersection(ST_GeomFromText('POLYGON((" + p_t + "))',4326), ST_GeomFromText(ST_AsText(ST_Transform(way,4326)),4326)))) FROM planet_osm_line WHERE ST_Intersects(ST_GeomFromText('POLYGON((" + p_t + "))',4326), ST_GeomFromText(ST_AsText(ST_Transform(way,4326)),4326))"
        curr.execute(r)
        r = curr.fetchall()
        if str(r[0][0]) == 'None':
            return 0
        # =print(r[0][0])
        # for item in r:
        #     print(item)
        return r[0][0]

    # def calc_length(self):
    #     length = data.__len__()
    #     # length = 14518
    #     global adj_matrix
    #     adj_matrix = np.zeros((length, length))

    def roadlgt_eval(self,data):
        output_file = open('./data/plot.txt', 'w+')
        x = []
        y = []
        print(len(data))
        for i in range(0,len(data)):
            coords = data.get_feature(i).geometry.coordinates[0]
            l = self.road_lenght(coords)
            # l = 5
            p = str(data.get_feature(i).properties['prestige'])
            p = p[len(p)-2:len(p)]
            s = str(l) + '\t' + str(p) + '\n'
            x.append(l)
            y.append(int(p))
            print(str(i)+" "+s)
            output_file.write(s)

        return x,y

    def plot_data(self,x,y):
        # plt.plot(x, y, label='linear')
        plt.scatter(x,y)
        plt.savefig("foo.png")

    def draw_city_grid(self, data):
        for gj in data.__dict__['_data']['features']:

            s = str(gj['properties']['prestige'])
            print(s[len(s) - 2:len(s)])

    def readPlotData(self):
        x = []
        y = []
        input_file = open("./data/plot_rms.txt", "r+")
        for rec in input_file:
            s = re.split('\t', rec)
            x.append(float(str.strip(s[0])))
            y.append(float(str.strip(s[1])))
        return x, y

    def main(self):
        # self.city_grid_l = pgj.load(filepath="./data/city_grid.geojson")
        # self.draw_city_grid(self.city_grid_l)
        try:
            # x, y = self.roadlgt_eval(self.city_grid_l)
            x, y = self.readPlotData()
            self.plot_data(x, y)
        except  Exception:
            print(Exception)

if __name__ == '__main__':
    app = Plot()
    app.main()