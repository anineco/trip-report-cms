#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import glob
import json
import math
import os.path
import re
import string
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

import requests
from exiftool import ExifToolHelper

from config import GPX_DIR, IMG_DIR, WORK_DIR, SYM_SUMMIT, DBURL
from const import namespaces

# コマンドライン引数のチェック
parser = argparse.ArgumentParser(description="Create resource JSON")
parser.add_argument("cid", help="Content ID")
parser.add_argument("title", help="Title")
args = parser.parse_args()

cid = args.cid
title = args.title

resource = {
    "cid": cid,
    "title": title,
}


# extract sequetial number (4 digits) from photo file name
def extract_number(file):
    base = os.path.basename(file)
    patterns = [
        r"^.{4}(\d{4})\.",  # fixed 4 characters + 4 digits
        r"(\d{4})\d{5}\.",  # %y%m%d%H%M%S + 3 digits
        r"\d{2}(\d{4})\.",  # arbitrary string + 6 digits
    ]
    for pattern in patterns:
        if match := re.search(pattern, base):
            return match.group(1)

    print(f"Photo filename with unknown pattern: {file}", file=sys.stderr)
    sys.exit(1)


# cache of summits and prefectures obtained from DB
summits = {}  # id -> { name, [{distance, wptname}] }
prefectures = {}  # code -> { code, name, qid }


def get_point(lon, lat, wptname):
    response = requests.get(f"{DBURL}?lon={lon}&lat={lat}")
    if not response.ok:
        print(f"Error: {response.status_code}", file=sys.stderr)
        sys.exit(1)
    data = response.json()
    if data is None:
        print(f"Warning: no summit found ({lon}, {lat}) {wptname}", file=sys.stderr)
        return
    id, name, distance = data["id"], data["name"], data["distance"]
    print(f"Summit: {id} {name} (distance: {distance}m) {wptname}", file=sys.stderr)
    if id not in summits:
        summits[id] = data  # { id, name, ... }
        summits[id]["wpts"] = []
    summits[id]["wpts"].append({"distance": distance, "name": wptname})
    for item in data["prefectures"]:
        code = item["code"]
        prefectures[code] = item  # {code, name, qid}


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
                "sym": wpt.find("sym", namespaces).text,
                "name": wpt.find("name", namespaces).text,
            }
            if (
                item["sym"] == SYM_SUMMIT
                and (cmt := wpt.find("cmt", namespaces)) is not None
            ):
                get_point(item["lon"], item["lat"], item["name"])
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
            # compute rough estimate of distance in degree
            d = math.hypot(float(wpt["lat"]) - lat, float(wpt["lon"]) - lon)
            if dmin > d:
                dmin = d
                n = i
        trkpt["d"] = dmin
        trkpt["n"] = n

    m = len(trkpts) - 1  # index of the last trackpoint

    # consider 3 neighboring points to avoid GPS jitter
    for i, trkpt in enumerate(trkpts):
        p0 = trkpts[i - 1 if i > 0 else 0]
        p1 = trkpt
        p2 = trkpts[i + 1 if i < m else m]
        nearest = -1
        if (
            p0["n"] == p1["n"] == p2["n"]
            and min(p0["d"], p1["d"], p2["d"]) < 0.0004  # NOTE: about 44m
        ):
            nearest = p1["n"]
        trkpt["nearest"] = nearest

    # create timeline
    section = []
    timeline = []
    summit_names = []

    for i, trkpt in enumerate(trkpts):
        if (n1 := trkpt["nearest"]) < 0:
            continue
        n0 = trkpts[i - 1]["nearest"] if i > 0 else -1
        n2 = trkpts[i + 1]["nearest"] if i < m else -1
        if n0 != n1:
            start = trkpt["time"]
            start_date = start.split("T")[0]
        if n1 == n2:
            continue
        q = wpts[n1]
        end = trkpt["time"]
        end_date = end.split("T")[0]
        if start_date != end_date:
            # crossing midnight
            # temporarily set end time to 23:59:59 of start date
            end_tmp = end
            end = f"{start_date}T23:59:59"
        item = {"name": q["name"], "timespan": [start, end]}
        if q["sym"] == SYM_SUMMIT and "ele" in q:
            item["ele"] = q["ele"]
            summit_names.append(q["name"])
        timeline.append(item)
        if start_date == end_date:
            continue
        # sectioning at midnight
        t = timeline[0]["timespan"][0].split("T")  # start date, time
        section.append(
            {
                "title": "⚠️" + "〜".join(summit_names),
                "date": t[0],
                "timespan": [timeline[0]["timespan"][1], timeline[-1]["timespan"][0]],
                "timeline": timeline,
                "photo": [],
            }
        )
        # reset for new section
        timeline.clear()
        summit_names.clear()
        start = f"{end_date}T00:00:00"
        end = end_tmp
        item = {"name": q["name"], "timespan": [start, end]}
        if q["sym"] == SYM_SUMMIT and "ele" in q:
            item["ele"] = q["ele"]
            summit_names.append(q["name"])
        timeline.append(item)

    # finalize the last section
    t = timeline[0]["timespan"][0].split("T")  # start date, time
    section.append(
        {
            "title": "⚠️" + "〜".join(summit_names),
            "date": t[0],
            "timespan": [timeline[0]["timespan"][1], timeline[-1]["timespan"][0]],
            "timeline": timeline,
            "photo": [],
        }
    )
    return section


