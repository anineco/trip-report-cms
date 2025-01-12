#!/opt/local/bin/bash -eu
r=($(sqlite3 metadata.sqlite3 '
SELECT max(start) FROM metadata;
SELECT max(pub) FROM metadata;
'))
YEAR=${r[0]:0:4}
date1=${r[1]}
date2=$(cut -d ',' -f 1 changelog.csv | sort -n | tail -n 1)

echo date1=$date1
echo date2=$date2

if [[ "$date1" > "$date2" ]]; then
  LM_DATE=$date1
else
  LM_DATE=$date2
fi
cat << EOS
VITE_YEAR=$YEAR
VITE_LM_DATE=$LM_DATE
VITE_LM_YEAR=${LM_DATE:0:4}
VITE_LMYY=${LM_DATE:2:2}
EOS
