#!/bin/sh
echo '<?xml version="1.0" encoding="UTF-8"?>'
echo '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
for name in *.html; do
  lastmod=$(stat -c %y "$name" | cut -d' ' -f1)
  case $name in
  [0-9]*)
    printf "<url>\n <loc>https://anineco.org/%s</loc>\n <lastmod>%s</lastmod>\n <priority>0.8</priority>\n</url>\n" $name $lastmod
    ;;
  index.html)
    printf "<url>\n <loc>https://anineco.org/</loc>\n <lastmod>%s</lastmod>\n <priority>0.5</priority>\n</url>\n" $lastmod
    ;;
  about.html|link.html|profile.html|nandoku.html)
    printf "<url>\n <loc>https://anineco.org/%s</loc>\n <lastmod>%s</lastmod>\n <priority>0.2</priority>\n</url>\n" $name $lastmod
    ;;
  *)
    ;;
  esac
done
echo '</urlset>'
