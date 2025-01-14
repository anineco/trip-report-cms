#!/bin/sh
echo "Content-type: text/plain;charset=UTF-8"
echo ""
/usr/local/bin/wget -q -O - https://a.hatena.ne.jp/$QUERY_STRING/rss | /usr/local/bin/xsltproc hatena_rss.xsl -
