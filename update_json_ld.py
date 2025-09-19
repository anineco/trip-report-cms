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

prefs_aux = {
    "000822": ["新潟県", "長野県"],
    "020921": ["福島県", "新潟県"],
    "030309": ["群馬県"],
    "030810": ["富山県"],
    "040330": ["青森県"],
    "050211": ["栃木県"],
    "060205": ["栃木県"],
    "060527": ["栃木県"],
    "070113": ["栃木県"],
    "070520": ["山梨県"],
    "070912": ["鳥取県"],
    "080915": ["群馬県"],
    "081109": ["群馬県"],
    "090405": ["新潟県"],
    "090523": ["群馬県"],
    "100509": ["栃木県"],
    "100515": ["群馬県"],
    "100724": ["福島県", "群馬県"],
    "100801": ["群馬県"],
    "110618": ["群馬県", "新潟県"],
    "110814": ["新潟県"],
    "111218": ["群馬県"],
    "130706": ["栃木県"],
    "130804": ["栃木県"],
    "140405": ["群馬県"],
    "170320": ["千葉県"],
    "180812": ["栃木県"],
    "241014": ["新潟県"],
    "990815": ["長野県"],
}


def update_json_ld(filename):
    original_path = Path(filename)
    cid = original_path.stem  # 拡張子を除いたファイル名
    backup_path = Path(f"{filename}.bak")
    original_path.rename(backup_path)

    sql = """
SELECT rec, start, end, issue FROM record WHERE link=%s
"""
    cursor.execute(sql, (f"{cid}.html",))
    record = cursor.fetchone()
    sql = """
SELECT id, name FROM explored JOIN sanmei USING (id) WHERE type=1 AND rec=%s
"""
    cursor.execute(sql, (record["rec"],))
    summits = cursor.fetchall()
    prefectures = {}
    for s in summits:
        sql = """
SELECT code, name FROM city WHERE code IN (SELECT DISTINCT (code DIV 1000) * 1000 FROM location WHERE id=%s)
"""
        cursor.execute(sql, (s["id"],))
        prefs = cursor.fetchall()
        for p in prefs:
            prefectures[p["code"]] = p["name"]

    parser = html.HTMLParser(encoding="utf-8")
    tree = html.parse(str(backup_path), parser=parser)
    script_tags = tree.xpath('//script[@type="application/ld+json"]')
    if not script_tags:
        print(f"Error: No JSON-LD script tag found in {filename}.", file=sys.stderr)
        sys.exit(1)
    json_data = json.loads(script_tags[0].text)

    issue_date = None
    if record["issue"] is not None:
        issue_date = str(record["issue"])
    elif "datePublished" in json_data:
        issue_date = json_data["datePublished"]

    location = []
    if prefectures:
        for code in sorted(prefectures):
            location.append({"@type": "AdministrativeArea", "name": prefectures[code]})
    elif cid in prefs_aux:
        for name in prefs_aux[cid]:
            location.append({"@type": "AdministrativeArea", "name": name})

    json_ld = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": f"https://anineco.org/{cid}.html",
        },
        "headline": json_data["headline"],
        "author": {"@type": "Person", "name": "あにねこ"},
        "datePublished": issue_date,
        "image": json_data["image"],
        "about": {
            "@type": "Event",
            "name": json_data["headline"],
            "startDate": str(record["start"]),
            "endDate": str(record["end"]),
            "location": location,
        },
    }
    if issue_date is None:
        del json_ld["datePublished"]

    updated_json_string = json.dumps(
        json_ld, indent=1, separators=(",", ":"), ensure_ascii=False
    )
    script_tags[0].text = updated_json_string

    # <time>タグを削除
    time_elements = tree.xpath("//time")
    for time_tag in time_elements:
        time_tag.drop_tag()

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
