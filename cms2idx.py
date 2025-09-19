#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sqlite3
from datetime import datetime, timedelta
from os import getenv

from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader

from config import DATA_DIR
from utils import jp_period

load_dotenv(dotenv_path=".env.local")
lm_date = getenv("VITE_LM_DATE")
lm_year = getenv("VITE_LM_YEAR")
lmyy = getenv("VITE_LMYY")

lm = datetime.strptime(lm_date, "%Y-%m-%d")

context = {"lm_date": lm_date, "lm_year": lm_year, "lmyy": lmyy, "items": []}

# read data base
connection = sqlite3.connect(f"file:{DATA_DIR}/metadata.sqlite3?mode=ro", uri=True)
connection.isolation_level = None
cursor = connection.cursor()

sql = """
SELECT cid, start, end, pub, region, title, summary, link, img1x, img2x FROM metadata
ORDER BY start DESC LIMIT 3
"""
cursor.execute(sql)
for cid, start, end, pub, region, title, summary, link, img1x, img2x in cursor.fetchall():
    s = datetime.strptime(start, "%Y-%m-%d")
    e = datetime.strptime(end, "%Y-%m-%d")
    p = datetime.strptime(pub, "%Y-%m-%d")

    context["items"].append(
        {
            "cid": cid,
            "period": jp_period(s, e),
            "region": region,
            "title": title,
            "summary": summary,
            "link": link,
            "img1x": img1x,
            "img2x": img2x,
            "new": lm - p <= timedelta(days=7),
        }
    )

connection.close()

# load mountain category
with open("src/category.json", "r", encoding="utf-8") as f:
    category = json.load(f)["category"]
context["category"] = [{"name": c[4]} for c in category]

# Jinja2 template
env = Environment(loader=FileSystemLoader("template"), trim_blocks=True)
template = env.get_template("index.html")
print(template.render(context))
# __END__
