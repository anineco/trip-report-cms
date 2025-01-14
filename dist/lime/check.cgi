#!/usr/local/bin/perl

#┌─────────────────────────────────
#│ LimeCounter : check.cgi - 2013/08/14
#│ Copyright (c) KentWeb
#│ http://www.kent-web.com/
#└─────────────────────────────────

# モジュール宣言
use strict;
use CGI::Carp qw(fatalsToBrowser);

# 外部ファイル取り込み
require './init.cgi';
my %cf = init();

print <<EOM;
Content-type: text/html; charset=utf-8

<html>
<head>
<meta http-equiv="content-type" content="text/html; charset=utf-8">
<title>Check Mode</title>
</head>
<body>
<b>Check Mode: [ $cf{version} ]</b>
<ul>
EOM

# インデックスファイル
if (-f $cf{idxfile}) {
	print "<li>インデックスファイルパス : OK\n";
	if (-r $cf{idxfile} && -w $cf{idxfile}) {
		print "<li>インデックスファイルパーミッション : OK\n";
	} else {
		print "<li>インデックスファイルパーミッション : NG\n";
	}
} else {
	print "<li>インデックスファイルパス : NG\n";
}

# データディレクトリ
if (-d $cf{logdir}) {
	print "<li>ログディレクトリパス：OK\n";
	if (-r $cf{logdir} && -w $cf{logdir} && -x $cf{logdir}) {
		print "<li>ログディレクトリパーミッション：OK\n";
	} else {
		print "<li>ログディレクトリパーミッション : NG\n";
	}
} else {
	print "<li>ログディレクトリパス : NG\n";
}

# テンプレート
for (qw(list list-pie error)) {
	if (-e "$cf{tmpldir}/$_.html") {
		print "<li>テンプレート( $_.html ) : OK\n";
	} else {
		print "<li>テンプレート( $_.html ) : NG\n";
	}
}

print <<EOM;
</ul>
</body>
</html>
EOM
exit;


