import os
import folium
import time
# import sys
# from geodata import *
# from folium.features import DivIcon
# import webbrowser
import pygeoj as pgj
from geographiclib.geodesic import Geodesic
from shapely.geometry import Point, Polygon
import numpy as np
from threading import Thread

# from pyroutelib3 import Router
from osrm_routes import osrm_routes

#import osrm
#osrm.RequestConfig.host = 'router.project-osrm.org'
adj_matrix = np.zeros((5,5))
class RequesterThread(Thread):
    def __init__(self, data, size,index,range):
        """Инициализация потока"""
        Thread.__init__(self)
        self.data = data
        self.size = size
        self.index = index
        self.range = range

    def run(self):
        """Запуск потока"""
        length = self.data.__len__()
        max = self.index+self.range
        if self.index+self.range > length:
            max = length
        for i in range(self.index,max):
            temp = []
            for j in range(0, length):
                if j == i:
                    temp.append(0)
                else:
                    radius = self.size * (2 ** 0.5) / 2
                    p1 = Map_prestige.get_new_coord(self,(self.data.get_feature(i).geometry.coordinates[0][0]), 135, radius)
                    p2 = Map_prestige.get_new_coord(self,(self.data.get_feature(j).geometry.coordinates[0][0]), 135, radius)
                    temp.append(float(Map_prestige.calc_distance(self,[p1, p2])))
            adj_matrix[i] = temp

