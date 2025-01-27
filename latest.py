#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import sqlite3

from config import DATA_DIR

# find the latest dates from metadata and changelog

connection = sqlite3.connect(f"file:{DATA_DIR}/metadata.sqlite3?mode=ro", uri=True)
connection.isolation_level = None
cursor = connection.cursor()

cursor.execute("SELECT max(start), max(pub) FROM metadata")
date1, date2 = cursor.fetchone()

connection.close()

date3 = "0000-00-00"
with open(f"{DATA_DIR}/changelog.csv", mode="r") as f:
    for pub, content in csv.reader(f):
        if date3 < pub:
            date3 = pub

year = date1[0:4]
lm_date = max(date2, date3)
lm_year = lm_date[0:4]
lmyy = lm_date[2:4]

# add prefix 'VITE_' for Vite environment variables
print(f"VITE_YEAR={year}")
print(f"VITE_LM_DATE={lm_date}")
print(f"VITE_LM_YEAR={lm_year}")
print(f"VITE_LMYY={lmyy}")

# __END__
