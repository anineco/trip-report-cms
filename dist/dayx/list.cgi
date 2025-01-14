#!/usr/local/bin/perl

#┌─────────────────────────────────
#│ DAY COUNTER-EX : list.cgi - 2017/05/14
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

# 設定ファイル取込
require './init.cgi';
my %cf = set_init();

# リスト一覧
list_data();

#-----------------------------------------------------------
#  リスト一覧
#-----------------------------------------------------------
sub list_data {
	# 累計ファイル読み込み
	open(IN,"$cf{logfile}") or die "open err: $!";
	my $data = <IN>;
	close(IN);
	
	my ($day) = (split(/<>/,$data))[0];
	
	# 本日ファイル読み込み
	open(IN,"$cf{todfile}") or die "open err: $!";
	my $tod = <IN>;
	close(IN);
	
	# 時間取得
	$ENV{TZ} = "JST-9";
	my ($mday,$mon,$year,$wday) = (localtime(time))[3..6];
	my @week = ('Sun','Mon','Tue','Wed','Thu','Fri','Sat');
	my $date = sprintf("%02d/%02d (%s) ", $mon+1,$mday,$week[$wday]);
	my $this_mon  = sprintf("%04d/%02d", $year+1900,$mon+1);
	
	# 日次ファイル読み込み
	my ($max,@day);
	open(IN,"$cf{dayfile}") or die "open err: $!";
	while(<IN>) {
		my (undef,$cnt) = split(/<>/);
		
		if ($max < $cnt) { $max = $cnt; }
		push(@day,$_);
	}
	close(IN);
	
	if ($max < $tod) { $max = $tod; }
	push(@day,"$date<>$tod<>\n");
	
	# グラフ長の係数（最高値を240px）
	my $key = 240 / $max;
	
	# 月次ファイルを読み込み
	my ($max2,@mon);
	open(IN,"$cf{monfile}") or die "open err: $!";
	while(<IN>) {
		my (undef,$cnt) = split(/<>/);
		
		if ($max2 < $cnt) { $max2 = $cnt; }
		push(@mon,$_);
	}
	close(IN);
	
	# グラフ長の係数（最高値を240px）
	my $key2 = 480 / $max2;
	
	open(IN,"$cf{tmpldir}/day-graph.txt");
	my $day_graph = join('', <IN>);
	close(IN);
	
	open(IN,"$cf{tmpldir}/day-item.txt");
	my $day_date = join('', <IN>);
	close(IN);
	
	# テンプレート読み込み
	open(IN,"$cf{tmpldir}/list.html") or die "open err: $!";
	my $tmpl = join('', <IN>);
	close(IN);
	
	$tmpl =~ s/!list_title!/$cf{list_title}/g;
	$tmpl =~ s/!this_month!/$this_mon/g;
	
	# 日次
	my ($chart_day,$graph,$date,$last_day);
	my $i = 0;
	for (@day) {
		chomp;
		my ($md,$dcnt) = split(/<>/);
		
		# グラフ幅を指定
		my $width;
		if ($dcnt > 0) {
			$width = int($dcnt * $key);
		} else {
			$width = 1;
		}
		if ($width < 1) { $width = 1; }
		
		# 桁処理
		$dcnt = comma($dcnt);
		
		$md =~ m|\d+/(\d+) \((..).\)|;
		my $day = $last_day = $1;
		my $week = $2;
		$day =~ s/^0//;
		$day =
			$week eq 'Sa' ? qq|<span style="color:blue">$day<br />$week</span>| :
			$week eq 'Su' ? qq|<span style="color:red">$day<br />$week</span>| :
				qq|$day<br />$week|;
		
		# ループ
		my $tmp1 = $day_graph;
		$tmp1 =~ s/!count!/$dcnt/g;
		$tmp1 =~ s/!height!/$width/g;
		$graph .= $tmp1;
		
		my $tmp2 = $day_date;
		$tmp2 =~ s|!date!|$day|g;
		$date .= $tmp2;
	}
	
	$tmpl =~ s/<!-- day:graph -->/$graph/;
	$tmpl =~ s/<!-- day:date -->/$date/;
	
	# テンプレート分割
	my ($head,$loop,$foot) = split(/<!-- loop -->/s,$tmpl);
	
	# 表示開始
	print "Content-type: text/html; charset=utf-8\n\n";
	print $head;
	
	# 月次
	for (@mon) {
		my ($ym,$mcnt) = split(/<>/);
		my ($year,$mon) = split(/\//,$ym);
		
		my $avr;
		
		# 今月：分母は日次データの数
		if ($_ eq $mon[$#mon]) {
			if ($mcnt > 0) {
				$avr = int (($mcnt / $last_day) + 0.5);
				$avr = comma($avr);
			} else {
				$avr = ' - ';
			}
			
		# 今月以外：分母がその月の末日
		} else {
			my $last = last_day($year,$mon);
			$avr = int (($mcnt / $last) + 0.5);
			$avr = comma($avr);
		}
		
		# グラフ幅を指定
		my $width;
		if ($mcnt > 0) {
			$width = int($mcnt * $key2);
		} else {
			$width = 1;
		}
		if ($width < 1) { $width = 1; }
		
		# 桁処理
		$mcnt = comma($mcnt);
		
		# ループ
		my $tmp = $loop;
		$tmp =~ s/!date!/$ym/g;
		$tmp =~ s/!month!/$mcnt/g;
		$tmp =~ s/!average!/$avr/g;
		$tmp =~ s/!width!/$width/g;
		print $tmp;
	}
	
	# フッタ
	footer($foot);
}

#-----------------------------------------------------------
#  月の末日
#-----------------------------------------------------------
sub last_day {
	my ($year,$mon) = @_;
	
	my $last = (31,28,31,30,31,30,31,31,30,31,30,31)[$mon - 1]
	+ ($mon == 2 && (($year % 4 == 0 && $year % 100 != 0) || $year % 400 == 0));
	
	return $last;
}

#-----------------------------------------------------------
#  桁区きり
#-----------------------------------------------------------
sub comma {
	local($_) = @_;
	
	1 while s/(.*\d)(\d\d\d)/$1,$2/;
	$_;
}

#-----------------------------------------------------------
#  フッター
#-----------------------------------------------------------
sub footer {
	my $foot = shift;
	
	# 著作権表記（削除禁止）
	my $copy = <<EOM;
<p style="margin-top:2em;text-align:center;font-family:Verdana,Helvetica,Arial;font-size:10px;">
	- <a href="http://www.kent-web.com/" target="_top">DayCounterEX</a> -
</p>
EOM

	if ($foot =~ /(.+)(<\/body[^>]*>.*)/si) {
		print "$1$copy$2\n";
	} else {
		print "$foot$copy\n";
		print "</body></html>\n";
	}
	exit;
}