class Map_prestige():
    def __init__(self):
        self.colors_grad = ["#E50023","#E01F00","#DC6000","#D89E00","#CDD400","#8CCF00","#4CCB00","#10C700","#00C32A","#00BF62"]
        self.stepinthread = 1

        self.m = folium.Map(location=[ 48.747316, 44.51088], zoom_start=10)

        self.boundary = pgj.load(filepath="./data/boundary_gjs.geojson")
        self.fg_cc = folium.FeatureGroup(name="City contours(all)")
        self.m.add_child(self.fg_cc)

        self.admins_geojs = pgj.load(filepath="./data/admin.geojson")
        self.fg_cd = folium.FeatureGroup(name="City district")
        self.m.add_child(self.fg_cd)

        self.fg_tp = folium.FeatureGroup(name="Transport Points")
        self.tp_geojs = pgj.load(filepath="./data/transport_points.geojson")
        self.m.add_child(self.fg_tp)

        self.fg_grid = folium.FeatureGroup(name="Grid")
        self.m.add_child(self.fg_grid)

    def draw_city_boundary(self,data,featuregroup):
        for gj in data.__dict__['_data']['features']:
            pl = folium.GeoJson(gj)
            pl.add_to(featuregroup)

    def draw_city_district(self,data,featuregroup):
        for gj in data.__dict__['_data']['features']:
            if gj['properties']['admin_leve'] == 9:
                pl = folium.GeoJson(gj)
                pl.add_child(folium.Popup(gj['properties']['name']))
                pl.add_to(featuregroup)

    def draw_transport_points(self,data,featuregroup):
        for gj in data.__dict__['_data']['features']:
            if gj['properties']['name'] != None:
                pl = folium.GeoJson(gj)
                pl.add_child(folium.Popup(gj['properties']['name']))
                pl.add_to(featuregroup)

    def generate_city_grid(self,featuregroup_in,map_out,size):
        b = featuregroup_in.get_bounds()

        lt_abs = [b[1][0], b[0][1]] #left-top
        lb_abs = [b[0][0], b[0][1]] # left-bottom
        rb_abs = [b[0][0], b[1][1]] # right-bottom
        rt_abs = [b[1][0], b[1][1]] # right-top

        #folium.PolyLine([lt_abs,rt_abs,rb_abs,lb_abs,lt_abs],color='blue').add_to(self.fg_grid)

        city_grid = pgj.new()

        count_x = round((self.get_distance([lt_abs,rt_abs])/size)+0.5)
        count_y = round((self.get_distance([lt_abs,lb_abs])/size)+0.5)

        for i in range(0,count_y): #from lt to lb
            lt_str = self.get_new_coord(list(reversed(lt_abs)), 180, size * i)
            for j in range(0, count_x): #from lt to rt
                lt = self.get_new_coord(lt_str, 90, size * j)
                rt = self.get_new_coord(lt, 90, size)
                rb = self.get_new_coord(rt, 180, size)
                lb = self.get_new_coord(rb, 270, size)
                points = [[lt, rt, rb, lb]]
                city_grid.add_feature(properties = {"stroke": "#fc1717",
                                                    "fill_color": "#85cdc1",
                                                    "prestige": i+j},
                                        geometry={"type": "Polygon", "coordinates": points})

        city_grid.save("./data/city_grid.geojson")

    def draw_city_grid(self,data,featuregroup):
        for gj in data.__dict__['_data']['features']:
            pl = folium.GeoJson(gj, style_function=lambda x: {
                'color': x['properties']['stroke'],
                'fillColor': x['properties']['fill_color'],
                'opacity': 0,
                'fillOpacity': 0.5
            })
            pl.add_child(folium.Popup(str(gj['properties']['prestige'])))
            pl.add_to(featuregroup)

    def remove_null_cells(self,data):
        points = self.boundary.get_feature(0).geometry.coordinates
        data_out = pgj.new()
        for i in range(0,len(data)):
            layer1 = Polygon(data.get_feature(i).geometry.coordinates[0])
            layer2 = Polygon(points[0][0])
            points_intersect = layer1.intersection(layer2)
            if not points_intersect.is_empty:
                data_out.addfeature(data.get_feature(i))
                # data.__dict__['_data']['features'][i]['properties']['fill_color'] = "#000036"
                # data.__dict__['_data']['features'][i]['properties']['stroke'] = "#000000"

        return data_out

    def get_new_coord(self,coords,azimut,radius):
        # azimut: 0 - up, 90 - right, 180 - down, 270 - left
        geod = Geodesic.WGS84  # define the WGS84 ellipsoid
        dic = geod.Direct(coords[1],coords[0],azimut,radius)
        return [dic['lon2'],dic['lat2']]

    def get_distance(self,coords):
        geod = Geodesic.WGS84  # define the WGS84 ellipsoid
        distance = geod.Inverse(coords[0][0],coords[0][1],coords[1][0],coords[1][1])
        return float(distance['s12'])

    def draw_rivers(self):
        self.waterareas = pgj.load(filepath="./data/waterareas.geojson")
        for gj in self.waterareas.__dict__['_data']['features']:
            pl = folium.GeoJson(gj)
            pl.add_to(self.m)

    def generate_route(self,coords):

        folium.Marker([coords[0][1],coords[0][0]]).add_to(self.m)
        folium.Marker([coords[1][1], coords[1][0]]).add_to(self.m)

        p1 = osrm.Point(latitude=coords[0][0], longitude=coords[0][1])
        p2 = osrm.Point(latitude=coords[1][0], longitude=coords[1][1])

        result = osrm.simple_route( p1, p2, output='route', overview="full", geometry='wkt')
        print(result[0]['distance'])
        list_coords = result[0]['geometry'].split(',')
        for i in range(0,len(list_coords)):
            if i == 0:
                list_coords[i] = list_coords[i][list_coords[i].find('(')+1:]
            if i == len(list_coords)-1:
                list_coords[i] = list_coords[i][:list_coords[i].find(')')-1]
            list_coords[i] = list_coords[i].split(' ')
            temp = float(list_coords[i][0])
            list_coords[i][0] = float(list_coords[i][1])
            list_coords[i][1] = temp
        folium.PolyLine(list_coords).add_to(self.m)

    def calc_adjacency_matrix(self,data,size,read_matrix):

        length = data.__len__()
        global adj_matrix
        adj_matrix = np.zeros((length,length))
        start = time.time()

        if read_matrix:
            # TODO считывание матрицы с файла
            txt = open('./data/adjacency_matrix.txt').readlines()
            mas = []
            for i in txt:
                temp = i.split('\n')
                temp = temp[0].rstrip()
                mas.append(temp.split('\t'))

            for i in range(0, length):
                for j in range(0, length):
                    adj_matrix[i][j] = float(mas[i][j])
        else:
            threads = []
            #TODO self.stepinthread динмическое кол-во итераций в одном потоке

            for i in range(0,length,self.stepinthread):
                thread = RequesterThread(data,size,i,self.stepinthread)
                thread.setDaemon(True)
                threads.append(thread)
                thread.start()

            for t in threads:
                t.join()


        print("Расчет\\считывание матрицы смежности", time.time()-start)

        if read_matrix != True:
            output_file = open('./data/adjacency_matrix.txt', 'w+')
            for i in adj_matrix:
                for j in i:
                    output_file.write(str(j) + '\t')
                output_file.write('\n')

        start = time.time()
        self.calc_grad_eval_con_cells(adj_matrix)
        print("Оценка доступноти", time.time() - start)

    def calc_distance(self,coords):
        # p1 = osrm.Point(latitude=coords[0][0], longitude=coords[0][1])
        # p2 = osrm.Point(latitude=coords[1][0], longitude=coords[1][1])
        #
        # result = osrm.simple_route(p1, p2, output='route', overview="full", geometry='wkt')
        distance = osrm_routes.get_distante(points=''+str(coords[0][0])+','+str(coords[0][1])+';'+str(coords[1][0])+','+str(coords[1][1]))
        return distance #float(result[0]['distance'])
        # router = Router("car")
        # start = router.data.findNode(coords[0][1],coords[0][0])
        # end = router.data.findNode(coords[1][1],coords[1][0])
        # print(start)
        # print(end)
        # status, route = router.doRoute(start,end)
        # print(status)
        # print(route)

    def calc_grad_eval_con_cells(self,matrix):
        eval_cells = []
        matrix_temp = []
        start = time.time()
        for i in matrix:
            temp = []
            for j in i:
                if j !=0:
                    temp.append(j)
            matrix_temp.append(temp)
        print("Удаление нулевых значений из матрицы смежности", time.time() - start)

        matrix = np.array(matrix_temp)
        temp_min = []
        temp_max = []
        for i in matrix:
            temp_min.append(np.min(i))
            temp_max.append(np.max(i))
        grad_min = np.min(temp_min)
        grad_max = np.max(temp_max)

        grad = np.linspace(grad_min, grad_max, 11)
        index = 0
        for i in matrix:
            i_ = np.array(i)
            temp = []

            for j in i:
                for k in range(1, len(grad)):
                    if j <= grad[k]:
                        temp.append(10-k)
                        break
            self.city_grid_l.__dict__['_data']['features'][index]['properties']['prestige'] = str(temp)

            for j in range(1,len(grad)):
                if i_.mean() <= grad[j]:
                    self.city_grid_l.__dict__['_data']['features'][index]['properties']['prestige'] = str(
                        self.city_grid_l.__dict__['_data']['features'][index]['properties']['prestige']) + ' ' + str(
                        10 - j)
                    self.city_grid_l.__dict__['_data']['features'][index]['properties']['fill_color'] = self.colors_grad[
                        10 - j]
                    break
            index += 1

    def main(self):
        self.draw_city_boundary(self.boundary,self.fg_cc)
        # self.draw_rivers()
        start = time.time()
        self.generate_city_grid(self.fg_cc,self.m,2500)
        print("Генерация сетки", time.time() - start)
        self.city_grid_l = pgj.load(filepath="./data/city_grid.geojson")
        start = time.time()
        self.city_grid_l = self.remove_null_cells(self.city_grid_l)
        print("Удаление пустых ячеек", time.time() - start)
        self.city_grid_l.save("./data/city_grid.geojson")
        self.calc_adjacency_matrix(self.city_grid_l,2500,True)

        #print(osrm_routes.get_distante(points='13.388860,52.517037;13.397634,52.529407'))
        #self.generate_route([ self.city_grid_l.get_feature(0).geometry.coordinates[0][2],self.city_grid_l.get_feature(11).geometry.coordinates[0][2]])
        self.draw_city_grid(self.city_grid_l, self.fg_grid)
        #self.draw_city_district(self.admins_geojs,self.fg_cd)
        #self.draw_transport_points(self.tp_geojs,self.fg_tp)
        self.m.add_child(folium.LayerControl())
        self.m.save(os.path.join('', 'map.html'))
        #webbrowser.open('map.html', new=2)

if __name__ == '__main__':
    app = Map_prestige()
    app.main()