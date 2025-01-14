# YEAR:    最新の山行記録の開始年
# LM_YEAR: 最終更新年
# LMYY:    最終更新年の下2桁
include .env.local
YEAR = ${VITE_YEAR}
LM_YEAR = ${VITE_LM_YEAR}
LMYY = ${VITE_LMYY}

# defined in config.py
DIST_DIR = ./dist
DATA_DIR = ./data

TARGET_HTML = $(addprefix ${DIST_DIR}/, index.html toc.html ch${YEAR}.html hist${LMYY}.html)
TARGET_RDF = $(addprefix ${DIST_DIR}/, tozan.rdf tozan2.rdf)
TARGET_CSS = $(addprefix ${DIST_DIR}/css/, top.css tozan.css list.css chronicle.css lightbox.css)
TARGET_JS  = $(addprefix ${DIST_DIR}/js/, tozan.js lightbox.js)
TARGET_ENV = .env.local

.ONESHELL:

all: ${TARGET_HTML} ${TARGET_RDF} ${TARGET_ENV}

css: ${TARGET_CSS}

js: ${TARGET_JS}

.env.local: ${DATA_DIR}/metadata.sqlite3 latest.py
	./latest.py > $@

${DIST_DIR}/index.html: ${DATA_DIR}/metadata.sqlite3 cms2idx.py template/index.html .env.local
	./cms2idx.py > $@

${DIST_DIR}/toc.html: ${DATA_DIR}/metadata.sqlite3 cms2toc.py template/toc.html .env.local
	./cms2toc.py > $@

${DIST_DIR}/ch${YEAR}.html: ${DATA_DIR}/metadata.sqlite3 cms2ch.py template/ch.html
	./cms2ch.py ${YEAR} > $@

${DIST_DIR}/hist${LMYY}.html: ${DATA_DIR}/metadata.sqlite3 ${DATA_DIR}/changelog.csv cms2hist.py template/hist.html
	./cms2hist.py ${LM_YEAR} > $@

${DIST_DIR}/tozan.rdf: ${DATA_DIR}/metadata.sqlite3 cms2rss.py template/rss10.xml
	./cms2rss.py 1.0 > $@

${DIST_DIR}/tozan2.rdf: ${DATA_DIR}/metadata.sqlite3 cms2rss.py template/rss20.xml
	./cms2rss.py 2.0 > $@

${DIST_DIR}/css/%.css: src/%.css
	cleancss -o $@ $^

${DIST_DIR}/js/%.js: src/%.js .env.local
	npm run build

.PHONY: sitemap lint clean .dummy

sitemap: ${DIST_DIR}/sitemap.xml.gz ${DIST_DIR}/msearch/default.db

${DIST_DIR}/sitemap.xml.gz: .dummy
	(cd ${DIST_DIR}; ${CURDIR}/mksitemap.sh) | gzip -9 -c > $@

${DIST_DIR}/msearch/default.db: .dummy
	(cd ${DIST_DIR}/msearch; ./genindex.pl)

lint:
	# NOTE: exclude google*.html
	./htmllint.sh ${DIST_DIR}/[^g]*.html
	npx htmlhint "${DIST_DIR}/[^g]*.html"

clean:
	rm -f ${TARGET_HTML} ${TARGET_RDF} ${TARGET_CSS} ${TARGET_ENV}

# end of Makefile
