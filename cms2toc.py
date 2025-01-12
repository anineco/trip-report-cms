#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
import os
import sqlite3

from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader

from utils import iso_period

load_dotenv(dotenv_path='.env.local')
year = os.getenv('VITE_YEAR')
lm_date = os.getenv('VITE_LM_DATE')
lm_year = os.getenv('VITE_LM_YEAR')

context = {
    'lm_date': lm_date,
    'lm_year': lm_year,
    'hist': [],
    'chron': []
}

# 年別更新履歴

for year in range(int(lm_year), 2003, -1):
    context['hist'].append({
        'year': year,
        'url': 'hist{:02d}.html'.format(year % 100)
    })

# 年別山行記録

connection = sqlite3.connect('metadata.sqlite3')
cursor = connection.cursor()

for year in range(int(lm_year), 1997, -1):
    data = [] # NOTE: data = [ {period, title, link}, ... ]
    cursor.execute('''
    SELECT start, end, title, link FROM metadata
    WHERE start LIKE ? ORDER BY start
    ''' , (f"{year}%",))
    for start, end, title, link in cursor.fetchall():
        s = datetime.strptime(start, '%Y-%m-%d')
        e = datetime.strptime(end, '%Y-%m-%d')

        data.append({
            'period': iso_period(s, e),
            'title': title,
            'link': link
        })

    context['chron'].append({
        'year': year,
        'url': f'ch{year}.html',
        'record': data
    })

connection.close()

# Jinja2 template
env = Environment(loader=FileSystemLoader('template'), trim_blocks=True)
template = env.get_template('toc.html')
print(template.render(context))
# __END__
