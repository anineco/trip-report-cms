#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path
import re
import sqlite3
import sys

from config import DATA_DIR, DIST_DIR

# open database connection
connection = sqlite3.connect(f"{DATA_DIR}/metadata.sqlite3")
cursor = connection.cursor()

# create table
sql = """
CREATE TABLE IF NOT EXISTS metadata (
    cid TEXT PRIMARY KEY, -- content id
    start TEXT NOT NULL, -- start date
    end TEXT NOT NULL, -- end date
    pub TEXT, -- publication date
    title TEXT NOT NULL,
    summary TEXT,
    link TEXT, -- content url
    img1x TEXT, -- cover image
    img2x TEXT
)
"""
cursor.execute(sql)
connection.commit()

# $ cd DATA_DIR
# $ sqlite3 metadata.sqlite3
# sqlite> .mode csv
# sqlite> .import metadata_no_page.csv metadata
# sqlite> .quit

# parse command line arguments
if len(sys.argv) > 1 and sys.argv[1] == "-d":
    # delete articles
    for arg in sys.argv[2:]:
        if arg.endwith(".html"):
            cid = os.path.splitext(os.path.basename(arg))[0]
        else:
            cid = arg
        cursor.execute("DELETE FROM metadata WHERE cid = ?", (cid,))

    connection.commit()
    connection.close()
    sys.exit(0)

# insert reports
for arg in sys.argv[1:]:
    if arg.endswith(".html"):
        filename = arg
        cid = os.path.splitext(os.path.basename(arg))[0]
    else:
        cid = arg
        filename = f"${DIST_DIR}/{cid}.html"
    link = f"{cid}.html"
    pub = summary = img1x = img2x = ""
    f = open(filename, "r", encoding="utf-8")
    for line in f:
        if match := re.search(r'"temporalCoverage":"(.*?)"', line):
            datespan = match.group(1).split("/")
            start = datespan[0]
            if len(datespan) > 1:
                e = datespan[1].split("-")
                y, m, d = start.split("-")
                if len(e) == 3:
                    y, m, d = e
                elif len(e) == 2:
                    m, d = e
                else:
                    d = e[0]
                end = f"{y}-{m}-{d}"
            else:
                end = start
        elif match := re.search(r"^<title>(.*?)</title>", line):
            title = match.group(1)
        elif match := re.search(r'^<meta name="description" content="(.*?)">', line):
            summary = match.group(1)
        elif match := re.search(
            r'^<meta property="og:image" content="https://anineco.org/(.*?)/2x/(.*?).jpg">',
            line,
        ):
            folder, cover = match.groups()
            img1x = f"{folder}/S{cover}.jpg"
            img2x = f"{folder}/2x/S{cover}.jpg"
        elif match := re.search(r'"datePublished":"(.*?)"', line):
            pub = match.group(1)

    f.close()
    sql = """
REPLACE INTO metadata (cid, start, end, pub, title, summary, link, img1x, img2x)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
"""
    cursor.execute(sql, (cid, start, end, pub, title, summary, link, img1x, img2x))
    connection.commit()

connection.close()
# __END__
