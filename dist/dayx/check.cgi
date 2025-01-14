#!/usr/local/bin/perl

#┌─────────────────────────────────
#│ DAY COUNTER-EX : check.cgi - 2017/05/14
#│ copyright (c) KentWeb, 1997-2017
#│ http://www.kent-web.com/
#└─────────────────────────────────

# モジュール宣言
use strict;
use warnings;
use utf8;
use open ':utf8';
use open ':std';
use CGI::Carp qw(fatalsToBrowser);

require "./init.cgi";
my %cf = set_init();

print <<EOM;
Content-type: text/html

<html>
<head>
<meta http-equiv="content-type" content="text/html; charset=utf-8">
<title>Check Mode</title>
</head>
<body>
<b>Check Mode: [ $cf{version} ]</b>
<ul>
EOM

# ログファイル確認
my %log = (
	logfile => '累計',
	todfile => '本日',
	yesfile => '昨日',
	dayfile => '日次',
	monfile => '月次',
	);
	
	for ( keys %log ) {
	if (-f $cf{$_}) {
		print "<li>$log{$_}ファイルパス : OK\n";
		
		# ログファイルのパーミッション
		if (-r $cf{$_} && -w $cf{$_}) {
			print "<li>$log{$_}ファイルパーミッション : OK\n";
		} else {
			print "<li>$log{$_}ファイルパーミッション : NG\n";
		}
	} else {
		print "<li>$log{$_}ファイルパス : NG\n";
	}
}

# テンプレート
if (-f "$cf{tmpldir}/list.html") {
	print "<li>テンプレート : OK\n";
} else {
	print "<li>テンプレート : NG\n";
}

# 画像チェック
for ( $cf{gifdir1}, $cf{gifdir2} ) {
	foreach my $i (0 .. 9) {
		if (-e "$_/$i.gif") {
			print "<li>画像 : $_/$i.gif → OK\n";
		} else {
			print "<li>画像 : $_/$i.gif → NG\n";
		}
	}
}

eval { require $cf{gifcat_pl}; };
if ($@) {
	print "<li>gifcat.plテスト : NG\n";
} else {
	print "<li>gifcat.plテスト : OK\n";
}

eval { require Image::Magick; };
if ($@) {
	print "<li>Image::Magickテスト : NG\n";
} else {
	print "<li>Image::Magickテスト : OK\n";
}

print <<EOM;
</ul>
</body>
</html>
EOM

exit;

