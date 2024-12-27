#!/bin/sh
SRC=docs/
DEST=anineco:/home/anineco/www/tozan/ # 🔖
rsync $@ -av --delete --iconv=UTF-8 --prune-empty-dirs --include-from=INCLUDES --exclude-from=EXCLUDES $SRC $DEST
