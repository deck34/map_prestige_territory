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