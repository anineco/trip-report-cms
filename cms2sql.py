#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob
import json
import sqlite3
import sys

import mysql.connector

from config import DATA_DIR, DIST_DIR, HOME

ICON_SUMMIT = "symbols/Summit.png"

# open metadata database of trip reports
connection1 = sqlite3.connect(f"{DATA_DIR}/metadata.sqlite3")
cursor1 = connection1.cursor()

# open the geologiacl database of mountains for nearest point search
# NOTE: access to the database is limited to the repository owner
connection2 = mysql.connector.connect(
    option_files=f"{HOME}/.my.cnf", database="anineco_tozan"
)
cursor2 = connection2.cursor()


# read geojson file and find nearest summit
def read_geojson(file):
    with open(file, "r", encoding="utf-8") as f:
        root = json.load(f)

    for feature in root["features"]:
        # extract summit points
        geometry = feature["geometry"]
        propertys = feature["properties"]
        if not (geometry["type"] == "Point" and propertys["_iconUrl"] == ICON_SUMMIT):
            continue
        lon, lat = geometry["coordinates"]
        name = propertys["name"]
        # find nearest point
        sql = f"""
SET @p=ST_GeomFromText('POINT({lon} {lat})', 4326, 'axis-order=long-lat')
"""
        cursor2.execute(sql)
        sql = """
SELECT id, name, ST_Distance_Sphere(pt, @p) AS d FROM geom ORDER BY d LIMIT 1
"""
        cursor2.execute(sql)
        id, name, d = cursor2.fetchone()
        if d < 40:  # less than 40m
            d = round(d, 1)
            print(f"INSERT INTO explored VALUES (@rec, NULL, {id}); -- {name}, {d}m")


# command line arguments
if len(sys.argv) != 2:
    print(f"Usage: {sys.argv[0]} <cid>", file=sys.stderr)
    sys.exit(1)
cid = sys.argv[1]  # Content ID

# write SQL for register new article
sql = """
SELECT start, end, pub, title, summary, link, img1x FROM metadata WHERE cid=?
"""
cursor1.execute(sql, (cid,))
start, end, pub, title, summary, link, img1x = cursor1.fetchone()
sql = f"""
INSERT INTO record VALUES (NULL, '{start}', '{end}', '{pub}', '{title}', '{summary}', '{link}', '{img1x}');
"""
print(sql)
print("SET @rec=LAST_INSERT_ID();")

# write SQL for register explored points
for file in glob.glob(f"{DIST_DIR}/{cid}/routemap*.geojson"):
    read_geojson(file)

connection1.close()
connection2.close()
# __END__
