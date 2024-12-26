#!/bin/bash
r=($(sqlite3 record.db '
SELECT max(start) FROM record;
CREATE TEMP TABLE issues (issue TEXT);
INSERT INTO issues SELECT max(issue) FROM record;
INSERT INTO issues SELECT max(issue) FROM changelog;
SELECT max(issue) FROM issues;
'))
YEAR=${r[0]:0:4}
LM_DATE=${r[1]}
cat << EOS
VITE_YEAR=$YEAR
VITE_LM_DATE=$LM_DATE
VITE_LM_YEAR=${LM_DATE:0:4}
VITE_LMYY=${LM_DATE:2:2}
EOS
