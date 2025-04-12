#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import glob
import json
import sqlite3
import sys

import requests

from config import DATA_DIR, DIST_DIR

ICON_SUMMIT = "symbols/Summit.png"
DBURL = "https://map.jpn.org/share/mt.php"

# command line arguments
if len(sys.argv) != 2:
    print(f"Usage: {sys.argv[0]} <cid>", file=sys.stderr)
    sys.exit(1)
cid = sys.argv[1]  # Content ID

# open metadata database of trip reports
connection = sqlite3.connect(f"file:{DATA_DIR}/metadata.sqlite3?mode=ro", uri=True)
connection.isolation_level = None
cursor = connection.cursor()

# write SQL for register new article
sql = """
SELECT start, end, pub, title, summary, link, img1x FROM metadata WHERE cid=?
"""
cursor.execute(sql, (cid,))
try:
    start, end, pub, title, summary, link, img1x = cursor.fetchone()
except TypeError:
    print(f"Error: cid {cid} not found", file=sys.stderr)
    sys.exit(1)
sql = f"INSERT INTO record VALUES (NULL, '{start}', '{end}', '{pub}', '{title}', '{summary}', '{link}', '{img1x}');"
print(sql)
print("SET @rec=LAST_INSERT_ID();")

connection.close()

# gather summit points
summits = {}  # (lon, lat) -> name
for file in glob.glob(f"{DIST_DIR}/{cid}/routemap*.geojson"):
    with open(file, "r", encoding="utf-8") as f:
        root = json.load(f)
    for feature in root["features"]:
        geometry = feature["geometry"]
        propertys = feature["properties"]
        if geometry["type"] == "Point" and propertys["_iconUrl"] == ICON_SUMMIT:
            lon, lat = geometry["coordinates"]
            name = propertys["name"]
            if (lon, lat) not in summits:
                summits[(lon, lat)] = name
            elif name != summits[(lon, lat)]:
                print(f"Error: name {name} is duplicated", file=sys.stderr)
                sys.exit(1)

# find the nearest point for each summit
points = {}  # id -> { name, [{d, name}] }
for (lon, lat), name1 in summits.items():
    response = requests.get(f"{DBURL}?lon={lon}&lat={lat}")
    if not response.ok:
        print(f"Error: {response.status_code}")
        sys.exit(1)
    data = response.json()
    id, name2, d = data[0]["id"], data[0]["name"], data[0]["d"]
    if id not in points:
        points[id] = {"name": name2, "smts": []}
    points[id]["smts"].append({"d": d, "name": name1})

# output SQL for explored points
for id in points:
    name2 = points[id]["name"]
    smts = sorted(points[id]["smts"], key=lambda x: x["d"])
    i = 0
    for smt in smts:
        d, name1 = smt["d"], smt["name"]
        dd = round(d, 1)
        if i == 0 and d < 100:  # [m]
            print(
                f"INSERT INTO explored VALUES (@rec, NULL, {id}/* {name2} */); -- {name1}, {dd}m"
            )
        else:
            print(f"# {id} {name2} -- {name1}, {dd}m")
        i += 1

# __END__
