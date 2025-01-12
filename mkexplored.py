#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import glob
import json
import os
import sqlite3
import sys

import mysql.connector

# open sqlite3 connection
connection1 = sqlite3.connect('metadata.sqlite3')
cursor1 = connection1.cursor()

# open mysql connection
connection2 = mysql.connector.connect(
    option_files=os.path.expanduser('~/.my.cnf'),
    database='anineco_tozan'
)
cursor2 = connection2.cursor()

# read geojson file and write SQL for register explored points
def read_geojson(file):
    with open(file, 'r', encoding='utf-8') as f:
        root = json.load(f)

    for feature in root['features']:
        # extract summit points
        geometry = feature['geometry']
        propertys = feature['properties']
        if not (geometry['type'] == 'Point' and propertys['_iconUrl'] == 'symbols/Summit.png'):
            continue
        coordinates = geometry['coordinates']
        name = propertys['name']
        lon = coordinates[0]
        lat = coordinates[1]
        # find nearest point
        cursor2.execute(f"SET @p=ST_GeomFromText('POINT({lon} {lat})',4326,'axis-order=long-lat')")
        cursor2.execute('SELECT id,name,ST_Distance_Sphere(pt,@p) AS d FROM geom ORDER BY d LIMIT 1')
        id, name, d = cursor2.fetchone()
        if d < 40:
            d = round(d, 1)
            print(f'INSERT INTO explored VALUES (@rec,NULL,{id}); -- {name},{d}m')

# command line arguments
if len(sys.argv) < 1:
    print(f"Usage: {sys.argv[0]} <cid>", file=sys.stderr)
    sys.exit(1)
cid = sys.argv[1] # Content ID

# write SQL for register new article
cursor1.execute('SELECT start,end,pub,title,summary,link,img1x FROM metadata WHERE cid=?', (cid,))
start, end, pub, title, summary, link, img1x = cursor1.fetchone()
print(f'INSERT INTO record VALUES (NULL,"{start}","{end}","{pub}","{title}","{summary}","{link}","{img1x}");')
print('SET @rec=LAST_INSERT_ID();')

# write SQL for register explored points
for file in glob.glob(f"docs/{cid}/routemap*.geojson"):
    read_geojson(file)

connection1.close()
connection2.close()
# __END__
