#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
import sqlite3
import sys

from jinja2 import Environment, FileSystemLoader

from utils import jp_period

# command line arguments
rss_version = sys.argv[1] if len(sys.argv) == 2 else '1.0'
if not rss_version in ['1.0', '2.0']:
    print(f"Usage: {sys.argv[0]} [1.0|2.0]", file=sys.stderr)
    sys.exit(1)

# context
context = {
    'items': []
}

# open database connection
connection = sqlite3.connect('data/metadata.sqlite3')
cursor = connection.cursor()

cursor.execute('''
SELECT start, end, pub, title, summary, link, img1x, img2x FROM metadata
ORDER BY start DESC LIMIT 15
''')
for start, end, pub, title, summary, link, img1x, img2x in cursor.fetchall():
    s = datetime.strptime(start, '%Y-%m-%d')
    e = datetime.strptime(end, '%Y-%m-%d')

    context['items'].append({
        'period': jp_period(s, e),
        'pub': pub,
        'title': title,
        'summary': summary,
        'link': link,
        'img1x': img1x,
        'img2x': img2x
    })

connection.close()

# Jinja2 template engine
env = Environment(loader=FileSystemLoader('template'), trim_blocks=True)
template = env.get_template('rss20.xml' if rss_version == '2.0' else 'rss10.xml')
print(template.render(context))
# __END__
