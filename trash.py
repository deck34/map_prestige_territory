import osmnx as ox
from shapely.geometry import Point, Polygon

G = ox.graph_from_place('Manhattan Island, New York City, New York, USA', network_type='drive')
bbox = [44.1883745, 46.270169, 44.3398689, 46.3394103]
# p = Polygon([[82.84099937170515, 55.006780231540105], [82.84490663896092, 55.00678016881035], [82.84490663896092, 55.00453446419033], [82.84099958998117, 55.004534401465776]])
# g = ox.graph_from_polygon(p, network_type='drive')
# ox.plot_graph(ox.project_graph(g))
# g = ox.graph_from_bbox(44.1095807, 48.4070531, 44.6898741, 48.8890717, network_type='drive')
graph_proj = ox.project_graph(G)
ox.plot_graph(ox.project_graph(G))
stats = ox.basic_stats(graph_proj)
print(stats)
# import re, string
#
# txt = open('data\\adjacency_matrix_example.txt').readlines()
# mas = []
# for i in txt:
#     temp = i.split('\n')
#     temp = temp[0].rstrip()
#     mas.append(temp.split('\t'))
# # print(mas[0][mas.__len__()])
# for i in mas:
#     print(i)

    # print(osrm_routes.get_distante(points='13.388860,52.517037;13.397634,52.529407'))
    # self.generate_route([ self.city_grid_l.get_feature(0).geometry.coordinates[0][2],self.city_grid_l.get_feature(11).geometry.coordinates[0][2]])


# from osmread import parse_file, Way
#
# tags = []
# count = 0
# for entity in parse_file('data/crimean.osm.pbf'):
#     if entity.tags not in tags:
#         tags.append(entity.tags)
#         count += 1
# print(count)

#----------------------------------------------
#
# def get_minimum_distance(self, point, points):
#     minimum = 10 ** 10 + 0.1
#     for i in points:
#         dist = self.get_distance([point, i])
#         if dist < minimum:
#             minimum = dist
#     return minimum

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