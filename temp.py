import os
import folium
geoJsonData = {
    "features": [
        {
            "geometry": {
                "coordinates": [[
                    [
                        12.98583984375,
                        56.70450561416937
                    ],
                    [
                        14.589843749999998,
                        57.604221411628735
                    ],
                    [
                        13.590087890625,
                        58.15331598640629
                    ],
                    [
                        11.953125,
                        57.955674494979526
                    ],
                    [
                        11.810302734375,
                        58.76250326278713
                    ]
                ]],
                "type": "Polygon"
            },
            "properties": {
                "stroke": "#fc1717",
                "stroke-opacity": 1,
                "stroke-width": 2,
                "name": "name1"
            },
            "type": "Feature"
        },
        {
            "geometry": {
                "coordinates": [
                    [
                        14.9468994140625,
                        57.7569377956732
                    ],
                    [
                        15.078735351562498,
                        58.06916140721414
                    ],
                    [
                        15.4302978515625,
                        58.09820267068277
                    ],
                    [
                        15.281982421875002,
                        58.318144965188246
                    ],
                    [
                        15.4852294921875,
                        58.36427519285588
                    ]
                ],
                "type": "LineString"
            },
            "properties": {
                "stroke": "#1f1a95",
                "stroke-opacity": 1,
                "stroke-width": 2,
                "name": "name1"
            },
            "type": "Feature"
        }
    ],
    "type": "FeatureCollection"
}
m = folium.Map(location=[ 56.7, 12.9], zoom_start=6)

html="""
    <h1> This is a big popup</h1><br>
    With a few lines of code...
    <p>
    <code>
        from numpy import *<br>
        exp(-2*pi)
    </code>
    </p>
    """
iframe = folium.IFrame(html=html, width=500, height=300)

folium.GeoJson(geoJsonData,
    style_function=lambda x: {
        'color' : x['properties']['stroke'],
        'weight' : x['properties']['stroke-width'],
        'opacity': 0.6,
        'fillColor' : x['properties']['stroke'],
        'name' : x['properties']['name'],
        }).add_child(folium.Popup(iframe,max_width=500)).add_to(m)
m.save(os.path.join('', 'm.html'))