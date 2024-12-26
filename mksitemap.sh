#!/bin/sh
cd docs
echo '<?xml version="1.0" encoding="UTF-8"?>'
echo '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
/bin/ls -l -T *.html| while read p l u g s m d t y n; do
  case $n in
  [0-9]*)
    printf "<url>\n <loc>https://anineco.org/%s</loc>\n <lastmod>%04d-%02d-%02d</lastmod>\n <priority>0.8</priority>\n</url>\n" $n $y $m $d
    ;;
  index.html)
    printf "<url>\n <loc>https://anineco.org/</loc>\n <lastmod>%04d-%02d-%02d</lastmod>\n <priority>0.5</priority>\n</url>\n" $y $m $d
    ;;
  about.html|link.html|profile.html|nandoku.html)
    printf "<url>\n <loc>https://anineco.org/%s</loc>\n <lastmod>%04d-%02d-%02d</lastmod>\n <priority>0.2</priority>\n</url>\n" $n $y $m $d
    ;;
  *)
    ;;
  esac
done
echo '</urlset>'
