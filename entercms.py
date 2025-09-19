#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import re
import sqlite3
import sys
from pathlib import Path

from lxml import html

from config import DATA_DIR, DIST_DIR

# open database connection
connection = sqlite3.connect(f"file:{DATA_DIR}/metadata.sqlite3?mode=rwc", uri=True)
connection.isolation_level = None

# create table
sql = """
CREATE TABLE IF NOT EXISTS metadata (
    cid TEXT PRIMARY KEY, -- content id
    start TEXT NOT NULL, -- start date
    end TEXT NOT NULL, -- end date
    pub TEXT, -- publication date
    region TEXT, -- list of prefectures
    title TEXT NOT NULL,
    summary TEXT,
    link TEXT, -- content url
    img1x TEXT, -- cover image
    img2x TEXT
)
"""
connection.execute(sql)

# $ cd DATA_DIR
# $ sqlite3 metadata.sqlite3
# sqlite> CREATE TABLE metadata ……;
# sqlite> .mode csv
# sqlite> .import metadata_no_page.csv metadata
# sqlite> .quit

# parse command line arguments
if len(sys.argv) > 1 and sys.argv[1] == "-d":
    # delete articles
    for arg in sys.argv[2:]:
        if arg.endswith(".html"):
            path = Path(arg)
            cid = path.stem  # 拡張子を除いたファイル名
        else:
            cid = arg
        try:
            connection.execute("DELETE FROM metadata WHERE cid = ?", (cid,))
        except sqlite3.Error as e:
            print(e, file=sys.stderr)
    connection.close()
    sys.exit(0)

# regist articles into metadata database
for arg in sys.argv[1:]:
    if arg.endswith(".html"):
        path = Path(arg)
        cid = path.stem  # 拡張子を除いたファイル名
    else:
        cid = arg
        path = Path(f"{DIST_DIR}/{cid}.html")
    link = f"{cid}.html"

    parser = html.HTMLParser(encoding="utf-8")
    tree = html.parse(str(path), parser=parser)

    elements = tree.xpath("//head/title")
    title = elements[0].text

    elements = tree.xpath('//meta[@name="description"]')
    summary = elements[0].get("content")

    img1x = img2x = ""
    if elements := tree.xpath('//meta[@property="og:image"]'):
        image = elements[0].get("content")
        if match := re.search(r"https://anineco.org/(.*?)/2x/(.*?).jpg", image):
            folder, cover = match.groups()  # NOTE: folder may not match cid
            img1x = f"{folder}/S{cover}.jpg"
            img2x = f"{folder}/2x/S{cover}.jpg"

    script_tags = tree.xpath('//script[@type="application/ld+json"]')
    json_data = json.loads(script_tags[0].text)

    pub = json_data.get("datePublished", "")
    about = json_data["about"]
    start = about["startDate"]
    end = about["endDate"]
    location = about["location"]
    region = " ".join(
        [loc["name"] for loc in location if loc["@type"] == "AdministrativeArea"]
    )

    sql = """
REPLACE INTO metadata (cid, start, end, pub, region, title, summary, link, img1x, img2x)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""
    try:
        connection.execute(
            sql, (cid, start, end, pub, region, title, summary, link, img1x, img2x)
        )
    except sqlite3.Error as e:
        print(e, file=sys.stderr)

connection.close()
# __END__
