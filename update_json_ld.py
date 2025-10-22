#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
import json
import re
import sys
from pathlib import Path

import mysql.connector
from lxml import html

mycnf = Path("~/.my.cnf").expanduser()
config = configparser.ConfigParser()
config.read(mycnf, encoding="utf-8")

connection = mysql.connector.connect(
    host=config["client"]["host"],  # データベースサーバーのホスト名
    user=config["client"]["user"],  # ユーザー名
    password=config["client"]["password"],  # パスワード
    database=config["mysql"]["database"],  # データベース名
)
cursor = connection.cursor(dictionary=True)


def update_json_ld(filename):
    original_path = Path(filename)
    cid = original_path.stem  # 拡張子を除いたファイル名
    backup_path = Path(f"{filename}.bak")
    original_path.rename(backup_path)

    parser = html.HTMLParser(encoding="utf-8")
    tree = html.parse(str(backup_path), parser=parser)
    script_tags = tree.xpath('//script[@type="application/ld+json"]')
    if not script_tags:
        print(f"Error: No JSON-LD script tag found in {filename}.", file=sys.stderr)
        sys.exit(1)

    sql = """
SELECT rec, start, end, issue, title, summary, link, image FROM record WHERE link=%s
"""
    cursor.execute(sql, (f"{cid}.html",))
    record = cursor.fetchone()

    if image := record["image"]:
        if match := re.search(r"^(.*)/S(.*)$", image):
            dest, file = match.groups()
            image = [
                {
                    "@type": "ImageObject",
                    "url": f"https://anineco.org/{dest}/W{file}",
                    "width": 1200,
                    "height": 675,
                },
                {
                    "@type": "ImageObject",
                    "url": f"https://anineco.org/{dest}/F{file}",
                    "width": 1200,
                    "height": 900,
                },
                {
                    "@type": "ImageObject",
                    "url": f"https://anineco.org/{dest}/Q{file}",
                    "width": 1200,
                    "height": 1200,
                },
            ]

    sql = """
SELECT id, sanmei.kana, sanmei.name, alt, lat, lon
FROM geom
JOIN sanmei USING (id)
JOIN explored USING (id)
WHERE type=1 AND rec=%s
ORDER BY ascent_order
"""
    cursor.execute(sql, (record["rec"],))
    summits = cursor.fetchall()

    prefectures = {}
    itinerary = []
    json_summits = []

    for summit in summits:
        places = []
        id = summit["id"]
        sql = """
SELECT code, name, qid
FROM city
WHERE code IN (
    SELECT DISTINCT CONCAT(LEFT(code, 2), '000') FROM location WHERE id=%s
)
ORDER BY code
"""
        cursor.execute(sql, (id,))
        for item in cursor.fetchall():
            code = item["code"]
            prefectures[code] = item
            places.append({"@id": f"urn:org.jpn.map:area:{code}"})

        itinerary.append(
            {
                "@type": "Place",
                "@id": f"urn:org.jpn.map:summit:{summit['id']}",
            }
        )
        json_summits.append(
            {
                "@type": "Place",
                "@id": f"urn:org.jpn.map:summit:{summit['id']}",
                "name": summit["name"],
                "additionalType": "http://schema.org/Mountain",
                "geo": {
                    "@type": "GeoCoordinates",
                    "latitude": str(summit["lat"]),
                    "longitude": str(summit["lon"]),
                    "elevation": summit["alt"],
                },
                "containedInPlace": places,
            }
        )

    json_blog = {
        "@type": "BlogPosting",
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": f"https://anineco.org/{cid}.html",
        },
        "headline": record["title"],
        "description": record["summary"],
        "author": {
            "@type": "Person",
            "name": "あにねこ",
            "url": "https://anineco.org/profile.html",
        },
        "datePublished": str(record["issue"]),
        "image": image,
        "about": {
            "@type": "Trip",
            "name": record["title"],
            "departureTime": str(record["start"]),
            "arrivalTime": str(record["end"]),
            "description": record["summary"],
            "itinerary": itinerary,
        },
    }
    if not record["issue"]:
        del json_blog["datePublished"]
    if not image:
        del json_blog["image"]

    json_areas = []
    for code, item in sorted(prefectures.items()):
        json_areas.append(
            {
                "@type": "AdministrativeArea",
                "@id": f"urn:org.jpn.map:area:{code}",
                "name": item["name"],
                "sameAs": f"wd:{item['qid']}",
            }
        )

    json_ld = {
        "@context": {
            "@vocab": "http://schema.org",
            "wd": "https://www.wikidata.org/entity/",
        },
        "@graph": [
            json_blog,
            *json_summits,
            *json_areas,
        ],
    }

    updated_json_string = json.dumps(json_ld, separators=(",", ":"), ensure_ascii=False)
    script_tags[0].text = updated_json_string

    output = html.tostring(
        tree.getroot(), method="html", encoding="unicode", doctype="<!DOCTYPE html>"
    )
    output_modified = output.replace("</source>", "")  # </source>を削除
    with original_path.open("w", encoding="utf-8") as f:
        f.write(output_modified)
        f.write("\n")


for arg in sys.argv[1:]:
    print(f"Updating {arg}...", file=sys.stderr)
    update_json_ld(arg)

cursor.close()
connection.close()
