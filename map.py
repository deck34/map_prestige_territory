import os
import folium
import sys
from geodata import *
from folium.features import DivIcon
import webbrowser
import pygeoj as pgj
from geographiclib.geodesic import Geodesic
from shapely.geometry import Point, Polygon

class Map():
    def __init__(self):
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

    def main(self):
        self.draw_city_boundary(self.boundary,self.fg_cc)
        #self.draw_rivers()
        #self.generate_city_grid(self.fg_cc,self.m,2500)
        self.city_grid_l = pgj.load(filepath="./data/city_grid.geojson")
        self.city_grid_l = self.remove_null_cells(self.city_grid_l)
        self.draw_city_grid(self.city_grid_l, self.fg_grid)
        #self.draw_city_district(self.admins_geojs,self.fg_cd)
        #self.draw_transport_points(self.tp_geojs,self.fg_tp)
        self.m.add_child(folium.LayerControl())
        self.m.save(os.path.join('', 'map.html'))
        #webbrowser.open('map.html', new=2)

if __name__ == '__main__':
    app = Map()
    app.main()