# YEAR:    最新の山行記録の開始年
# LM_YEAR: 最終更新年
# LMYY:    最終更新年の下2桁
include .env.local
YEAR=$(VITE_YEAR)
LM_YEAR=$(VITE_LM_YEAR)
LMYY=$(VITE_LMYY)

TARGET_HTML = $(addprefix docs/, index.html toc.html ch${YEAR}.html hist${LMYY}.html)
TARGET_RDF = $(addprefix docs/, tozan.rdf tozan2.rdf)
TARGET_CSS = $(addprefix docs/css/, top.css tozan.css list.css chronicle.css lightbox.css)
TARGET_ENV = .env.local

.ONESHELL:

all: ${TARGET_HTML} ${TARGET_RDF} ${TARGET_CSS} ${TARGET_ENV}

.env.local: record.sqlite3 latest.sh
	./latest.sh > $@

docs/index.html: record.sqlite3 rec2idx.pl templates/index.html
	./rec2idx.pl > $@

docs/toc.html: record.sqlite3 rec2toc.pl templates/toc.html
	./rec2toc.pl > $@

docs/ch${YEAR}.html: record.sqlite3 rec2ch.pl templates/ch.html
	./rec2ch.pl ${YEAR} > $@

docs/hist${LMYY}.html: record.sqlite3 rec2hist.pl templates/hist.html
	./rec2hist.pl ${LM_YEAR} > $@

docs/tozan.rdf: record.sqlite3 rec2rss.pl templates/rss.rdf
	./rec2rss.pl > $@

docs/tozan2.rdf: record.sqlite3 rec2rss2.pl templates/rss2.rdf
	./rec2rss2.pl > $@

docs/css/%.css: src/%.css
	cleancss -o $@ $^

.PHONY: sitemap lint clean .dummy

sitemap: sitemap.xml.gz msearch/default.db

docs/sitemap.xml.gz: .dummy
	./mksitemap.sh | gzip -9 -c > $@

docs/msearch/default.db: .dummy
	(cd msearch; ./genindex.pl)

lint:
	./htmllint.sh docs/[0-9]*.html
	# ./ckpubdat.pl

clean:
	rm -f ${TARGET_HTML} ${TARGET_RDF} ${TARGET_CSS} ${TARGET_ENV}

# end of Makefile
