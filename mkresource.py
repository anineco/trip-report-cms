#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import glob
import json
import math
import os
import re
import string
import sys
import xml.etree.ElementTree as ET

from exiftool import ExifToolHelper

import config

WORKSPACE = os.path.expanduser(config.WORKSPACE)
MATERIAL_GPX = os.path.expanduser(config.MATERIAL_GPX)
MATERIAL_IMG = os.path.expanduser(config.MATERIAL_IMG)

ICON_SUMMIT = '952015' # kashmir3d:icon

# command line arguments
if len(sys.argv) < 3:
    print(f"Usage: {sys.argv[0]} <cid> <title>", file=sys.stderr)
    sys.exit(1)

cid = sys.argv[1] # Content ID
title = sys.argv[2] # Title

resource = { 'cid': cid, 'title': title, 'section': [] }

namespaces = {
    '': 'http://www.topografix.com/GPX/1/1',
    'kashmir3d': 'http://www.kashmir3d.com/namespace/kashmir3d'
}

def read_section(files): # read GPX files
    wpts = []
    trkpts_unsorted = []
    for file in files:
        root = ET.parse(file).getroot()
        for wpt in root.findall(".//wpt", namespaces):
            item = {
                'lat': wpt.get('lat'),
                'lon': wpt.get('lon'),
                'icon': wpt.find(".//kashmir3d:icon", namespaces).text,
                'name': wpt.find("name", namespaces).text
            }
            if item['icon'] == ICON_SUMMIT:
                for cmt in wpt.findall("cmt", namespaces):
                    for row in cmt.text.split(','):
                        key, value = row.split('=')
                        if key == '標高': # elevation
                            item['ele'] = value
            wpts.append(item)

        for trk in root.findall(".//trk", namespaces):
            for trkseg in trk.findall("trkseg", namespaces):
                for trkpt in trkseg.findall("trkpt", namespaces):
                    time = trkpt.find("time", namespaces).text
                    t = datetime.strptime(time, "%Y-%m-%dT%H:%M:%SZ") # UTC
                    t += timedelta(hours=9) # translate to JST
                    item = {
                        'lat': trkpt.get('lat'),
                        'lon': trkpt.get('lon'),
                        'time': t.strftime("%Y-%m-%dT%H:%M:%S")
                    }
                    trkpts_unsorted.append(item)

    trkpts = sorted(trkpts_unsorted, key=lambda x: x['time'])

    # for each trackpoint, find the nearest waypoint
    for trkpt in trkpts:
        lat = float(trkpt['lat'])
        lon = float(trkpt['lon'])
        dmin = float('inf')
        n = -1
        for i, wpt in enumerate(wpts):
            # NOTE: compute rough estimate of distance in degree
            d = math.hypot(float(wpt['lat']) - lat, float(wpt['lon']) - lon)
            if dmin > d:
                dmin = d
                n = i
        trkpt['d'] = dmin
        trkpt['n'] = n

    m = len(trkpts) - 1

    for i, trkpt in enumerate(trkpts):
        p0 = trkpts[i - 1 if i > 0 else 0]
        p1 = trkpt
        p2 = trkpts[i + 1 if i < m else m]
        nearest = -1
        if p0['n'] == p1['n'] and p2['n'] == p1['n']:
            if min(p0['d'], p1['d'], p2['d']) < 0.0004: # NOTE: about 44m:
                nearest = p1['n']
        trkpt['nearest'] = nearest

    # create timeline
    timeline = []
    summits = []

    for i, trkpt in enumerate(trkpts):
        n1 = trkpt['nearest']
        if n1 < 0:
            continue
        n0 = -1 if i < 1 else trkpts[i - 1]['nearest']
        n2 = -1 if i > m - 1 else trkpts[i + 1]['nearest']
        if n0 != n1:
            start = trkpt['time']
        if n1 != n2:
            end = trkpt['time']
            q = wpts[n1]
            item = {
                'name': q['name'],
                'timespan': [start, end]
            }
            if q['icon'] == ICON_SUMMIT:
                item['ele'] = q['ele']
                summits.append(q['name'])
            timeline.append(item)

    t = timeline[0]['timespan'][0].split('T')
    return {
        'title': title or '〜'.join(summits),
        'date': t[0],
        'timespan': [ timeline[0]['timespan'][1], timeline[-1]['timespan'][0] ],
        'timeline': timeline,
        'photo': []
    }

