#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sqlite3
import sys
from pathlib import Path

from config import DATA_DIR, WORK_DIR

ICON_SUMMIT = "symbols/Summit.png"
DBURL = "https://map.jpn.org/share/mt.php"

# command line arguments
if len(sys.argv) != 2:
    print(f"Usage: {sys.argv[0]} <cid>", file=sys.stderr)
    sys.exit(1)
cid = sys.argv[1]  # Content ID

# check if the JSON file exists
json_path = Path(f"{WORK_DIR}/{cid}.json")
if not json_path.exists():
    print(f"Error: {json_path} not found", file=sys.stderr)
    sys.exit(1)

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

# output explored summits
with json_path.open("r", encoding="utf-8") as f:
    root = json.load(f)
    for summit in root["summits"]:
        id = summit["id"]
        name = summit["name"]
        distance = summit["distance"]
        print(f"INSERT INTO explored VALUES (@rec, NULL, {id}); -- {name} {distance:.1f}m")

# __END__
