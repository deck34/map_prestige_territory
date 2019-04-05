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
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np
import time
from threading import Thread
from collections import Counter
from collections import OrderedDict

x = np.zeros(5)
y = np.zeros(5)
class RequesterThread(Thread):
    def __init__(self, data,index,range):
        #Инициализация потока
        Thread.__init__(self)
        self.data = data
        self.index = index
        self.range = range

    def run(self):
        print(Thread.getName(self), "start")
        #Запуск потока
        length = self.data.__len__()
        max = self.index+self.range
        if self.index+self.range > length:
            max = length
        # i = int(self.index/length)
        # j = self.index - length*i

        for i in range(self.index,max):
            coords = self.data.get_feature(i).geometry.coordinates[0]
            l = Plot.road_lenght(self,coords)
            # l=5
            p = str(self.data.get_feature(i).properties['prestige'])
            p = p[len(p)-2:len(p)]
            s = str(l) + '\t' + str(p) + '\n'
            x[i] = l # x.append(l)
            y[i] = int(p) # y.append(int(p))
            # print(Thread.getName(self) + " " + str(i) + "  " + s)
            # output_file.write(s)

class Plot():

    def __init__(self):
        self.threads = 100

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

    def calc_length_parallel(self,data):
        # output_file = open('./data/plot.txt', 'w+')
        length = len(data)
        # length = 14518
        global x
        global y
        x = np.zeros(length)
        y = np.zeros(length)

        threads = []
        x.shape = (length)
        y.shape = (length)

        step = round((length / self.threads))
        for i in range(0, length, step):
            thread = RequesterThread(data, i, step)
            thread.setDaemon(True)
            threads.append(thread)
            thread.start()

        for t in threads:
            t.join()

        return x, y
        # adj_matrix.shape = (length, length)

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

    def readPlotData1(self,name,data):
        x = []
        y = []
        input_file = open(name, "r+")
        i=0
        for rec in input_file:
            s = re.split('\t', rec)
            x.append(float(str.strip(s[0])))
            # y.append(float(str.strip(s[1])))
            y.append((100-(int(data.get_feature(i).properties['prestige']))*2))
            i+=1

        return x, y

    def xy_tofile(self,x,y):
        output_file = open('./data/plot.txt', 'w+')
        for i in range(0,len(x)):
            s = str(x[i]) + '\t' + str(y[i]) + '\n'
            output_file.write(s)

    def plot_hist(self):
        self.city_grid_rms = pgj.load(filepath="./data/city_grid_rms_grad50_2.geojson")
        self.city_grid_mean = pgj.load(filepath="./data/city_grid_mean_grad50_2.geojson")
        self.city_grid_median = pgj.load(filepath="./data/city_grid_median_grad50_2.geojson")
        self.city_grid_gmean = pgj.load(filepath="./data/city_grid_gmean_grad50_2.geojson")
        x1, y1 = self.readPlotData1("./data/plot_rms.txt", self.city_grid_rms)
        x2, y2 = self.readPlotData1("./data/plot_mean.txt", self.city_grid_mean)
        x3, y3 = self.readPlotData1("./data/plot_median.txt", self.city_grid_median)
        x4, y4 = self.readPlotData1("./data/plot_median.txt", self.city_grid_gmean)

        plt.hist((y1,y2,y3,y4), label=('rms', 'mean', 'median', 'gmean'), color=('b', 'g', 'r', 'y'))
        plt.xlabel('Аssessment')
        plt.ylabel('Road length')
        plt.title('Compare')
        plt.legend()
        # xi = [i for i in range(min(min(y1),min(y2),min(y3)), max(max(y1),max(y2),max(y3)),5)]
        # xi = [i for i in range(30, 80, 5)]
        # plt.xticks(xi)
        # plt.xlim(min(min(y1),min(y2),min(y3))-5, max(max(y1),max(y2),max(y3))+5)
        plt.show()

    def plot_bar(self):
        self.city_grid_rms = pgj.load(filepath="./data/city_grid_rms_grad50_2.geojson")
        self.city_grid_mean = pgj.load(filepath="./data/city_grid_mean_grad50_2.geojson")
        self.city_grid_median = pgj.load(filepath="./data/city_grid_median_grad50_2.geojson")
        self.city_grid_gmean = pgj.load(filepath="./data/city_grid_gmean_grad50_2.geojson")
        x1, y1 = self.readPlotData1("./data/plot_rms.txt", self.city_grid_rms)
        x2, y2 = self.readPlotData1("./data/plot_mean.txt", self.city_grid_mean)
        x3, y3 = self.readPlotData1("./data/plot_median.txt", self.city_grid_median)
        x4, y4 = self.readPlotData1("./data/plot_median.txt", self.city_grid_gmean)

        # plt.hist((y1,y2,y3), label=('rms', 'mean', 'median'))
        n_groups = max(len(y1), len(y2), len(y3), len(y3))
        fig, ax = plt.subplots()
        index = np.arange(n_groups)
        bar_width = 0.2
        opacity = 0.8
        b1 = ax.bar(np.arange(len(x1)), x1, bar_width, alpha=opacity, color='b', label=('rms'))
        b2 = ax.bar(np.arange(len(x2)) + bar_width, x2, bar_width, alpha=opacity, color='g', label=('mean'))
        b3 = ax.bar(np.arange(len(x3)) + bar_width * 2, x3, bar_width, alpha=opacity, color='r', label=('median'))
        b4 = ax.bar(np.arange(len(x4)) + bar_width * 3, x4, bar_width, alpha=opacity, color='y', label=('gmean'))
        plt.xlabel('Аssessment')
        plt.ylabel('Road length')
        plt.title('Compare')
        plt.legend()
        plt.tight_layout()
        # plt.xticks(index + bar_width, y3)
        plt.show()

    def plot_bar1(self):
        self.city_grid_rms = pgj.load(filepath="./data/city_grid_rms_grad50_2.geojson")
        self.city_grid_mean = pgj.load(filepath="./data/city_grid_mean_grad50_2.geojson")
        self.city_grid_median = pgj.load(filepath="./data/city_grid_median_grad50_2.geojson")
        self.city_grid_gmean = pgj.load(filepath="./data/city_grid_gmean_grad50_2.geojson")
        x1, y1 = self.readPlotData1("./data/plot_rms.txt", self.city_grid_rms)
        x2, y2 = self.readPlotData1("./data/plot_mean.txt", self.city_grid_mean)
        x3, y3 = self.readPlotData1("./data/plot_median.txt", self.city_grid_median)
        x4, y4 = self.readPlotData1("./data/plot_median.txt", self.city_grid_gmean)

        count_y1 = OrderedDict(sorted(Counter(y1).items()))
        count_y2 = OrderedDict(sorted(Counter(y2).items()))
        count_y3 = OrderedDict(sorted(Counter(y3).items()))
        count_y4 = OrderedDict(sorted(Counter(y4).items()))

        y1_data = np.fromiter(count_y1.keys(), dtype=float)
        y2_data = np.fromiter(count_y2.keys(), dtype=float)
        y4_data = np.fromiter(count_y4.keys(), dtype=float)
        y3_data = np.fromiter(count_y3.keys(), dtype=float)
        x1_data = np.fromiter(count_y1.values(), dtype=float)
        x2_data = np.fromiter(count_y2.values(), dtype=float)
        x3_data = np.fromiter(count_y3.values(), dtype=float)
        x4_data = np.fromiter(count_y4.values(), dtype=float)
        # for i in range(0,len(count_y1)):
        #     a=count_y1.get(i)
        #     b=0
        # n_groups = 3
        # index = np.arange(n_groups)
        # bar_width = 0.35
        n_groups = max(len(y1_data),len(y2_data),len(y3_data),len(y4_data))
        fig, ax = plt.subplots()
        index = np.arange(n_groups)
        bar_width = 0.2
        opacity = 0.8
        b1 = ax.bar(np.arange(len(x1_data)), x1_data, bar_width, alpha=opacity, color='b', label=('rms'))
        b2 = ax.bar(np.arange(len(x2_data)) + bar_width, x2_data, bar_width, alpha=opacity, color='g', label=('mean'))
        b3 = ax.bar(np.arange(len(x3_data)) + bar_width*2, x3_data, bar_width, alpha=opacity, color='r', label=('median'))
        b4 = ax.bar(np.arange(len(x4_data)) + bar_width * 3, x4_data, bar_width, alpha=opacity, color='y', label=('gmean'))
        # plt.bar((y1_data, y2_data, y3_data), (x1_data, x2_data, x3_data), label=('rms', 'mean', 'median'))
        # plt.bar(y1_data,x1_data, label=('rms'))
        # plt.bar(y2_data, x2_data, label=('mean'))
        # plt.bar(y2_data, x2_data, label=('median'))
        plt.xlabel('Аssessment')
        plt.ylabel('Count')
        plt.title('Compare')
        plt.legend()
        # plt.colorbar()
        # xi = [i for i in range(min(min(y1),min(y2),min(y3)), max(max(y1),max(y2),max(y3)),5)]
        # xi = [i for i in range(30, 80, 5)]
        plt.xticks(index + bar_width,y3_data)
        # plt.yticks(range(0, 100,10))
        # plt.xlim(min(min(y1),min(y2),min(y3))-5, max(max(y1),max(y2),max(y3))+5)
        plt.tight_layout()
        plt.show()

    def plot_bar1(self):
        self.city_grid_rms = pgj.load(filepath="./data/city_grid_rms_grad50_2.geojson")
        self.city_grid_mean = pgj.load(filepath="./data/city_grid_mean_grad50_2.geojson")
        self.city_grid_median = pgj.load(filepath="./data/city_grid_median_grad50_2.geojson")
        self.city_grid_gmean = pgj.load(filepath="./data/city_grid_gmean_grad50_2.geojson")
        x1, y1 = self.readPlotData1("./data/plot_rms.txt", self.city_grid_rms)
        x2, y2 = self.readPlotData1("./data/plot_mean.txt", self.city_grid_mean)
        x3, y3 = self.readPlotData1("./data/plot_median.txt", self.city_grid_median)
        x4, y4 = self.readPlotData1("./data/plot_median.txt", self.city_grid_gmean)

        count_y1 = OrderedDict(sorted(Counter(y1).items()))
        count_y2 = OrderedDict(sorted(Counter(y2).items()))
        count_y3 = OrderedDict(sorted(Counter(y3).items()))
        count_y4 = OrderedDict(sorted(Counter(y4).items()))

        y1_data = np.fromiter(count_y1.keys(), dtype=float)
        y2_data = np.fromiter(count_y2.keys(), dtype=float)
        y4_data = np.fromiter(count_y4.keys(), dtype=float)
        y3_data = np.fromiter(count_y3.keys(), dtype=float)
        x1_data = np.fromiter(count_y1.values(), dtype=float)
        x2_data = np.fromiter(count_y2.values(), dtype=float)
        x3_data = np.fromiter(count_y3.values(), dtype=float)
        x4_data = np.fromiter(count_y4.values(), dtype=float)
        # for i in range(0,len(count_y1)):
        #     a=count_y1.get(i)
        #     b=0
        # n_groups = 3
        # index = np.arange(n_groups)
        # bar_width = 0.35
        n_groups = max(len(y1_data),len(y2_data),len(y3_data),len(y4_data))
        fig, ax = plt.subplots()
        index = np.arange(n_groups)
        bar_width = 0.2
        opacity = 0.8
        b1 = ax.bar(np.arange(len(x1_data)), x1_data, bar_width, alpha=opacity, color='b', label=('rms'))
        b2 = ax.bar(np.arange(len(x2_data)) + bar_width, x2_data, bar_width, alpha=opacity, color='g', label=('mean'))
        b3 = ax.bar(np.arange(len(x3_data)) + bar_width*2, x3_data, bar_width, alpha=opacity, color='r', label=('median'))
        b4 = ax.bar(np.arange(len(x4_data)) + bar_width * 3, x4_data, bar_width, alpha=opacity, color='y', label=('gmean'))
        # plt.bar((y1_data, y2_data, y3_data), (x1_data, x2_data, x3_data), label=('rms', 'mean', 'median'))
        # plt.bar(y1_data,x1_data, label=('rms'))
        # plt.bar(y2_data, x2_data, label=('mean'))
        # plt.bar(y2_data, x2_data, label=('median'))
        plt.xlabel('Аssessment')
        plt.ylabel('Count')
        plt.title('Compare')
        plt.legend()
        # plt.colorbar()
        # xi = [i for i in range(min(min(y1),min(y2),min(y3)), max(max(y1),max(y2),max(y3)),5)]
        # xi = [i for i in range(30, 80, 5)]
        plt.xticks(index + bar_width,y3_data)
        # plt.yticks(range(0, 100,10))
        # plt.xlim(min(min(y1),min(y2),min(y3))-5, max(max(y1),max(y2),max(y3))+5)
        plt.tight_layout()
        plt.show()

    def plot_bar2(self):
        self.city_grid_rms = pgj.load(filepath="./data/city_grid_rms_grad50_2.geojson")
        self.city_grid_mean = pgj.load(filepath="./data/city_grid_mean_grad50_2.geojson")
        self.city_grid_median = pgj.load(filepath="./data/city_grid_median_grad50_2.geojson")
        self.city_grid_gmean = pgj.load(filepath="./data/city_grid_gmean_grad50_2.geojson")
        x1, y1 = self.readPlotData1("./data/plot_rms.txt", self.city_grid_rms)
        x2, y2 = self.readPlotData1("./data/plot_mean.txt", self.city_grid_mean)
        x3, y3 = self.readPlotData1("./data/plot_median.txt", self.city_grid_median)
        x4, y4 = self.readPlotData1("./data/plot_median.txt", self.city_grid_gmean)

        # count_y1 = OrderedDict(sorted(Counter(y1).items()))
        # count_y2 = OrderedDict(sorted(Counter(y2).items()))
        # count_y3 = OrderedDict(sorted(Counter(y3).items()))
        # count_y4 = OrderedDict(sorted(Counter(y4).items()))
        #
        # y1_data = np.fromiter(count_y1.keys(), dtype=float)
        # y2_data = np.fromiter(count_y2.keys(), dtype=float)
        # y4_data = np.fromiter(count_y4.keys(), dtype=float)
        # y3_data = np.fromiter(count_y3.keys(), dtype=float)
        # x1_data = np.fromiter(count_y1.values(), dtype=float)
        # x2_data = np.fromiter(count_y2.values(), dtype=float)
        # x3_data = np.fromiter(count_y3.values(), dtype=float)
        # x4_data = np.fromiter(count_y4.values(), dtype=float)

        n_groups = max(len(y1), len(y2), len(y3), len(y4))
        fig, ax = plt.subplots()
        index = np.arange(n_groups)
        bar_width = 0.2
        opacity = 0.8
        b1 = ax.bar(np.arange(len(x1)), x1, bar_width, alpha=opacity, color='b', label=('rms'))
        b2 = ax.bar(np.arange(len(x2)) + bar_width, x2, bar_width, alpha=opacity, color='g', label=('mean'))
        b3 = ax.bar(np.arange(len(x3)) + bar_width * 2, x3, bar_width, alpha=opacity, color='r', label=('median'))
        b4 = ax.bar(np.arange(len(x4)) + bar_width * 3, x4, bar_width, alpha=opacity, color='y', label=('gmean'))
        # plt.bar((y1_data, y2_data, y3_data), (x1_data, x2_data, x3_data), label=('rms', 'mean', 'median'))
        # plt.bar(y1_data,x1_data, label=('rms'))
        # plt.bar(y2_data, x2_data, label=('mean'))
        # plt.bar(y2_data, x2_data, label=('median'))
        plt.xlabel('Аssessment')
        plt.ylabel('Road length')
        plt.title('Compare')
        plt.legend()
        # plt.colorbar()
        # xi = [i for i in range(min(min(y1),min(y2),min(y3)), max(max(y1),max(y2),max(y3)),5)]
        # xi = [i for i in range(30, 80, 5)]
        plt.xticks(index + bar_width, y3)
        # plt.yticks(range(0, 100,10))
        # plt.xlim(min(min(y1),min(y2),min(y3))-5, max(max(y1),max(y2),max(y3))+5)
        plt.tight_layout()
        plt.show()

    def f(self):
        self.city_grid_rms = pgj.load(filepath="./data/city_grid_rms_grad50_1.geojson")
        self.city_grid_mean = pgj.load(filepath="./data/city_grid_mean_grad50_1.geojson")
        self.city_grid_median = pgj.load(filepath="./data/city_grid_median_grad50_1.geojson")
        x1, y1 = self.readPlotData1("./data/plot_rms.txt", self.city_grid_rms)
        x2, y2 = self.readPlotData1("./data/plot_mean.txt", self.city_grid_mean)
        x3, y3 = self.readPlotData1("./data/plot_median.txt", self.city_grid_median)
        y1_data = np.fromiter(Counter(y1).keys(), dtype=float)
        y2_data = np.fromiter(Counter(y2).keys(), dtype=float)
        y3_data = np.fromiter(Counter(y3).keys(), dtype=float)
        x1_data = np.fromiter(Counter(y1).values(), dtype=float)
        x2_data = np.fromiter(Counter(y2).values(), dtype=float)
        x3_data = np.fromiter(Counter(y3).values(), dtype=float)

        # data to plot
        n_groups = 4
        means_frank = (90, 55, 40, 65,10)
        means_guido = (85, 62, 54, 20)

        # create plot
        fig, ax = plt.subplots()
        index = np.arange(n_groups)
        bar_width = 0.35
        opacity = 0.8

        rects1 = plt.bar(np.arange(len(means_frank)), means_frank, bar_width,
                         alpha=opacity,
                         color='b',
                         label='Frank')

        rects2 = plt.bar(np.arange(len(means_guido)) + bar_width, means_guido, bar_width,
                         alpha=opacity,
                         color='g',
                         label='Guido')

        plt.xlabel('Person')
        plt.ylabel('Scores')
        plt.title('Scores by person')
        plt.xticks(index + bar_width, ('A', 'B', 'C', 'D'))
        plt.legend()

        plt.tight_layout()
        plt.show()

    def plot_hist3d(self):
        self.city_grid_rms = pgj.load(filepath="./data/city_grid_rms_grad50_1.geojson")
        # # self.city_grid_mean = pgj.load(filepath="./data/city_grid_mean_grad50_1.geojson")
        # # self.city_grid_median = pgj.load(filepath="./data/city_grid_median_grad50_1.geojson")
        x1, y1 = self.readPlotData1("./data/plot_rms.txt", self.city_grid_rms)
        # # x2, y2 = self.readPlotData1("./data/plot_mean.txt", self.city_grid_mean)
        # # x3, y3 = self.readPlotData1("./data/plot_median.txt", self.city_grid_median)
        #
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        x_data = np.array(y1).flatten()
        y_data = np.array(x1).flatten()
        count_array = Counter(y1)
        z_data = []
        for i in range(0,len(y1)):
            z_data.append(count_array[y1[i]])
        # # vals = np.fromiter(Counter(y1).values(), dtype=float)
        # # z_data = vals.flatten()
        z_data = np.array(z_data).flatten()

        # data_2d = [[1, 2, 3, 4],
        #            [7, 6, 5, 4],
        #            [7, 8, 9, 10]]
        # data_array = np.array(data_2d)
        # x_data, y_data = np.meshgrid(np.arange(data_array.shape[1]),
        #                              np.arange(data_array.shape[0]))
        # x_data = x_data.flatten()
        # y_data = y_data.flatten()
        # z_data = data_array.flatten()
        ax.bar3d(x_data,
                 y_data,
                 np.zeros(len(z_data)),
                 1, 1, z_data)
        plt.show()

    def main(self):
        # self.f()
        self.plot_bar2()
        # self.city_grid_l = pgj.load(filepath="./data/city_grid.geojson")
        # # self.draw_city_grid(self.city_grid_l)
        # start = time.time()
        # try:
        #     # x, y = self.calc_length_parallel(self.city_grid_l)
        #     # print("Выполнение запросов к БД ", time.time() - start)
        #     # x, y = self.roadlgt_eval(self.city_grid_l)
        #     x, y = self.readPlotData1("./data/plot_rms.txt", self.city_grid_l)
        #     self.plot_data(x, y)
        # except  Exception:
        #     print(Exception)

        # start = time.time()
        # self.xy_tofile(x,y)
        # print("Сохранение в файл ", time.time() - start)

if __name__ == '__main__':
    app = Plot()
    app.main()