# set source GPX files and file name of routemap
for track in glob.glob(f"{MATERIAL_GPX}/{cid}/trk*.gpx"):
    if match := re.search(r".*/trk(\d?)\.gpx", track):
        c = match.group(1)
        files = glob.glob(f"{MATERIAL_GPX}/{cid}/???{c}.gpx") # rte, trk, wpt
        section = read_section(files)
        section['gpx'] = files
        section['routemap'] = f"routemap{c}.geojson"
        resource['section'].append(section)

# set start and end date to resource
if 'section' in resource:
    resource['date'] = {
        'start': resource['section'][0]['date'],
        'end': resource['section'][-1]['date']
    }
else:
    print(f"No GPX files found: {cid}", file=sys.stderr)
    match = re.search(r'(\d\d)(\d\d)(\d\d)', cid)
    ymd = '20{}-{}-{}'.format(*match.groups())
    resource['date'] = { 'start': ymd, 'end': ymd }
    resource['section'] = { 'timespan': [ f'{ymd}T00:00:00', f'{ymd}T23:59:59' ] }

# set cover image to resource
hash = {}
covers = glob.glob(f"{MATERIAL_IMG}/{cid}/cover/*")
if len(covers) == 0:
    print(f"No cover image found: {cid}", file=sys.stderr)
    sys.exit(1)
file = covers[0]
base = os.path.basename(file)
match = re.search(r'^.*(\d{4})\..*$', base)
if not match:
    print(f"Invalid file name: {base}", file=sys.stderr)
    sys.exit(1)
key = match.group(1)
resource['cover'] = { 'file': file, 'hash': key }
hash['key'] = 1

# load photo's metadata
photos_unsorted = []
for file in glob.glob(f"{MATERIAL_IMG}/{cid}/*[0-9][0-9][0-9][0-9].*"):
    item = { 'file': file }
    base = os.path.basename(file)
    match = re.search(r'^.*(\d{4})\..*$', base)
    if not match:
        print(f"Invalid file name: {base}", file=sys.stderr)
        sys.exit(1)
    key = match.group(1)
    if key in hash and key != resource['cover']['hash']:
        for c in string.ascii_lowercase:
            if (keyc := key + c) not in hash:
                hash[keyc] = 1
                item['hash'] = keyc
                break
        if 'hash' not in item:
            print(f"Too many photos: {cid}", file=sys.stderr)
            sys.exit(1)
    else:
        hash[key] = 1
        item['hash'] = key

    with ExifToolHelper() as et:
        try:
            info = et.get_metadata(file)[0]
            date_time_original = info['EXIF:DateTimeOriginal']
            t = datetime.strptime(date_time_original, "%Y:%m:%d %H:%M:%S")
            item['time'] = t.strftime("%Y-%m-%dT%H:%M:%S")
            item['width'] = info['File:ImageWidth']
            item['height'] = info['File:ImageHeight']
            item['caption'] = info['XMP:Title']
        except KeyError:
            print(f"KeyError: {file}", file=sys.stderr)
        except ValueError:
            print(f"ValueError: {file}", file=sys.stderr)

    photos_unsorted.append(item)

photos = sorted(photos_unsorted, key=lambda x: x['time'])

# assign photos to sections by time
n = len(resource['section']) - 1 # index of the last section
for photo in photos:
    t = photo['time']
    for i, section in enumerate(resource['section']):
        if i == n or t < section['timespan'][1]:
            section['photo'].append(photo)
            break
        t1 = datetime.strptime(section['timespan'][1], "%Y-%m-%dT%H:%M:%S")
        t2 = datetime.strptime(resource['section'][i + 1]['timespan'][0], "%Y-%m-%dT%H:%M:%S")
        tc = t1 + (t2 - t1) / 2
        if t < tc.strftime("%Y-%m-%dT%H:%M:%S"):
            section['photo'].append(photo)
            break

# prepare workspace
folder = f"{WORKSPACE}/{cid}"
if not os.path.exists(folder):
    os.makedirs(folder)

# write resource.json
file = f"{WORKSPACE}/{cid}.json"
with open(file, 'w') as f:
    f.write(json.dumps(resource, ensure_ascii=False, indent=2))

# __END__
