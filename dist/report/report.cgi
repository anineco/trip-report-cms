#!/usr/local/bin/perl

#┌─────────────────────────────────
#│ アクセス解析システム
#│ Access Report : report.cgi - 2013/03/22
#│ copyright (c) KentWeb
#│ http://www.kent-web.com/
#└─────────────────────────────────

# モジュール宣言
use strict;
use warnings;
use utf8;
use open ':utf8';
use open ':std';
use CGI::Carp qw(fatalsToBrowser);
use Net::DNS;
use lib "./lib";
use CGI::Minimal;

# added by tad
if ($ENV{HTTP_HOST} ne 'anineco.org') {
	&load_img;
}

# 設定ファイル認識
require "./init.cgi";
my %cf = init();

# データ受理
my $cgi = CGI::Minimal->new;

# 解析
analyze_log();

#-----------------------------------------------------------
#  解析
#-----------------------------------------------------------
sub analyze_log {
	# ランダムモード
	if ($cf{rand} > 0) {
		srand;
		my $rand = int(rand($cf{rand}));
		if ($rand != 0) { load_img(); }
	}

	# リンク元取得
	my $ref;
	if ($cf{ssi}) {
		$ref = $ENV{HTTP_REFERER};
	} else {
		$ref = $ENV{QUERY_STRING};

		# escapeで取得のためURLデコードしておく
		$ref = $cgi->url_decode($ref) if ($ref);
	}

	# リンク元解析
	if ($ref =~ /^https?:\/\/[-.!~*'()\w;\/?:\@&=+\$,%#]+/i) {

		# URLデコード
		$ref = $cgi->url_decode($ref);

		# コード変換
		# require Jcode;
		# $ref = Jcode->new($ref)->sjis;

		# 無害化
		$ref = $cgi->htmlize($ref);
		$ref =~ s/'/&#39;/g;

	} else {
		$ref = '';
	}

	# リンク元集計での除外指定
	if ($cf{myurl}) {
		my $flg;
		foreach ( split(/\s+/, $cf{myurl}) ) {
			if (index($ref,$_) >= 0) { $flg++; last; }
		}
		if ($flg) { $ref = ''; }
	}

	# ホスト/IP除外
	my ($addr,$host) = get_host();

	# ブラウザ情報取得
	my $hua = $ENV{HTTP_USER_AGENT};

	my ($os,$agent);
	if ($hua =~ /AOL/) { $agent = 'AOL'; }
	elsif ($hua =~ /Opera/i) { $agent = 'Opera'; }
	elsif ($hua =~ /PlayStation/i) { $agent = 'PlayStation'; }
	elsif ($hua =~ /Googlebot/i) { $agent = 'Googlebot'; }
	elsif ($hua =~ /slurp\@inktomi\.com/i) { $agent = 'Slurp/cat'; }
	elsif ($hua =~ /Infoseek SideWinder/i) { $agent = 'Infoseek SideWinder'; }
	elsif ($hua =~ /FAST\-WebCrawler/i) { $agent = 'FAST-WebCrawler'; }
	elsif ($hua =~ /ia_archiver/i) { $agent = 'ia_archiver'; }
	elsif ($hua =~ /Edg\//i) { $agent = 'Edge'; }
	elsif ($hua =~ /Edge/i) { $agent = 'Edge'; }
	elsif ($hua =~ /Chrome/i) { $agent = 'Chrome'; }
	elsif ($hua =~ /Safari/i) { $agent = 'Safari'; }
	elsif ($hua =~ /Firefox/i) { $agent = 'Firefox'; }
	elsif ($hua =~ /MSIE (\d+)/i) { $agent = "MSIE $1"; }
	elsif ($hua =~ m|Mozilla/5.+Trident/7|i) { $agent = "MSIE 11"; }
	elsif ($hua =~ /Netscape/i) { $agent = 'Netscape'; }
	elsif ($hua =~ /Mozilla/i) { $agent = 'Mozilla'; }
	elsif ($hua =~ /Gecko/i) { $agent = 'Gecko'; }
	elsif ($hua =~ /Lynx/i) { $agent = 'Lynx'; }
	elsif ($hua =~ /Cuam/i) { $agent = 'Cuam'; $os = 'Windows'; }
	elsif ($hua =~ /Ninja/i) { $agent = 'Ninja'; $os = 'Windows'; }
	elsif ($hua =~ /WWWC/i) { $agent = 'WWWC'; $os = 'Windows'; }
	elsif ($hua =~ /DoCoMo/i) { $agent = $os = 'DoCoMo'; }
	elsif ($hua =~ /^MOT-|^J-PHONE|^SoftBank|^Vodafone|NetFront/i) { $agent = $os = 'SoftBank'; }
	elsif ($hua =~ /^UP\.Browser|^KDDI/i) { $agent = $os = 'EZweb'; }
	elsif ($hua =~ /L\-mode/i) { $agent = $os = 'L-mode'; }
	elsif ($hua =~ /ASTEL/i) { $agent = $os = 'ASTEL'; }
	elsif ($hua =~ /PDXGW/i) { $agent = $os = 'H&quot;'; }

	$agent = $cgi->htmlize($agent) if ($agent);
	$agent =~ s/['\r\n\0]//g;

	if ($hua =~ /win[dows ]*95/i) { $os = 'Win95'; }
	elsif ($hua =~ /win[dows ]*9x/i) { $os = 'WinMe'; }
	elsif ($hua =~ /win[dows ]*98/i) { $os = 'Win98'; }
	elsif ($hua =~ /win[dows ]*XP/i) { $os = 'WinXP'; }
	elsif ($hua =~ /win[dows ]*NT ?5\.1/i) { $os = 'WinXP'; }
	elsif ($hua =~ /Win[dows ]*NT ?5/i) { $os = 'Win2000'; }
	elsif ($hua =~ /win[dows ]*2000/i) { $os = 'Win2000'; }
	elsif ($hua =~ /Win[dows ]*NT ?5\.2/i) { $os = 'Win2003'; }
	elsif ($hua =~ /Win[dows ]*NT 6\.0/i || $hua =~ /Vista/i) { $os = 'WinVista'; }
	elsif ($hua =~ /Win[dows ]*NT 6\.1/i) { $os = 'Win7'; }
	elsif ($hua =~ /Win[dows ]*NT 6\.2/i) { $os = 'Win8'; }
	elsif ($hua =~ /Win[dows ]*NT 6\.3/i) { $os = 'Win8.1'; }
	elsif ($hua =~ /Win[dows ]*NT 10\.0/i) { $os = 'Win10'; }
	elsif ($hua =~ /Win[dows ]*NT/i) { $os = 'WinNT'; }
	elsif ($hua =~ /Win[dows ]*CE/i) { $os = 'WinCE'; }
	elsif ($hua =~ /shap pda browser/i) { $os = 'ZAURUS'; }
	elsif ($hua =~ /iPhone/i) { $os = 'iPhone'; }
	elsif ($hua =~ /iPad/i) { $os = 'iPad'; }
	elsif ($hua =~ /Mac/i) { $os = 'Mac'; }
	elsif ($hua =~ /Android/i) { $os = 'Android'; }
	elsif ($hua =~ /X11|SunOS|Linux|HP-UX|FreeBSD|NetBSD|OSF1|IRIX/i) { $os = 'UNIX'; }

	# 時間取得
	$ENV{TZ} = "JST-9";
	my $hour = (localtime(time))[2];

	# ログ読み込み
	my @data;
	open(DAT,"+< $cf{logfile}") or die "open err: $cf{logfile}";
	eval 'flock(DAT, 2);';
	my $top = <DAT>;

	# IPチェック
	if ($cf{ip_chk}) {
		chomp($top);
		if ($addr eq $top) {
			close(DAT);
			&load_img;
		}
	}

	# 記事数を調整
	my $i = 0;
	while (<DAT>) {
		$i++;
		push(@data,$_);

		last if ($i >= $cf{maxlog} - 1);
	}

	# 更新
	seek(DAT, 0, 0);
	print DAT "$addr\n";
	print DAT "$agent<>$os<>$host<>$ref<>$hour<>\n";
	print DAT @data;
	truncate(DAT, tell(DAT));
	close(DAT);

	# 表示
	&load_img;
}

#-----------------------------------------------------------
#  結果表示
#-----------------------------------------------------------
sub load_img {
	if ($cf{ssi}) {
		print "Content-type: text/plain\n\n";
	} else {
		# 透過GIF定義
		my @img = qw(
			47 49 46 38 39 61 01 00 01 00 f0
			00 00 00 00 00 00 00 00 21 f9 04
			01 00 00 00 00 2c 00 00 00 00 01
			00 01 00 00 02 02 44 01 00 3b
			);

		print "Content-type: image/gif\n";
		print "Cache-Control: no-store\n\n";
		binmode (STDOUT);
		foreach (@img) {
			print pack('C*',hex($_));
		}
	}
	exit;
}

#-----------------------------------------------------------
#  ホスト名取得
#-----------------------------------------------------------
sub get_host {
	# ホスト名取得
	my $host = $ENV{REMOTE_HOST};
	my $addr = $ENV{REMOTE_ADDR};
	if (!$host || $host eq $addr) {
		my $res = Net::DNS::Resolver->new;
		my $query = $res->search($addr, 'PTR');
		$host = $addr;
		if ($query) {
			foreach my $rr ($query->answer) {
				if ($rr->type eq 'PTR' && $rr->ptrdname ne 'NXDOMAIN') {
					$host = $rr->ptrdname;
					last;
				}
			}
		}
	}

	if ($cf{deny_host}) {
		my $flg;
		foreach ( split(/\s+/, $cf{deny_host}) ) {
			if (index("$host $addr",$_) >= 0) { $flg++; last; }
		}
		if ($flg) { &load_img; }
	}

	if ($host =~ /(.*)\.(\d+)$/) { ; }
	elsif ($host =~ /(.*)\.(.*)\.(.*)\.(.*)$/) { $host = "\*\.$2\.$3\.$4"; }
	elsif ($host =~ /(.*)\.(.*)\.(.*)$/) { $host = "\*\.$2\.$3"; }

	# 結果
	return ($addr,$host);
}

