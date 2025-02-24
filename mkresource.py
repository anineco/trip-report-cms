#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob
import json
import math
import os.path
import re
import string
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

from exiftool import ExifToolHelper

from config import GPX_DIR, IMG_DIR, WORK_DIR
from const import namespaces

ICON_SUMMIT = "952015"  # kashmir3d:icon

# command line arguments
if len(sys.argv) != 3:
    print(f"Usage: {sys.argv[0]} <cid> <title>", file=sys.stderr)
    sys.exit(1)

cid = sys.argv[1]  # Content ID
title = sys.argv[2]  # Title

resource = {"cid": cid, "title": title, "section": []}


# extract sequetial number (4 digits) from photo file name
def extract_number(file):
    base = os.path.basename(file)
    patterns = [
        r"^.{4}(\d{4})\.",  # fixed 4 characters + 4 digits
        r"(\d{4})\d{5}\.",  # %y%m%d%H%M%S + 3 digits
        r"\d{2}(\d{4})\."  # arbitrary string + 6 digits
    ]
    for pattern in patterns:
        if match := re.search(pattern, base):
            return match.group(1)

    print(f"Photo filename with unknown pattern: {file}", file=sys.stderr)
    sys.exit(1)


# generate a section containing photos sectioning by the time of waypoints
def read_section(files):  # gpx files
    wpts = []
    trkpts_unsorted = []
    for file in files:
        root = ET.parse(file).getroot()
        for wpt in root.findall(".//wpt", namespaces):
            item = {
                "lat": wpt.get("lat"),
                "lon": wpt.get("lon"),
                "icon": wpt.find(".//kashmir3d:icon", namespaces).text,
                "name": wpt.find("name", namespaces).text,
            }
            if (
                item["icon"] == ICON_SUMMIT
                and (cmt := wpt.find("cmt", namespaces)) is not None
            ):
                for row in cmt.text.split(","):
                    key, value = row.split("=")
                    if key == "標高":  # 'elevation'
                        item["ele"] = value
                        break
            wpts.append(item)

        for trk in root.findall(".//trk", namespaces):
            for trkseg in trk.findall("trkseg", namespaces):
                for trkpt in trkseg.findall("trkpt", namespaces):
                    time = trkpt.find("time", namespaces).text
                    t = datetime.strptime(
                        time, "%Y-%m-%dT%H:%M:%SZ"
                    )  # UTC aka Zulu time
                    t += timedelta(hours=9)  # translate to JST
                    item = {
                        "lat": trkpt.get("lat"),
                        "lon": trkpt.get("lon"),
                        "time": t.strftime("%Y-%m-%dT%H:%M:%S"),
                    }
                    trkpts_unsorted.append(item)

    trkpts = sorted(trkpts_unsorted, key=lambda x: x["time"])

    # for each trackpoint, find the nearest waypoint
    for trkpt in trkpts:
        lat = float(trkpt["lat"])
        lon = float(trkpt["lon"])
        dmin = float("inf")
        n = -1
        for i, wpt in enumerate(wpts):
            # NOTE: compute rough estimate of distance in degree
            d = math.hypot(float(wpt["lat"]) - lat, float(wpt["lon"]) - lon)
            if dmin > d:
                dmin = d
                n = i
        trkpt["d"] = dmin
        trkpt["n"] = n

    m = len(trkpts) - 1

    for i, trkpt in enumerate(trkpts):
        p0 = trkpts[i - 1 if i > 0 else 0]
        p1 = trkpt
        p2 = trkpts[i + 1 if i < m else m]
        nearest = -1
        if p0["n"] == p1["n"] and p2["n"] == p1["n"]:
            if min(p0["d"], p1["d"], p2["d"]) < 0.0004:  # NOTE: about 44m:
                nearest = p1["n"]
        trkpt["nearest"] = nearest

    # create timeline
    timeline = []
    summits = []

    for i, trkpt in enumerate(trkpts):
        n1 = trkpt["nearest"]
        if n1 < 0:
            continue
        n0 = trkpts[i - 1]["nearest"] if i > 0 else -1
        n2 = trkpts[i + 1]["nearest"] if i < m else -1
        if n0 != n1:
            start = trkpt["time"]
        if n1 != n2:
            end = trkpt["time"]
            q = wpts[n1]
            item = {"name": q["name"], "timespan": [start, end]}
            if q["icon"] == ICON_SUMMIT and "ele" in q:
                item["ele"] = q["ele"]
                summits.append(q["name"])
            timeline.append(item)

    t = timeline[0]["timespan"][0].split("T")  # start date, time
    return {
        "title": title or "〜".join(summits),
        "date": t[0],
        "timespan": [timeline[0]["timespan"][1], timeline[-1]["timespan"][0]],
        "timeline": timeline,
        "photo": [],
    }


