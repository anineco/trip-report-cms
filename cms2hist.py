#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
import csv
import sqlite3
import sys

from jinja2 import Environment, FileSystemLoader

from config import DATA_DIR
from utils import iso_period

if len(sys.argv) != 2:
    print(f"Usage: {sys.argv[0]} <year>", file=sys.stderr)
    sys.exit(1)
year = sys.argv[1]

data = {}  # NOTE: data = { pub => [content, ...] }

# read data base
connection = sqlite3.connect(f"{DATA_DIR}/metadata.sqlite3")
cursor = connection.cursor()

sql = """
SELECT cid, start, end, pub, title, link FROM metadata
WHERE pub IS NOT NULL AND pub LIKE ? ORDER BY pub, start DESC
"""
cursor.execute(sql, (f"{year}%",))
for cid, start, end, pub, title, link in cursor.fetchall():
    s = datetime.strptime(start, "%Y-%m-%d")
    e = datetime.strptime(end, "%Y-%m-%d")
    period = iso_period(s, e)
    content = f'{period} <a href="{link}">{title}</a> の山行記録を追加。'  # NOTE: customize content
    data.setdefault(pub, []).append(content)

connection.close()

# read changelog
with open(f"{DATA_DIR}/changelog.csv", "r", encoding="utf-8") as f:
    for pub, content in csv.reader(f):
        if pub.startswith(year):
            data.setdefault(pub, []).append(content)

context = {"year": year, "lm_year": year, "items": []}

for key, value in sorted(data.items(), reverse=True):
    content = "<br>".join(value)
    context["items"].append({"pub": key, "content": content.replace("<br>", "<br>\n")})

# Jinja2 template
env = Environment(loader=FileSystemLoader("template"), trim_blocks=True)
template = env.get_template("hist.html")
print(template.render(context))
# __END__
