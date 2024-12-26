#!/usr/bin/env python

# HTML formatter

import sys
from lxml import etree as ET

args = sys.argv
if len(args) == 1:
    text = sys.stdin.read()
elif len(args) == 2:
    with open(args[1], mode='r', encoding='utf-8') as f:
        text = f.read()
else:
    print('Usage: formatter.py [<file>]', file=sys.stderr)
    sys.exit()

html = ET.fromstring(text, ET.HTMLParser())
ret = ET.tostring(html, method='html', encoding='unicode', doctype='<!DOCTYPE html>')
# FIXME: sourceは空要素であるが余分な終了タグが付加されるので削除
print(ret.replace('</source>', ''))
