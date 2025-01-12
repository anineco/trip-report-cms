#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import json
import math
import os
import sys

from jinja2 import Environment, FileSystemLoader

import config
from utils import iso_period, jp_period, jp_perion_short, jp_datespan

WORKSPACE = os.path.expanduser(config.WORKSPACE)

def round_time(t): # datetime object
    s = 60 * (t.minute % 5) + t.second # seconds from the last 5-minute
    if s > 150 or (s == 150 and t.minute % 2 == 1): # round up
        t += timedelta(minutes=5)
    t -= timedelta(seconds=s)
    return t

def gen_timeline(points): 
    ret = ""
    for i, p in enumerate(points):
        if i > 0:
            ret += ' …'
        ret += p['name']
        if 'ele' in p:
            ret += f"({p['ele']})"
        s = round_time(datetime.strptime(p['timespan'][0], '%Y-%m-%dT%H:%M:%S'))
        e = round_time(datetime.strptime(p['timespan'][1], '%Y-%m-%dT%H:%M:%S'))
        t = s if i > 0 else e
        ret += f" {t.hour}:{t.minute:02d}"
        if i > 0 and i < len(points) - 1:
            if e - s >= timedelta(minutes=10):
                ret += f"〜{e.hour}:{e.minute:02d}"
    return ret

# WGPS84 to Web Mercator projection
def trans(lon, lat):
    wpx = (lon + 180) / 360
    s = math.sin(math.radians(lat))
    wpy = 0.5 - (1 / (4 * math.pi)) * math.log((1 + s) / (1 - s))
    return wpx, wpy

def center(min_lon, min_lat, max_lon, max_lat):
    lon = (min_lon + max_lon) / 2
    lat = (min_lat + max_lat) / 2
    min_wp = trans(min_lon, max_lat) # northwest center
    max_wp = trans(max_lon, min_lat) # southeast center
    wx = 256 * (max_wp[0] - min_wp[0])
    wy = 256 * (max_wp[1] - min_wp[1])
    xw = 580 / wx
    yw = 400 / wy
    w = min(xw, yw)
    zoom = int(math.log(w) / math.log(2))
    if zoom > 16:
        zoom = 16
    return round(lat, 6), round(lon, 6), zoom

# generate routemap URL
def gen_routemap(routemap):
    file = f"{WORKSPACE}/{cid}/{routemap}"
    with open(file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if not 'bbox' in data:
        print(f"Error: {file} does not have bbox.", file=sys.stderr)
        sys.exit(1)
    bbox = data['bbox']
    lat, lon, zoom = center(bbox[0], bbox[1], bbox[2], bbox[3])
    return f"routemap.html?lat={lat}&amp;lon={lon}&amp;zoom={zoom}&amp;url={cid}/{routemap}"

# generate photo pair
def gen_photo(photos):
    ret = []
    for i in range(0,len(photos),2):
        p0 = photos[i]
        p1 = photos[i+1]
        w0, h0 = (270, 180) if p0['width'] > p0['height'] else (180, 270)
        w1, h1 = (270, 180) if p1['width'] > p1['height'] else (180, 270)
        ret.append({
            'base0': p0['hash'], 'w0': w0, 'h0': h0, 'cap0': p0['caption'],
            'base1': p1['hash'], 'w1': w1, 'h1': h1, 'cap1': p1['caption']
        })
    return ret

# generate section
def gen_section(sections):
    ret = []
    for s in sections:
        ret.append({
            'title': s['title'],
            'date': s['date'], # %Y-%m-%d
            'timeline': gen_timeline(s['timeline']),
            'routemap': gen_routemap(s['routemap']),
            'photo': gen_photo(s['photo'])
        })
    return ret

# command line arguments
if len(sys.argv) < 2:
    print(f"Usage: {sys.argv[0]} <cid>", file=sys.stderr)
    sys.exit(1)
cid = sys.argv[1] # Content ID

# load resource json
with open(f"{WORKSPACE}/{cid}.json", 'r', encoding='utf-8') as f:
    resource = json.load(f)

# set template context
s = datetime.strptime(resource['date']['start'], '%Y-%m-%d')
e = datetime.strptime(resource['date']['end'], '%Y-%m-%d')
now = datetime.now()

context = {
    'description': 'なんたら、かんたら。', # This and that
    'title': resource['title'],
    'cid' : resource['cid'],
    'cover': resource['cover']['hash'],
    'period': iso_period(s, e),
    'pubdate': now.strftime('%Y-%m-%d'),
    'date': resource['date'], # {'start': '%Y-%m-%d', 'end': '%Y-%m-%d'}
    'datejp': (lambda x, y: {'start': x, 'end': y})(jp_datespan(s, e)),
    'section': gen_section(resource['section']),
    'lm_year': now.year,
    'year': s.year
}

# Jinja2 template rendering
env = Environment(loader=FileSystemLoader('template'), trim_blocks=True)
template = env.get_template('draft.html')
print(template.render(context))
# __END__
