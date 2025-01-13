#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob
import json
import os
import sqlite3
import sys

import mysql.connector

ICON_SUMMIT = 'symbols/Summit.png'

# open metadata database of trip reports
connection1 = sqlite3.connect('data/metadata.sqlite3')
cursor1 = connection1.cursor()

# open geologiacl database of mountains for nearest point search
connection2 = mysql.connector.connect(
    option_files=os.path.expanduser('~/.my.cnf'),
    database='anineco_tozan'
)
cursor2 = connection2.cursor()

# read geojson file and find nearest summit from geological database
def read_geojson(file):
    with open(file, 'r', encoding='utf-8') as f:
        root = json.load(f)

    for feature in root['features']:
        # extract summit points
        geometry = feature['geometry']
        propertys = feature['properties']
        if not (geometry['type'] == 'Point' and propertys['_iconUrl'] == ICON_SUMMIT):
            continue
        lon, lat = geometry['coordinates']
        name = propertys['name']
        # find nearest point
        cursor2.execute(f"SET @p=ST_GeomFromText('POINT({lon} {lat})',4326,'axis-order=long-lat')")
        cursor2.execute('SELECT id,name,ST_Distance_Sphere(pt,@p) AS d FROM geom ORDER BY d LIMIT 1')
        id, name, d = cursor2.fetchone()
        if d < 40: # less than 40m
            d = round(d, 1)
            print(f'INSERT INTO explored VALUES (@rec,NULL,{id}); -- {name},{d}m')

# command line arguments
if len(sys.argv) != 2:
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
