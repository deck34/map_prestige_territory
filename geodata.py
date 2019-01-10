import re
import csv
import os
import pygeoj as pgj

def from_txt_to_geojson():
    input_file = open("./data/results_c.txt", "r+")

    with open("./data/gis_osm_places_a_free_1_c.csv", "r+",encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, dialect='excel')
        # output_file = open('./data/bounds.txt', 'w+')
        list=[]
        first=True
        for rec in reader:
            if first:
                first=False
                continue
            s = re.split(';', rec[0])
            list.append([s[2].strip(),s[4].strip()])

    bounds = pgj.new()
    points=[]
    i=0
    addingpoints=False

    for rec in input_file:
        s = re.split('\t', rec)
        if s[0]=="box":
            bbox = [[float(s[2].strip().replace(',','.')), float(s[3].strip().replace(',','.'))], [float(s[4].strip().replace(',','.')), float(s[5].strip().replace(',','.'))]]
        if s[0]==">>":
            addingpoints=True
            points.append([float(s[2].strip().replace(',','.')), float(s[3].strip().replace(',','.'))])
        elif addingpoints==True:
            addingpoints=False
            _points=points.copy()
            # if list[i][0] == "city" and list[i][1] == "Санкт-Петербург":
            # Для новосиба надо удалять 4 последние координаты
            if list[i][0] == "city" and list[i][1] == "Москва":
                bounds.add_feature(properties = {"name": list[i][1], "bbox": bbox},
                                   geometry={"type": "Polygon", "coordinates": [_points]})
            points.clear()
            bbox.clear()
            i+=1

    bounds.save("./data/bounds.geojson")
    # return bounds

from_txt_to_geojson()