# set source gpx files and file name of routemap
for track in glob.glob(f"{GPX_DIR}/{cid}/trk*.gpx"):
    if match := re.search(r".*/trk(\d?)\.gpx", track):
        c = match.group(1)
        files = glob.glob(f"{GPX_DIR}/{cid}/???{c}.gpx")  # rte, trk, wpt
        section = read_section(files)
        section["gpx"] = files
        section["routemap"] = f"routemap{c}.geojson"
        resource["section"].append(section)

# set start and end date to resource
if len(resource["section"]) > 0:
    resource["date"] = {
        "start": resource["section"][0]["date"],
        "end": resource["section"][-1]["date"],
    }
else:
    print(f"No GPX files found: {cid}", file=sys.stderr)
    match = re.search(r"(\d\d)(\d\d)(\d\d)", cid)
    ymd = "20{}-{}-{}".format(*match.groups())
    resource["date"] = {"start": ymd, "end": ymd}
    resource["section"] = {"timespan": [f"{ymd}T00:00:00", f"{ymd}T23:59:59"]}

# set cover image to resource
hash = set()
covers = glob.glob(f"{IMG_DIR}/{cid}/cover/*")
if len(covers) < 1:
    print(f"No cover image found: {cid}", file=sys.stderr)
    sys.exit(1)
file = covers[0]
key = extract_number(file) # extract sequential part of cover file name
resource["cover"] = {"file": file, "hash": key}
hash.add(key)

# load photo's metadata
photos_unsorted = []
# NOTE: photo file name should be "arbitrary string + at least 4 digits + extension"
for file in glob.glob(f"{IMG_DIR}/{cid}/*[0-9][0-9][0-9][0-9].*"):
    item = {"file": file}
    key = extract_number(file) # extract sequential part of photo file name
    if key in hash and key != resource["cover"]["hash"]:
        for c in string.ascii_lowercase:
            if (keyc := key + c) not in hash:
                hash.add(keyc)
                item["hash"] = keyc
                break
        if "hash" not in item:
            print(f"Too many photos: {cid}", file=sys.stderr)
            sys.exit(1)
    else:
        hash.add(key)
        item["hash"] = key

    with ExifToolHelper() as et:
        try:
            info = et.get_metadata(file)[0]
            date_time_original = info["EXIF:DateTimeOriginal"]
            t = datetime.strptime(date_time_original, "%Y:%m:%d %H:%M:%S")
            item["time"] = t.strftime("%Y-%m-%dT%H:%M:%S")
            item["width"] = info["File:ImageWidth"]
            item["height"] = info["File:ImageHeight"]
            item["caption"] = info["XMP:Title"]
        except KeyError:
            print(f"KeyError: {file}", file=sys.stderr)
        except ValueError:
            print(f"ValueError: {file}", file=sys.stderr)

    photos_unsorted.append(item)

photos = sorted(photos_unsorted, key=lambda x: x["time"])

# assign photos to sections by time
n = len(resource["section"]) - 1  # index of the last section
for photo in photos:
    t = photo["time"]
    for i, section in enumerate(resource["section"]):
        if i == n or t < section["timespan"][1]:
            section["photo"].append(photo)
            break
        # calculate midtime between current and next section
        t1 = datetime.strptime(section["timespan"][1], "%Y-%m-%dT%H:%M:%S")
        t2 = datetime.strptime(
            resource["section"][i + 1]["timespan"][0], "%Y-%m-%dT%H:%M:%S"
        )
        tc = t1 + (t2 - t1) / 2
        if t < tc.strftime("%Y-%m-%dT%H:%M:%S"):
            section["photo"].append(photo)
            break

# prepare WORK_DIR
folder = os.path.join(WORK_DIR, cid)
if not os.path.exists(folder):
    os.makedirs(folder)

# write resource.json
file = os.path.join(WORK_DIR, f"{cid}.json")
with open(file, "w", encoding="utf-8") as f:
    f.write(json.dumps(resource, ensure_ascii=False, indent=2))

# __END__
