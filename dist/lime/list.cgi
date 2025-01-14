#!/usr/local/bin/perl

#┌─────────────────────────────────
#│ LimeCounter : list.cgi - 2013/08/14
#│ Copyright (c) KentWeb
#│ http://www.kent-web.com/
#└─────────────────────────────────

# モジュール宣言
use strict;
use CGI::Carp qw(fatalsToBrowser);

# 外部ファイル取り込み
require './init.cgi';
my %cf = init();

# データ受理
my %in = parse_form();

# 処理分岐
list_data();

#-----------------------------------------------------------
#  集計画面
#-----------------------------------------------------------
sub list_data {
	# データ読み込み
	my $all = 0;
	my (@log,@tmp,%cnt);
	open(IN,"$cf{idxfile}") or error("open err: $cf{idxfile}");
	while (<IN>) {
		chomp;
		my ($id,$sub,$link,$file,$cat) = split(/<>/);

		# カテゴリ分けのとき
		next if ($in{cate} ne '' && $in{cate} ne $cat);

		open(DB,"$cf{logdir}/$id.dat");
		my $log = <DB>;
		close(DB);

		# ログ分解
		my ($count,undef) = split(/:/,$log);
		$count ||= 0;
		$cnt{$id} = $count;

		# 総計
		$all += $count;

		push(@tmp,$count);
		if ($in{chart} == 1) {
			push(@log,qq|["$sub",$count],|);
		} else {
			push(@log,$_);
		}
	}
	close(IN);

	# ソート処理
	# @log = @log[sort{$tmp[$b] <=> $tmp[$a]} 0 .. $#tmp];

	# DayCounterEX読込
	open(DB,"../dayx/data/dayx.dat");
	my $data = <DB>;
	close(DB);
	my ($total) = (split(/<>/,$data))[1];

	# 選択カテゴリ
	my %op;
	$op{cate} = qq|<option value="$_">全カテゴリー\n|;
	foreach (0 .. $#{$cf{categ}}) {
		if ($in{cate} eq $_) {
			$op{cate} .= qq|<option value="$_" selected>$cf{categ}[$_]\n|;
		} else {
			$op{cate} .= qq|<option value="$_">$cf{categ}[$_]\n|;
		}
	}

	# 選択グラフ
	my @chart = qw|棒グラフ 円グラフ|;
	foreach (0, 1) {
		if ($in{chart} == $_) {
			$op{chart} .= qq|<option value="$_" selected>$chart[$_]\n|;
		} else {
			$op{chart} .= qq|<option value="$_">$chart[$_]\n|;
		}
	}

	# 円グラフ表記のとき
	if ($in{chart} == 1) { pie_chart(\@log,\%op); }

	# テンプレート読込
	open(IN,"$cf{tmpldir}/list.html") or error("open err: list.html");
	my $tmpl = join('', <IN>);
	close(IN);

	# カテゴリなし
	if (@{$cf{categ}} == 0) {
		$tmpl =~ s/<!-- categ -->.+?<!-- categ -->//sg;
	}

	$tmpl =~ s/!homepage!/$cf{homepage}/g;
	$tmpl =~ s/!list_cgi!/$cf{list_cgi}/g;
	$tmpl =~ s/!all!/comma($all)/eg;
	$tmpl =~ s/!total!/comma($total)/eg;
	$tmpl =~ s/<!-- op_cate -->/$op{cate}/g;
	$tmpl =~ s/<!-- op_chart -->/$op{chart}/g;

	# テンプレート分解
	my ($head,$loop,$foot) = split(/<!-- loop -->/,$tmpl);

	# 画面展開
	print "Content-type: text/html; charset=utf-8\n\n";
	print $head;

	# 集計結果展開
	my ($i,$rk,$bef_c,$bef_r);
	foreach (@log) {
		my ($id,$sub,$link,$file,$cat) = split(/<>/);
		$link =~ s|anineco.org|anineco.sakura.ne.jp/tozan|;
		$sub = qq|<a href="$link" target="_blank">$sub</a>| if ($link);
		$i++;

		my ($per,$wid);
		if ($all > 0) {
			$per = sprintf("%.1f", $cnt{$id} * 100 / $all);
			if ($per > 100) { $per = 100; }
			$wid = int($per * 5);
			if ($wid < 1) { $wid = 1; }
		} else {
			$per = "0.0";
			$wid = 1;
		}

		# 順位定義
		$rk = $cnt{$id} ne $bef_c ? $i : $bef_r;
		$bef_c = $cnt{$id};
		$bef_r = $rk;

		# 文字置き換え
		my $tmp = $loop;
		$tmp =~ s/!item!/$sub/g;
		$tmp =~ s/!cate!/$cf{categ}[$cat]/g;
		$tmp =~ s/!rank!/$rk/g;
		my ($c);
		$c = comma($cnt{$id});
		if ($cnt{$id} >= 900 && $cnt{$id} < 1000) {
			$tmp =~ s|!count!|<span style="color:red;">$c</span>|g;
		} else {
			$tmp =~ s|!count!|$c|g;
		}
		$tmp =~ s|!graph!|<img src="$cf{graph}" height="8" width="$wid"> $per%|g;
		print $tmp;
	}

	# フッター
	footer($foot);
}

#-----------------------------------------------------------
#  円グラフ表記
#-----------------------------------------------------------
sub pie_chart {
	my ($log,$op) = @_;

	# スカラ変数化
	my $data = join("\n",@{$log});

	# テンプレート読込
	open(IN,"$cf{tmpldir}/list-pie.html") or error("open err: list-pie.html");
	my $tmpl = join('', <IN>);
	close(IN);

	# カテゴリなし
	if (@{$cf{categ}} == 0) {
		$tmpl =~ s/<!-- categ -->.+?<!-- categ -->//sg;
	}

	# 文字置き換え
	$tmpl =~ s/!data!/$data/g;
	$tmpl =~ s/!homepage!/$cf{homepage}/g;
	$tmpl =~ s/!list_cgi!/$cf{list_cgi}/g;
	$tmpl =~ s/<!-- op_cate -->/$$op{cate}/g;
	$tmpl =~ s/<!-- op_chart -->/$$op{chart}/g;

	# 画面展開
	print "Content-type: text/html; charset=utf-8\n\n";
	footer($tmpl);
}

#-----------------------------------------------------------
#  フッター
#-----------------------------------------------------------
sub footer {
	my $foot = shift;

	# 著作権表記（削除・改変禁止）
	my $copy = <<EOM;
<p style="margin-top:3em;text-align:center;font-family:Verdana,Helvetica,Arial;font-size:10px;">
- <a href="http://www.kent-web.com/" target="_top">LimeCounter</a> -
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

#-----------------------------------------------------------
#  エラー
#-----------------------------------------------------------
sub error {
	my $err = shift;

	# テンプレート読込
	open(IN,"$cf{tmpldir}/error.html") or die;
	my $tmpl = join('', <IN>);
	close(IN);

	$tmpl =~ s/!error!/$err/g;

	# 画面展開
	print "Content-type: text/html; charset=utf-8\n\n";
	print $tmpl;
	exit;
}

