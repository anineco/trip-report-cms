#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
import os
import sqlite3
import sys

from jinja2 import Environment, FileSystemLoader

from utils import jp_period_short

if len(sys.argv) < 2:
    print(f"Usage: {sys.argv[0]} <year>", file=sys.stderr)
    sys.exit(1)
year = sys.argv[1]

context = {
    'year': year,
    'items': []
}

# read data base
connection = sqlite3.connect('metadata.sqlite3')
cursor = connection.cursor()

lm_year = 2022 # NOTE: backward compatibility
cursor.execute('''
SELECT cid, start, end, pub, title, summary, link, img1x, img2x FROM metadata
WHERE start LIKE ? ORDER BY start
''', (f"{year}%",))
for cid, start, end, pub, title, summary, link, img1x, img2x in cursor.fetchall():
    if pub:
        p = datetime.strptime(pub, "%Y-%m-%d")
        if lm_year < p.year:
            lm_year = p.year
    s = datetime.strptime(start, '%Y-%m-%d')
    e = datetime.strptime(end, '%Y-%m-%d')

    context['items'].append({
        'cid': cid,
        'period': jp_period_short(s, e),
        'title': title,
        'summary': summary,
        'link': link,
        'img1x': img1x,
        'img2x': img2x
    })

context['lm_year'] = lm_year
connection.close()

# Jinja2 template
env = Environment(loader=FileSystemLoader('template'), trim_blocks=True)
template = env.get_template('ch.html')
print(template.render(context))
# __END__

