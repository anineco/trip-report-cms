#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import re
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

from lxml import html

from config import DATA_DIR, DIST_DIR, WORK_DIR

# open database connection
connection = sqlite3.connect(f"file:{DATA_DIR}/metadata.sqlite3?mode=rwc", uri=True)
connection.isolation_level = None

# create table
sql = """
CREATE TABLE IF NOT EXISTS metadata (
    cid TEXT PRIMARY KEY, -- content id
    start TEXT NOT NULL, -- start date
    end TEXT NOT NULL, -- end date
    pub TEXT, -- publication date
    region TEXT, -- list of prefectures
    title TEXT NOT NULL,
    summary TEXT,
    link TEXT, -- content url
    img1x TEXT, -- cover image
    img2x TEXT
)
"""
connection.execute(sql)

# $ cd DATA_DIR
# $ sqlite3 metadata.sqlite3
# sqlite> CREATE TABLE metadata ……;
# sqlite> .mode csv
# sqlite> .import metadata_no_page.csv metadata
# sqlite> .quit


def entercms(cid, print_only=False, modify_pub=False):
    if cid.endswith(".html"):
        original_path = Path(cid)
        cid = original_path.stem  # 拡張子を除いたファイル名
    else:
        original_path = Path(f"{DIST_DIR}/{cid}.html")

    link = f"{cid}.html"  # database `link` field

    if not print_only and modify_pub:
        backup_path = Path(f"{original_path}.bak")
        original_path.rename(backup_path)
        source_path = backup_path
    else:
        source_path = original_path

    print(f"Processing {cid} ...", file=sys.stderr)

    parser = html.HTMLParser(encoding="utf-8")
    tree = html.parse(str(source_path), parser=parser)

    elements = tree.xpath("//head/title")
    title = elements[0].text  # database `title` field

    elements = tree.xpath('//meta[@name="description"]')
    summary = elements[0].get("content")  # database `summary` field

    img1x = img2x = ""  # database `img1x` and `img2x` fields
    if elements := tree.xpath('//meta[@property="og:image"]'):
        image = elements[0].get("content")
        if match := re.search(r"https://anineco.org/(.*?)/2x/(.*?).jpg", image):
            folder, cover = match.groups()  # NOTE: folder may not match cid
            img1x = f"{folder}/S{cover}.jpg"
            img2x = f"{folder}/2x/S{cover}.jpg"

    script_tags = tree.xpath('//script[@type="application/ld+json"]')
    json_ld = json.loads(script_tags[0].text)
    graph = json_ld["@graph"]
    if not graph:
        print(f"Error: No @graph found in {arg}.", file=sys.stderr)
        sys.exit(1)

    json_blog = next(item for item in graph if item["@type"] == "BlogPosting")
    about = json_blog["about"]
    start = about["departureTime"]  # database `start` field
    end = about["arrivalTime"]  # database `end` field
    pub = json_blog.get("datePublished", "")  # database `pub` field

    # update publication date and descriptions
    if modify_pub:
        now = datetime.now()
        pub = now.strftime("%Y-%m-%d")  # database `pub` field
        json_blog["datePublished"] = pub
        json_blog["description"] = summary
        about["description"] = summary

    filtered_items = (item for item in graph if item["@type"] == "AdministrativeArea")
    sorted_items = sorted(filtered_items, key=lambda item: item["@id"])
    region = " ".join(
        [item["name"] for item in sorted_items]
    )  # database `region` field

    tupled_data = (cid, start, end, pub, region, title, summary, link, img1x, img2x)

    if print_only:
        print(tupled_data)
        return

    if modify_pub:
        updated_json_string = json.dumps(
            json_ld, separators=(",", ":"), ensure_ascii=False
        )
        script_tags[0].text = updated_json_string

        output = html.tostring(
            tree.getroot(), method="html", encoding="unicode", doctype="<!DOCTYPE html>"
        )
        output_modified = output.replace("</source>", "")  # </source>を削除

        with original_path.open("w", encoding="utf-8") as f:
            f.write(output_modified)
            f.write("\n")

        backup_path.unlink()  # remove backup file

    # insert or replace metadata
    sql = """
REPLACE INTO metadata (cid, start, end, pub, region, title, summary, link, img1x, img2x)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""
    try:
        connection.execute(sql, tupled_data)
    except sqlite3.Error as e:
        print(e, file=sys.stderr)

    # output SQL for explored summits
    with open(f"{WORK_DIR}/{cid}.sql", "w", encoding="utf-8") as f:
        f.write(
            f"""INSERT INTO record VALUES (NULL, '{start}', '{end}', '{pub}', '{title}', '{summary}', '{link}', '{img1x}');
SET @rec=LAST_INSERT_ID();
"""
        )
        # output explored summits
        i = 1
        for item in graph:
            if (
                item["@type"] == "Place"
                and item.get("additionalType") == "http://schema.org/Mountain"
            ):
                at_id = item["@id"]
                id = at_id.split(":")[-1]
                name = item["name"]
                f.write(
                    f"INSERT INTO explored VALUES (@rec, NULL, {i}, {id}); -- {name}"
                )
                f.write("\n")
                i += 1


# parse command line arguments
if len(sys.argv) > 1 and sys.argv[1] == "-d":
    sys.argv.pop(1)
    for arg in sys.argv[1:]:
        if arg.endswith(".html"):
            path = Path(arg)
            cid = path.stem  # 拡張子を除いたファイル名
        else:
            cid = arg
        try:
            connection.execute("DELETE FROM metadata WHERE cid = ?", (cid,))
        except sqlite3.Error as e:
            print(e, file=sys.stderr)
    connection.close()
    sys.exit(0)

print_only = False
modify_pub = False
if len(sys.argv) > 1 and sys.argv[1] == "-p":
    sys.argv.pop(1)
    print_only = True
if len(sys.argv) > 1 and sys.argv[1] == "-m":
    sys.argv.pop(1)
    modify_pub = True
for arg in sys.argv[1:]:
    entercms(arg, print_only=print_only, modify_pub=modify_pub)

connection.close()
# __END__
