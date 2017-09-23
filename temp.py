import os
import folium
import sys
from geodata import *
from folium.features import DivIcon
import webbrowser
import pygeoj as pgj

class Map():
    def __init__(self):
        self.m = folium.Map(location=[ 48.747316, 44.51088], zoom_start=10)

    def draw_city_boundary(self):
        boundary = pgj.load(filepath="./data/boundary_gjs.geojson")
        fg=folium.FeatureGroup(name="City contours(all)")
        for gj in boundary.__dict__['_data']['features']:
            pl = folium.GeoJson(gj)
            pl.add_to(fg)
        self.m.add_child(fg)

    def draw_city_district(self):
        admins_geojs = pgj.load(filepath="./data/admin.geojson")
        fg = folium.FeatureGroup(name="City district")
        for gj in admins_geojs.__dict__['_data']['features']:
            if gj['properties']['admin_leve'] == 9:
                pl = folium.GeoJson(gj)
                pl.add_child(folium.Popup(gj['properties']['name']))
                pl.add_to(fg)
        self.m.add_child(fg)

    def draw_transport_points(self):
        fg1=folium.FeatureGroup(name="Transport Points")
        tp_geojs = pgj.load(filepath="./data/transport_points.geojson")
        for gj in tp_geojs.__dict__['_data']['features']:
            if gj['properties']['name'] != None:
                pl = folium.GeoJson(gj)
                pl.add_child(folium.Popup(gj['properties']['name']))
                pl.add_to(fg1)
        self.m.add_child(fg1)

    def main(self):
        self.draw_city_boundary()
        self.draw_city_district()
        self.draw_transport_points()
        self.m.add_child(folium.LayerControl())
        self.m.save(os.path.join('', 'm.html'))
        webbrowser.open('m.html', new=2)

if __name__ == '__main__':
    app = Map()
    app.main()

#----------------------------------------------
#
# for gj in geoJsonData['features']:
#    # print(gj)
#     pl = folium.GeoJson(gj,style_function=lambda x: {
#         'color' : x['properties']['stroke'],
#         'weight' : x['properties']['stroke-width'],
#         'opacity': x['properties']['stroke-opacity'],
#         'fillColor' : x['properties']['stroke'],
#         'name' : x['properties']['name'],
#         })
#     pl.add_child(folium.Popup(gj['properties']['name']))
#     pl.add_to(fg)
# m.add_child(fg)
#
# html="""
#     <h1> This is a big popup</h1><br>
#     With a few lines of code...
#     <p>
#     <code>
#         from numpy import *<br>
#         exp(-2*pi)
#     </code>
#     </p>
#     """
# iframe = folium.IFrame(html=html, width=500, height=300)
# #.add_child(folium.Popup(iframe,max_width=500))
#
#
# folium.GeoJson(geoJsonData,style_function=lambda x: {
#         'color' : x['properties']['stroke'],
#         'weight' : x['properties']['stroke-width'],
#         'opacity': x['properties']['stroke-opacity'],
#         'fillColor' : x['properties']['stroke'],
#         'Popup' : x['properties']['name'],
#         }).add_to(m)
#
# folium.map.Marker(
#     [56.70450561416937,12.98583984375],
#     icon=DivIcon(
#         icon_size=(150,36),
#         icon_anchor=(0,0),
#         html='<div style="font-size: 24pt">Test</div>',
#         )
#     ).add_to(m)