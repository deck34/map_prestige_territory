import os
import folium

map = folium.Map(location=[48.710678, 44.516804],
                   zoom_start=13)

folium.RegularPolygonMarker(
    [48.705362, 44.55],
    popup='test',
    fill_color='#45647d',
    fill_opacity=0.1,
    number_of_sides=4,
    radius=100,
    rotation=0
    ).add_to(map)
folium.PolyLine([
                 [48.7218079,44.5595556],
                 [48.7600321,44.6452483],
                 [48.8020533,44.6733084]
                ]).add_to(map)
map.save(os.path.join('', 'map.html'))