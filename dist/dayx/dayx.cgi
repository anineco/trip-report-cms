#!/usr/local/bin/perl

#┌─────────────────────────────────
#│ DAY COUNTER-EX : dayx.cgi - 2017/05/14
#│ copyright (c) KentWeb, 1997-2017
#│ http://www.kent-web.com/
#└─────────────────────────────────

# モジュール宣言
use strict;
use warnings;
use utf8;
use open ':utf8';
use open ':std';

# 設定ファイル取込
require './init.cgi';
my %cf = set_init();

# 引数を解釈
my $q = $ENV{QUERY_STRING};
$q =~ s/\W//g;

# 非更新系
if ($q eq "yes" || ($cf{type} == 1 && $q eq "today")) {
	
	# データ読み込み
	my $count = read_data();
	
	# 画像表示
	load_image($count);

# 更新系
} else {
	
	# データ更新
	my $count = renew_data();
	
	# 画像表示
	load_image($count);
}

#-----------------------------------------------------------
#  データ読み込み（非更新）
#-----------------------------------------------------------
sub read_data {
	# 少し待つ（更新系との衝突回避）
	select(undef,undef,undef,0.5);
	
	# 記録ファイル読み込み
	my %data = (today => $cf{todfile}, yes => $cf{yesfile});
	open(DAT,"$data{$q}") or error();
	my $data = <DAT>;
	close(DAT);
	
	return $data;
}

#-----------------------------------------------------------
#  データ更新
#-----------------------------------------------------------
sub renew_data {
	# 記録ファイル読み込み
	open(DAT,"+< $cf{logfile}") or error();
	eval "flock(DAT,2);";
	my $data = <DAT>;
	
	# 記録ファイル分解 [ 日, 累計, 曜日, IP ]
	my ($key,$count,$youbi,$ip) = split(/<>/,$data);
	
	# 日時取得
	$ENV{TZ} = "JST-9";
	my ($mday,$mon,$year,$wday) = (localtime(time))[3..6];
	$year += 1900;
	$mon = sprintf("%02d",$mon+1);
	my @week = ('Sun','Mon','Tue','Wed','Thu','Fri','Sat');
	my $thisday = $week[$wday];
	my $date = "$year/$mon";
	
	# IPチェック
	my ($flg,$addr);
	if ($ENV{HTTP_HOST} ne 'anineco.org') { $flg = 1; }
	if ($cf{ip_check}) {
		$addr = $ENV{REMOTE_ADDR};
		if ($addr eq $ip) { $flg = 1; }
	}
	
	# カウントアップ
	if (!$flg) {
		$count++;
		
		# --- 当日処理
		if ($key eq $mday) {
			
			# 本日カウントアップ
			open(TOD,"+< $cf{todfile}") or error();
			eval "flock(TOD,2);";
			my $today = <TOD> + 1;
			seek(TOD,0,0);
			print TOD $today;
			truncate(TOD,tell(TOD));
			close(TOD);
			
			# 累計ログフォーマット
			$data = "$key<>$count<>$thisday<>$addr";
		
		# --- 翌日処理
		} else {
			
			# 本日クリア
			open(TOD,"+< $cf{todfile}") or error();
			eval "flock(TOD,2);";
			my $today = <TOD>;
			seek(TOD,0,0);
			print TOD "1";
			truncate(TOD,tell(TOD));
			close(TOD);
			
			# 昨日更新
			open(YES,"+> $cf{yesfile}") or error();
			eval "flock(YES, 2);";
			print YES $today;
			close(YES);
			
			# ログフォーマット
			$data = "$mday<>$count<>$thisday<>$addr";
			
			day_count($mday,$key,$mon,$youbi,$today);
			mon_count($date,$today);
		}
		
		# ログ更新
		seek(DAT,0,0);
		print DAT $data;
		truncate(DAT,tell(DAT));
	}
	close(DAT);
	
	return $count;
}

#-----------------------------------------------------------
#  日次カウント
#-----------------------------------------------------------
sub day_count {
	my ($mday,$key,$mon,$youbi,$today) = @_;
	
	# ログの日次キーより本日の日が小さければ月が変わったと判断する
	if ($mday < $key) {
		open(DB,"+> $cf{dayfile}") or error();
		close(DB);
	
	# 月内での処理
	} else {
		if ($key < 10) { $key = "0$key"; }
		
		open(DB,">> $cf{dayfile}") or error();
		eval "flock(DB,2);";
		print DB "$mon/$key ($youbi)<>$today<>\n";
		close(DB);
	}
}

#-----------------------------------------------------------
#  月次カウント
#-----------------------------------------------------------
sub mon_count {
	my ($date,$today) = @_;
	my @mons;
	
	open(MON,"+< $cf{monfile}") or error();
	eval "flock(MON, 2);";
	
	# 初めてのアクセスの場合
	if (-z $cf{monfile}) {
		$mons[0] = "$date<>$today<>\n";
	
	# ２回目以降
	} else {
		@mons = <MON>;
		
		# ログ配列の最終行を分解
		$mons[$#mons] =~ s/\n//;
		my ($y_m,$cnt) = split(/<>/,$mons[$#mons]);
		
		# 当月処理
		if ($y_m eq $date) {
			$cnt += $today;
			$mons[$#mons] = "$y_m<>$cnt<>\n";
		
		# 翌月処理
		#（ログ配列の最終行が $dateと異なれば、月が変ったと判断する）
		} else {
			$cnt += $today;
			$mons[$#mons] = "$y_m<>$cnt<>\n";
			push(@mons,"$date<>0<>\n");
		}
	}
	
	# ログファイル更新
	seek(MON, 0, 0);
	print MON @mons;
	truncate(MON,tell(MON));
	close(MON);
}

#-----------------------------------------------------------
#  カウンタ画像表示
#-----------------------------------------------------------
sub load_image {
	my ($data) = @_;
	
	my ($digit,$dir);
	if ($q eq 'gif') {
		$digit = $cf{digit1};
		$dir = $cf{gifdir1};
	} else {
		$digit = $cf{digit2};
		$dir = $cf{gifdir2};
	}
	
	# 桁数調整
	while (length($data) < $digit) {
		$data = '0' . $data;
	}
	
	# Image::Magickのとき
	if ($cf{image_pm} == 1) {
		require $cf{magick_pl};
		magick($data, $dir);
	}
	
	# 画像読み込み
	my @img;
	foreach ( split(//,$data) ) {
		push(@img,"$dir/$_.gif");
	}
	
	# 画像連結
	require $cf{gifcat_pl};
	print "Content-type: image/gif\n";
	print "Cache-Control: no-store\n\n";
	binmode(STDOUT);
	print gifcat::gifcat(@img);
}

#-----------------------------------------------------------
#  エラー処理
#-----------------------------------------------------------
sub error {
	# エラー画像
	my @err = qw{
		47 49 46 38 39 61 2d 00 0f 00 80 00 00 00 00 00 ff ff ff 2c
		00 00 00 00 2d 00 0f 00 00 02 49 8c 8f a9 cb ed 0f a3 9c 34
		81 7b 03 ce 7a 23 7c 6c 00 c4 19 5c 76 8e dd ca 96 8c 9b b6
		63 89 aa ee 22 ca 3a 3d db 6a 03 f3 74 40 ac 55 ee 11 dc f9
		42 bd 22 f0 a7 34 2d 63 4e 9c 87 c7 93 fe b2 95 ae f7 0b 0e
		8b c7 de 02	00 3b
	};
	
	print "Content-type: image/gif\n";
	print "Cache-Control: no-store\n\n";
	for (@err) { print pack('C*', hex($_));	}
	exit;
}

