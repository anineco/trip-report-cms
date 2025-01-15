#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import subprocess
import sys
import lxml.etree as ET

from config import WORK_DIR
import togeojson

if len(sys.argv) != 2:
    print(f'Usage: {sys.argv[0]} <cid>', file=sys.stderr)
    sys.exit(1)

cid = sys.argv[1] # Content ID

# read json file
with open(f'{WORK_DIR}/{cid}.json', 'r') as f:
    resource = json.load(f)

xt_error = 0.005 # cross track error in km
line_size = 3
line_style = '13' # dot
opacity = 0.5

for s in resource['section']:
    if not 'routemap' in s:
        continue
    routemap = s['routemap']

    cmd = [ 'gpsbabel', '-r', '-t', '-i', 'gpx' ]
    for gpx in s['gpx']:
        cmd.extend([ '-f', gpx ])
    cmd.extend([ '-x', f'simplify,error={xt_error}', '-o', 'gpx,gpxver=1.1', '-F', '-' ])

    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        xml = process.stdout.read()
    except subprocess.CalledProcessError as e:
        print(f'Error: {e}', file=sys.stderr)
        sys.exit(1)

    root = ET.fromstring(xml)
    
    geojson = togeojson.togeojson(root, line_size, line_style, opacity)
    with open(f'{WORK_DIR}/{cid}/{routemap}', 'w', encoding='utf-8') as f:
        f.write(json.dumps(geojson, ensure_ascii=False, separators=(',', ':')))
        f.write('\n')

# __END__
    