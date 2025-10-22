#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os.path
import sys
from datetime import datetime

from jinja2 import Environment, FileSystemLoader

from config import WORK_DIR


def json_escape(string):
    return json.dumps(string, ensure_ascii=False)


def gen_jsonld(resource):
    keys = [
        "cid", "title", "summary", "issue", "date", 
        "cover", "summits", "prefectures"
    ]
    # prepare context for Jinja2
    context = {key: resource[key] for key in keys}

    # Jinja2 template rendering
    env = Environment(loader=FileSystemLoader("template"), trim_blocks=True)
    env.filters["json_escape"] = json_escape
    template = env.get_template("ld.json.j2")
    output = template.render(context)
    return output

if __name__ == "__main__":
    if len(sys.argv) == 2:
        cid = sys.argv[1]  # Content ID
    else:
        print(f"Usage: {sys.argv[0]} <cid>", file=sys.stderr)
        sys.exit(1)

    # load resource json
    with open(os.path.join(WORK_DIR, f"{cid}.json"), "r", encoding="utf-8") as f:
        resource = json.load(f)

    now = datetime.now()
    resource["issue"] = resource.get("issue", now.strftime("%Y-%m-%d"))
    resource["summary"] = resource.get("summary", "⚠️ This article is a draft.")
    print(gen_jsonld(resource))

# __END__
