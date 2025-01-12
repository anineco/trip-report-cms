# YEAR:    最新の山行記録の開始年
# LM_YEAR: 最終更新年
# LMYY:    最終更新年の下2桁
include .env.local
YEAR = ${VITE_YEAR}
LM_YEAR = ${VITE_LM_YEAR}
LMYY = ${VITE_LMYY}

DOCS = docs/
TARGET_HTML = $(addprefix ${DOCS}, index.html toc.html ch${YEAR}.html hist${LMYY}.html)
TARGET_RDF = $(addprefix ${DOCS}, tozan.rdf tozan2.rdf)
TARGET_CSS = $(addprefix ${DOCS}css/, top.css tozan.css list.css chronicle.css lightbox.css)
TARGET_JS  = $(addprefix ${DOCS}js/, tozan.js lightbox.js)
TARGET_ENV = .env.local

.ONESHELL:

all: ${TARGET_HTML} ${TARGET_RDF} # ${TARGET_CSS} ${TARGET_JS} ${TARGET_ENV}

.env.local: data/metadata.sqlite3 latest.sh
	./latest.sh > $@

${DOCS}index.html: data/metadata.sqlite3 cms2idx.py template/index.html .env.local
	./cms2idx.py > $@

${DOCS}toc.html: data/metadata.sqlite3 cms2toc.py template/toc.html .env.local
	./cms2toc.py > $@

${DOCS}ch${YEAR}.html: data/metadata.sqlite3 cms2ch.py template/ch.html
	./cms2ch.py ${YEAR} > $@

${DOCS}hist${LMYY}.html: data/metadata.sqlite3 data/changelog.csv cms2hist.py template/hist.html
	./cms2hist.py ${LM_YEAR} > $@

${DOCS}tozan.rdf: data/metadata.sqlite3 cms2rss.py template/rss10.xml
	./cms2rss.py 1.0 > $@

${DOCS}tozan2.rdf: data/metadata.sqlite3 cms2rss.py template/rss20.xml
	./cms2rss.py 2.0 > $@

${DOCS}css/%.css: src/%.css
	cleancss -o $@ $^

${DOCS}js/%.js: src/%.js .env.local
	npm run build

.PHONY: sitemap lint clean .dummy

sitemap: ${DOCS}sitemap.xml.gz ${DOCS}msearch/default.db

${DOCS}sitemap.xml.gz: .dummy
	./mksitemap.sh | gzip -9 -c > $@

${DOCS}msearch/default.db: .dummy
	(cd ${DOCS}msearch; ./genindex.pl)

lint:
	./htmllint.sh docs/[0-9]*.html
	# ./ckpubdat.pl

clean:
	rm -f ${TARGET_HTML} ${TARGET_RDF} ${TARGET_CSS} ${TARGET_ENV}

# end of Makefile
