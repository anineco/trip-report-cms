#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import os
import sqlite3

from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader

from config import DATA_DIR
from utils import jp_period

load_dotenv(dotenv_path='.env.local')
lm_date = os.getenv('VITE_LM_DATE')
lm_year = os.getenv('VITE_LM_YEAR')
lmyy = os.getenv('VITE_LMYY')

lm = datetime.strptime(lm_date, '%Y-%m-%d')

context = {
    'lm_date': lm_date,
    'lm_year': lm_year,
    'lmyy': lmyy,
    'items': []
}

# read data base
connection = sqlite3.connect(f'{DATA_DIR}/metadata.sqlite3')
cursor = connection.cursor()

cursor.execute('''
SELECT cid, start, end, pub, title, summary, link, img1x, img2x FROM metadata
ORDER BY start DESC LIMIT 3
''')
for cid, start, end, pub, title, summary, link, img1x, img2x in cursor.fetchall():
    s = datetime.strptime(start, '%Y-%m-%d')
    e = datetime.strptime(end, '%Y-%m-%d')
    p = datetime.strptime(pub, '%Y-%m-%d')

    context['items'].append({
        'cid': cid,
        'period': jp_period(s, e),
        'title': title,
        'summary': summary,
        'link': link,
        'img1x': img1x,
        'img2x': img2x,
        'new': lm - p <= timedelta(days=7)
    })

connection.close()

# Jinja2 template
env = Environment(loader=FileSystemLoader('template'), trim_blocks=True)
template = env.get_template('index.html')
print(template.render(context))
# __END__
