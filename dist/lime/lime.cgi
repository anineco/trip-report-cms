#!/usr/local/bin/perl

#┌─────────────────────────────────
#│ LimeCounter : lime.cgi - 2013/08/14
#│ Copyright (c) KentWeb
#│ http://www.kent-web.com/
#└─────────────────────────────────

# モジュール宣言
use strict;

# 外部ファイル取り込み
require './init.cgi';
my %cf = init();

# 外部データ受け取り
my $buf = $ENV{QUERY_STRING};
$buf =~ s/\W//g;
error("ID情報不正") if ($buf eq '');

# データファイル定義
my $datfile = "$cf{logdir}/$buf.dat";

# カウントアップ
count_up();

#-----------------------------------------------------------
#  カウント処理
#-----------------------------------------------------------
sub count_up {
	# IPアドレス取得
	my $addr = $ENV{REMOTE_ADDR};

	if ($ENV{HTTP_HOST} ne 'anineco.sakura.ne.jp') {
		# データ読み取り
		open(DAT,"+< $datfile") or error("open errr: $datfile");
		eval "flock(DAT, 2);";
		my $data = <DAT>;

		# データ分解
		my ($count,$ip) = split(/:/,$data,2); # for ipv6

		# カウントアップ
		if (!$cf{ip_chk} || $addr ne $ip) {
			$count++;

			seek(DAT, 0, 0);
			print DAT "$count:$addr";
			truncate(DAT, tell(DAT));
		}
		close(DAT);
	}

	# ページカウンタのとき
	if ($cf{type} == 1) {

		# ダミー画像
		my @gif = qw(
			47 49 46 38 39 61 01 00 01 00 f0 00 00 00 00 00
			00 00 00 21 f9 04 01 00 00 00 00 2c 00 00 00 00
			01 00 01 00 00 02 02 44 01 00 3b
		);

		# ダミー画像表示
		print "Content-type: image/gif\n";
		print "Cache-Control: no-store\n\n";
		foreach (@gif) {
			print pack('C*',hex($_));
		}
		exit;

	# ダウンロードカウンタのとき
	} else {

		# index読み取り
		my ($flg, $jump);
		open(IN,"$cf{idxfile}") or error("open err: $cf{idxfile}");
		while (<IN>) {
			chomp;
			my ($id,$sub,$link,$file,$cat) = split(/<>/);

			if ($buf eq $id) {
				$flg++;
				$jump = $file;
				last;
			}
		}
		close(IN);

		if (!$flg) { error("IDが不正です"); }

		# Locationヘッダ
		if ($cf{type} == 2) {

			# ファイルへ移動
			if ($ENV{PERLXS} eq "PerlIS") {
				print "HTTP/1.0 302 Temporary Redirection\r\n";
 				print "Content-type: text/html\n";
			}
			print "Location: $jump\n\n";
			exit;

		# metaタグ
		} else {
			header('<meta http-equiv="refresh" content="1; url=$jump">');
			print qq|<div align="center">\n|;
			print qq|<p>ダウンロードできない場合は<a href="$jump">ここ</a>をクリック。</p>\n|;
			print qq|</div>\n|;
			print qq|</body></html>\n|;
			exit;
		}
	}
}

#-----------------------------------------------------------
#  エラー処理
#-----------------------------------------------------------
sub error {
	my $err = shift;

	# ダウンロードカウンタの場合
	if ($cf{type} > 1) {
		header();
		print "<h3>ERROR</h3>\n";
		print "<p>$err</p>\n";
		print "</body></html>\n";
		exit;

	# ページカウンタの場合
	} else {
		die "error: $err";
	}
}

#-----------------------------------------------------------
#  HTMLヘッダ
#-----------------------------------------------------------
sub header {
	my ($meta) = @_;

	print <<EOM;
Content-type: text/html; charset=utf-8

<html>
<head>
<meta http-equiv="content-type" content="text/html; charset=utf-8">
$meta
<title>$cf{version}</title>
</head>
<body>
EOM
}

