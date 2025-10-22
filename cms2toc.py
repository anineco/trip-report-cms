#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sqlite3
from datetime import datetime
from os import getenv

from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader

from config import DATA_DIR
from utils import iso_period

load_dotenv(dotenv_path=".env.local")
year = getenv("VITE_YEAR")
lm_date = getenv("VITE_LM_DATE")
lm_year = getenv("VITE_LM_YEAR")

context = {"lm_date": lm_date, "lm_year": lm_year, "hist": [], "chron": []}

# 年別更新履歴 (Update History by Year)

for year in range(int(lm_year), 2003, -1):  # CAUTION: the first year is hard-coded
    context["hist"].append({"year": year, "url": "hist{:02d}.html".format(year % 100)})

# 年別山行記録 (Trip Records by Year)

connection = sqlite3.connect(f"file:{DATA_DIR}/metadata.sqlite3?mode=ro", uri=True)
connection.isolation_level = None
cursor = connection.cursor()

for year in range(int(lm_year), 1997, -1):  # CAUTION: the first year is hard-coded
    data = []  # NOTE: data = [ {period, title, link}, ... ]
    sql = """
SELECT start, end, title, link FROM metadata
WHERE start LIKE ? ORDER BY start
"""
    cursor.execute(sql, (f"{year}%",))
    for start, end, title, link in cursor.fetchall():
        s = datetime.strptime(start, "%Y-%m-%d")
        e = datetime.strptime(end, "%Y-%m-%d")
        data.append({"period": iso_period(s, e), "title": title, "link": link})
    context["chron"].append({"year": year, "url": f"ch{year}.html", "record": data})

connection.close()

# 地図から選択 (Select from Map)

with open("src/category.json", "r", encoding="utf-8") as f:
    category = json.load(f)["category"]
context["category"] = [{"name": c[4]} for c in category]

# Jinja2 template
env = Environment(loader=FileSystemLoader("template"), trim_blocks=True)
template = env.get_template("toc.html.j2")
print(template.render(context))
# __END__
