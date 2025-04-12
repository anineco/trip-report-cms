#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import sys
from datetime import datetime

from jinja2 import Environment, FileSystemLoader

from config import DATA_DIR
from utils import jp_period_short

if len(sys.argv) != 2:
    print(f"Usage: {sys.argv[0]} <year>", file=sys.stderr)
    sys.exit(1)
year = sys.argv[1]

context = {"year": year, "items": []}

# read data base
connection = sqlite3.connect(f"file:{DATA_DIR}/metadata.sqlite3?mode=ro", uri=True)
connection.isolation_level = None
cursor = connection.cursor()

lm_year = 2022  # NOTE: backward compatibility
sql = """
SELECT cid, start, end, pub, title, summary, link, img1x, img2x FROM metadata
WHERE start LIKE ? ORDER BY start
"""
cursor.execute(sql, (f"{year}%",))
for cid, start, end, pub, title, summary, link, img1x, img2x in cursor.fetchall():
    if pub:
        p = datetime.strptime(pub, "%Y-%m-%d")
        if lm_year < p.year:
            lm_year = p.year
    s = datetime.strptime(start, "%Y-%m-%d")
    e = datetime.strptime(end, "%Y-%m-%d")

    context["items"].append(
        {
            "cid": cid,
            "period": jp_period_short(s, e),
            "title": title,
            "summary": summary,
            "link": link,
            "img1x": img1x,
            "img2x": img2x,
        }
    )

context["lm_year"] = lm_year
connection.close()

# Jinja2 template
env = Environment(loader=FileSystemLoader("template"), trim_blocks=True)
template = env.get_template("ch.html")
print(template.render(context))
# __END__
