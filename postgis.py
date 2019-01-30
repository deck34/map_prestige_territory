import folium
import psycopg2 as psql
import psycopg2.extras as ex
import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon
import string

# [82.7511322, 54.7996311993747, 83.16091036697941, 55.13473551670991]}
p1 = [54.7996311993747, 82.7511322],[55.13473551670991, 82.7511322],[55.13473551670991, 83.16091036697941],[54.7996311993747, 83.16091036697941],[54.7996311993747, 82.7511322]
p2 = [82.7511322, 54.7996311993747],[82.7511322, 55.13473551670991],[83.16091036697941, 55.13473551670991],[83.16091036697941, 54.7996311993747],[82.7511322, 54.7996311993747]
p = [83.1243317058348, 54.801877104722], [83.12821918232737, 54.80187704246452], [83.12821918232737, 54.79963126162705], [83.1243317058348, 54.801877104722]
p_t = str(p2)
p_t = p_t.replace(",", "")
p_t = p_t.replace("]", ",")
p_t = p_t.replace("[", "")
p_t = p_t.replace("(", "")
p_t = p_t.replace(")", "")
p_t = p_t[0:len(p_t)-1]
# print(p_t[0:len(p_t)-1])

db = psql.connect(dbname='postgis_db', user='postgis_db', password='postgis_db', host='localhost')
curr = db.cursor()
name = 'Новосибирск'
# request = "SELECT way_area FROM planet_osm_polygon WHERE name = '" + name + "'"
# request = "SELECT st_astext(st_transform(way, 4326)),name FROM planet_osm_polygon WHERE name= '" + name + "'" координаты границ города
request = "SELECT st_transform(way, 4326) as POLYGON ,name FROM planet_osm_polygon WHERE name= '" + name + "'"
# r = "SELECT osm_id, name, ST_AsText(ST_Transform(way,4326)) FROM planet_osm_roads WHERE ST_Intersects(ST_GeomFromText('POLYGON(("+p_t+"))',4326), ST_Transform(way,4326));"
r = "SELECT SUM(ST_LENGTH(ST_Intersection(ST_GeomFromText('POLYGON(("+p_t+"))',4326), ST_GeomFromText(ST_AsText(ST_Transform(way,4326)),4326)))) FROM planet_osm_line WHERE ST_Intersects(ST_GeomFromText('POLYGON(("+p_t+"))',4326), ST_GeomFromText(ST_AsText(ST_Transform(way,4326)),4326))"
curr.execute(r)
r = curr.fetchall()
# =print(r[0][0])
for item in r:
    print(item)

# polygon_geom = r[0][0]
# polygon_geom = polygon_geom[1:len(polygon_geom)-4]
# print(polygon_geom)
# crs = {'init': 'epsg:4326'}
# polygon = gpd.GeoDataFrame(index=[0], crs=crs, geometry=[polygon_geom])
# polygon.to_file(filename='polygon.geojson', driver='GeoJSON')
# m = folium.Map(location=[ 48.747316, 44.51088], zoom_start=4)
# folium.GeoJson(polygon).add_to(m)
# fg_cc = folium.FeatureGroup(name="City contours(all)")
# m.add_child(fg_cc)
#
# pl = folium.Polygon(r[0])
# pl.add_to(fg_cc)