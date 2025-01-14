#!/usr/local/bin/perl

# modified 2019-12-24 by anineco@nifty.com

# RDF for joyful in UTF-8
# Ver1.0.0 
# Copyright (c) 2005 by Shigeru Yatabe  All Rights Reserved.
# 種別：フリーウェア
# 内容：CGI-Store.Net制作のRSS for YY-BOARDを参考にして
# KENT WEB joyful.cgiに対応しました。

#===============================================================
# 注意事項
# ====================================================================
# このCGIを使用した、いかなる損害に対しても開発者は一切の責任を負いません。
# Jcodeを使えないサーバでは使用できません。
# その場合はjoyfulrdfESxp.cgiをお試しください。
# ====================================================================
# 設置方法
# ====================================================================
# joyful.cgiと同じディレクトリに置き、joyfulrdfUxp.cgiのパーミッションを705に
# 変更し実行可能な状態にしてください。
# これ以外にもjoyful_view.cgiが必要です。
# また標準版とは出力ファイルの形式が違いますので、設定にはご注意ください。

# ====================================================================
# 設定項目ここから（必須）
# ====================================================================
#use Jcode;
use strict;
use warnings;
use utf8;
use open ':utf8';
use open ':std';

# このファイルのURL
my $rss_file = 'https://anineco.org/bbs/rdf.cgi';

# logファイルのパス
my $logfile = './data/log.cgi';

# ＲＳＳに表示するタイトル
my $title = 'あにねこ登山日誌 - 掲示板';

# joyful.cgiのURL
my $script = 'https://anineco.org/bbs/';

# joyful_view.cgiのURL
my $script2 = 'https://anineco.org/bbs/index.cgi';

# 掲示板の簡単な説明
my $rss_setsumei = 'RDF for あにねこ登山日誌 - 掲示板';

# 出力する最大件数
my $rss_num = 10;


# ====================================================================
# 設定項目ここまで
# ====================================================================

#logfileの読み込み-------------------------

my @data1 = ();  #表示データ配列
my @data2 = ();  #ソート後の配列
my @hiduke = ();
my @namae = ();
my @daimei = ();
my @komento = ();
my @bango1 = (); #記事の番号
my @bango2 = (); #親記事の番号

# 読み込み---------------------
open (IN, $logfile);
flock (IN, 2) ;


while (my $temp = <IN>) {

#	Jcode::convert(\$temp, 'utf8', 'sjis');
	push @data1, $temp;
}
close (IN);

shift @data1;

if ($rss_num > $#data1 + 1) { $rss_num = $#data1 + 1; }

# データを降順にソート------------------
@data2 =  sort { ( split(/<>/,$b))[2] cmp ( split(/<>/,$a))[2] } @data1;

# 表示データの取り出し-----------------------
my $i = 0; 
my $dm1;
foreach (@data2) {
	if ($i >= $rss_num) { last;}
	($bango1[$i],$bango2[$i],$hiduke[$i],$namae[$i],$dm1,$daimei[$i],$komento[$i]) = split(/<>/);

	$i++;
}


# HTMLヘッダ----------------------------------
print 'Content-Type: application/xml; charset=UTF-8' . "\n";

#print 'Pragma: no-cache' . "\n";
print 'Cache-Control: no-store' . "\n";
print "\n";

#-------------------------------------------------------
print '<?xml version="1.0" encoding="UTF-8" ?>' . "\n";
print '<rdf:RDF' . "\n";
print '  xmlns="http://purl.org/rss/1.0/"' . "\n";
print '  xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"' . "\n";
print '  xmlns:dc="http://purl.org/dc/elements/1.1/"' . "\n";
print '  xml:lang="ja">' . "\n";

# 設定値の文字コードを変換-----------------
#	Jcode::convert(\$title, 'utf8', 'sjis');
#	Jcode::convert(\$script2, 'utf8', 'sjis');
#	Jcode::convert(\$rss_file, 'utf8', 'sjis');
#	Jcode::convert(\$rss_setsumei, 'utf8', 'sjis');


#-------------------------------

print ' <channel rdf:about="' . $rss_file . '">' . "\n";
print '  <title>' . $title . '</title>' . "\n";
print '  <link>' . $script . '</link>' . "\n";
print '  <description>' . $rss_setsumei . '</description>' . "\n";
print '  <items>' . "\n";
print '   <rdf:Seq>' . "\n";
for ( $i = 0; $i < $rss_num ; $i++) {
	print '    <rdf:li rdf:resource="' . $script . '#' . $bango1[$i] . '"/>' . "\n";
}
print '   </rdf:Seq>' . "\n";
print '  </items>' . "\n";
print ' </channel>' . "\n";





# 個別データ----------------------
for ( $i = 0; $i < $rss_num; $i++) {
	$hiduke[$i] = substr($hiduke[$i], 0, 4) . '-' . substr($hiduke[$i], 5, 2) . '-' . substr($hiduke[$i], 8, 2) . 'T' . substr($hiduke[$i], -5, 2) . ':' . substr($hiduke[$i], -2, 2) . '+09:00';

	$komento[$i] =~ s/<BR>/ /g;
	$komento[$i] =~ s/<br>/ /g;
	$komento[$i] =~ s/</(/g;
	$komento[$i] =~ s/>/)/g;



	print ' <item rdf:about="' . $script . '#' . $bango1[$i] . '">' . "\n";
	print '  <title>' . $daimei[$i] . '(' . $namae[$i] . ')' . '</title>' . "\n";
	print '  <link>' . $script2 . '?read=' . $bango1[$i] . '</link>' . "\n";
	print '  <description>' . $komento[$i] . '</description>' . "\n";
	print '  <dc:date>' . $hiduke[$i] . '</dc:date>' . "\n";
	print ' </item>' . "\n";
}

print '</rdf:RDF>' . "\n";

exit;

