import os
import folium
import sys
from geodata import *
from folium.features import DivIcon
import webbrowser
import pygeoj as pgj
from geographiclib.geodesic import Geodesic

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

    def generate_map_grid(self,featuregroup,map_out):
        b = featuregroup.get_bounds()

        lt = [b[1][0], b[0][1]] #left-top
        lb = [b[0][0], b[0][1]] # left-bottom
        rb = [b[0][0], b[1][1]] # right-bottom
        rt = [b[1][0], b[1][1]] # right-top

        folium.PolyLine([lt,rt,rb,lb,lt],color='red').add_to(map_out)

        folium.RegularPolygonMarker(lt,color='black').add_to(map_out)    #left-top
        folium.RegularPolygonMarker(lb,color='red').add_to(map_out)      #left-bottom
        folium.RegularPolygonMarker(rb,color='green').add_to(map_out)   #right-bottom
        folium.RegularPolygonMarker(rt,color='yellow').add_to(map_out)  #right-top

        folium.RegularPolygonMarker(self.get_new_coord(lt,0,1000),color='cian').add_to(map_out)

    def get_new_coord(self,coords,azimut,radius):
        geod = Geodesic.WGS84  # define the WGS84 ellipsoid
        dic = geod.Direct(coords[1],coords[0],azimut,radius)
        return [dic['lon2'],dic['lat2']]

    def main(self):
        self.draw_city_boundary(self.boundary,self.fg_cc)
        self.generate_map_grid(self.fg_cc,self.m)
        #self.draw_city_district(self.admins_geojs,self.fg_cd)
        #self.draw_transport_points(self.tp_geojs,self.fg_tp)
        self.m.add_child(folium.LayerControl())
        self.m.save(os.path.join('', 'map.html'))
        webbrowser.open('map.html', new=2)

if __name__ == '__main__':
    app = Map()
    app.main()