#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# a simple HTML LS formatter

import re
import sys

from lxml import etree as ET

args = sys.argv
if len(args) == 1:
    text = sys.stdin.read()
elif len(args) == 2:
    with open(args[1], mode="r", encoding="utf-8") as f:
        text = f.read()
else:
    print("Usage: html_formatter.py [<file>]", file=sys.stderr)
    sys.exit()

html = ET.fromstring(text, ET.HTMLParser())
ret = ET.tostring(html, method="html", encoding="unicode", doctype="<!DOCTYPE html>")
print(ret.replace("</source>", ""))  # NOTE: fix for lxml serialization bug

# __END__
