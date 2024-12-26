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
TARGET_ENV = .env.local

.ONESHELL:

all: ${TARGET_HTML} ${TARGET_RDF} ${TARGET_CSS} ${TARGET_ENV}

.env.local: record.sqlite3 latest.sh
	./latest.sh > $@

${DOCS}index.html: record.sqlite3 rec2idx.pl tmpl/index.html
	./rec2idx.pl > $@

${DOCS}toc.html: record.sqlite3 rec2toc.pl tmpl/toc.html
	./rec2toc.pl > $@

${DOCS}ch${YEAR}.html: record.sqlite3 rec2ch.pl tmpl/ch.html
	./rec2ch.pl ${YEAR} > $@

${DOCS}hist${LMYY}.html: record.sqlite3 rec2hist.pl tmpl/hist.html
	./rec2hist.pl ${LM_YEAR} > $@

${DOCS}tozan.rdf: record.sqlite3 rec2rss.pl tmpl/rss.rdf
	./rec2rss.pl > $@

${DOCS}tozan2.rdf: record.sqlite3 rec2rss2.pl tmpl/rss2.rdf
	./rec2rss2.pl > $@

${DOCS}css/%.css: src/%.css
	cleancss -o $@ $^

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
