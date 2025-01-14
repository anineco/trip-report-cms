#!/bin/sh
SRC=./dist
DST=anineco:/home/anineco/www/tozan # 🔖
rsync $@ -av --delete --iconv=UTF-8 --prune-empty-dirs --include-from=INCLUDES --exclude-from=EXCLUDES $SRC/ $DST/