# set source gpx files and file name of routemap
resource["section"] = []

for c in [""] + list(string.digits):  # '', '0', '1', ..., '9'
    files = []
    for item in ["trk", "wpt", "rte"]:
        gpx = f"{GPX_DIR}/{cid}/{item}{c}.gpx"
        if os.path.exists(gpx):
            files.append(gpx)
        elif item == "trk":
            break  # 'wpt' and 'rte' are optional
    if len(files) > 0:
        sections = read_section(files)
        sections[0]["gpx"] = files
        sections[0]["routemap"] = f"routemap{c}.geojson"
        resource["section"].extend(sections)
        if c == "":
            break  # use only the first set of gpx files

# set prefectures and summits to resource
resource["prefectures"] = [prefectures[code] for code in sorted(prefectures)]
resource["summits"] = []
for summit in summits.values():
    location = summit["prefectures"]
    # get minimum distance among waypoints associated with the summit
    distance = min([float(wpt["distance"]) for wpt in summit["wpts"]])
    summit["distance"] = distance
    del summit["wpts"]  # remove unnecessary data
    resource["summits"].append(summit)

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
    resource["section"] = [{"timespan": [f"{ymd}T00:00:00", f"{ymd}T23:59:59"]}]

# set cover image to resource
covers = glob.glob(f"{IMG_DIR}/{cid}/cover/*")
if len(covers) < 1:
    print(f"No cover image found: {cid}", file=sys.stderr)
    sys.exit(1)
file = covers[0]
hash = extract_number(file)  # extract sequential part of cover file name
resource["cover"] = {"file": file, "hash": hash}

hash_pool = set()
hash_pool.add(hash)

# load photo's metadata
photos_unsorted = []
# NOTE: photo file name should be "arbitrary string + at least 4 digits + extension"
with ExifToolHelper() as et:
    for file in glob.glob(f"{IMG_DIR}/{cid}/*[0-9][0-9][0-9][0-9].*"):
        item = {}
        item["file"] = file
        hash = extract_number(file)  # extract sequential part of photo file name
        if hash in hash_pool and hash != resource["cover"]["hash"]:
            for c in string.ascii_lowercase:
                if (hashc := hash + c) not in hash_pool:
                    hash_pool.add(hashc)
                    item["hash"] = hashc
                    break
            if "hash" not in item:
                print(f"Too many photos: {file}", file=sys.stderr)
                sys.exit(1)
        else:
            hash_pool.add(hash)
            item["hash"] = hash

        try:
            info = et.get_metadata(file)[0]
            date_time_original = info["EXIF:DateTimeOriginal"]
            t = datetime.strptime(date_time_original, "%Y:%m:%d %H:%M:%S")
            item["time"] = t.strftime("%Y-%m-%dT%H:%M:%S")
            item["width"] = info["File:ImageWidth"]
            item["height"] = info["File:ImageHeight"]
            item["caption"] = info.get("XMP:Title", "⚠️ caption not found")
        except KeyError:
            print(f"KeyError: {file}", file=sys.stderr)
        except ValueError:
            print(f"ValueError: {file}", file=sys.stderr)

        photos_unsorted.append(item)

# number of photos should be even for left/right layout
if (n := len(photos_unsorted)) % 2 != 0:
    print(f"Error: number of photos ({n}) should be even", file=sys.stderr)
    sys.exit(1)
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
