#!/bin/sh
SRC=./dist
DST=ds118:/volume1/web/tozan # 🔖
rsync $@ -av --delete --iconv=UTF-8 --prune-empty-dirs --include-from=INCLUDES --exclude-from=EXCLUDES $SRC/ $DST/
