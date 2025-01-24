#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob
import json
import requests
import sqlite3
import sys

from config import DATA_DIR, DIST_DIR

ICON_SUMMIT = "symbols/Summit.png"
DBURL = "https://map.jpn.org/share/db.php"

# command line arguments
if len(sys.argv) != 2:
    print(f"Usage: {sys.argv[0]} <cid>", file=sys.stderr)
    sys.exit(1)
cid = sys.argv[1]  # Content ID

# open metadata database of trip reports
connection = sqlite3.connect(f"{DATA_DIR}/metadata.sqlite3")
cursor = connection.cursor()

# write SQL for register new article
sql = """
SELECT start, end, pub, title, summary, link, img1x FROM metadata WHERE cid=?
"""
cursor.execute(sql, (cid,))
start, end, pub, title, summary, link, img1x = cursor.fetchone()
sql = f"""
INSERT INTO record VALUES (NULL, '{start}', '{end}', '{pub}', '{title}', '{summary}', '{link}', '{img1x}');
"""
print(sql)
print("SET @rec=LAST_INSERT_ID();")

connection.close()

# gather summit points
wpts = set()
for file in glob.glob(f"{DIST_DIR}/{cid}/routemap*.geojson"):
    with open(file, "r", encoding="utf-8") as f:
        root = json.load(f)
    for feature in root["features"]:
        geometry = feature["geometry"]
        propertys = feature["properties"]
        if geometry["type"] == "Point" and propertys["_iconUrl"] == ICON_SUMMIT:
            lon, lat = geometry["coordinates"]
            wpts.add((lon, lat))

# find the nearest point for each summit
ids = set()
for lon, lat in wpts:
    response = requests.get(f"{DBURL}?mt=1&lon={lon}&lat={lat}")
    if not response.ok:
        print(f"Error: {response.status_code}")
        sys.exit(1)
    data = response.json()
    id, name, d = data[0]["id"], data[0]["name"], data[0]["d"]
    if id not in ids and d < 40:  # less than 40m
        d = round(d, 1)
        print(f"INSERT INTO explored VALUES (@rec, NULL, {id}); -- {name}, {d}m")
        ids.add(id)

# __END__
