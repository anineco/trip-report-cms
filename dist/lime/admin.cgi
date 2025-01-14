#!/usr/local/bin/perl

#┌─────────────────────────────────
#│ LimeCounter : admin.cgi - 2013/08/14
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

# 認証
check_passwd();

# 管理モード
admin_mode();

#-----------------------------------------------------------
#  管理モード
#-----------------------------------------------------------
sub admin_mode {
	# 新規画面
	if ($in{job} eq "new") {

		new_form();

	# 新規発行
	} elsif ($in{job} eq "new2") {

		if ($in{file} eq "http://") { $in{file} = ""; }
		if ($in{link} eq "http://") { $in{link} = ""; }

		my $err;
		if ($in{id} =~ /\W/) { $err .= "IDは英数字で指定してください<br>"; }
		if ($in{id} eq "check") {$err .= "ID名でcheckは使用できません<br>"; }
		if ($in{sub} eq "") { $err .= "タイトル名が未入力です<br>"; }
		if ($cf{type} >= 2 && $in{file} eq "") { $err .= "ダウンロードファイルが未入力です<br>"; }
		error($err) if ($err);

		# indexチェック
		my ($flg,@log,@tmp);
		open(DAT,"+< $cf{idxfile}") or error("open err: $cf{idxfile}");
		while (<DAT>) {
			chomp;
			my ($id,$sub,$link,$file,$cat) = split(/<>/);

			if ($in{id} eq $id) {
				$flg++;
				last;
			}
			push(@tmp,$cat) if (@{$cf{categ}} > 0);
			push(@log,"$_\n");
		}

		# 重複
		if ($flg) {
			close(DAT);
			error("$in{id}は既存のIDと重複しています");
		}

		# 新規
		push(@tmp,$in{cate}) if (@{$cf{categ}} > 0);
		push(@log,"$in{id}<>$in{sub}<>$in{link}<>$in{file}<>$in{cate}<>\n");

		# ソート
		@log = @log[sort{$tmp[$a] <=> $tmp[$b]} 0 .. $#tmp] if (@{$cf{categ}} > 0);

		# 更新
		seek(DAT, 0, 0);
		print DAT @log;
		truncate(DAT, tell(DAT));
		close(DAT);

		# カウンタ値
		open(OUT,"+> $cf{logdir}/$in{id}.dat") or error("write err: $in{id}.dat");
		print OUT "$in{count}::\n";
		close(OUT);

	# 削除
	} elsif ($in{id} && $in{job} eq "dele") {

		# indexマッチング
		my @data;
		open(DAT,"+< $cf{idxfile}") or error("open err: $cf{idxfile}");
		while (<DAT>) {
			my ($id) = (split(/<>/))[0];
			next if ($in{id} eq $id);

			push(@data,$_);
		}

		# index更新
		seek(DAT, 0, 0);
		print DAT @data;
		truncate(DAT, tell(DAT));
		close(DAT);

		# ログ削除
		unlink("$cf{logdir}/$in{id}.dat");

	# 修正画面
	} elsif ($in{id} && $in{job} eq "edit") {

		# indexチェック
		my $log;
		open(IN,"$cf{idxfile}") or error("open err: $cf{idxfile}");
		while (<IN>) {
			chomp;
			my ($id,$sub,$link,$file,$cat) = split(/<>/);

			if ($in{id} eq $id) { $log = $_; last; }
		}
		close(IN);

		# 編集フォーム
		new_form($log);

	# 修正実行
	} elsif ($in{id} && $in{job} eq "edit2") {

		if ($in{file} eq "http://") { $in{file} = ""; }
		if ($in{link} eq "http://") { $in{link} = ""; }
		my $err;
		if ($in{sub} eq "") { $err .= "タイトル名が未入力です<br>"; }
		if ($cf{type} >= 2 && $in{file} eq "") { $err .= "ダウンロードファイルが未入力です<br>"; }
		error($err) if ($err);

		# index差替え
		my (@log,@tmp);
		open(DAT,"+< $cf{idxfile}") or error("open err: $cf{idxfile}");
		while (<DAT>) {
			chomp;
			my ($id,$sub,$link,$file,$cat) = split(/<>/);

			if ($in{id} eq $id) {
				$_ = "$in{id}<>$in{sub}<>$in{link}<>$in{file}<>$in{cate}<>";
				$cat = $in{cate};
			}
			push(@tmp,$cat) if (@{$cf{categ}} > 0);
			push(@log,"$_\n");
		}

		# ソート
		@log = @log[sort{$tmp[$a] <=> $tmp[$b]} 0 .. $#tmp] if (@{$cf{categ}} > 0);

		# 上書き
		seek(DAT, 0, 0);
		print DAT @log;
		truncate(DAT, tell(DAT));
		close(DAT);

		# カウンタ更新
		if ($in{cnt} != $in{count}) {
			open(DAT,"+< $cf{logdir}/$in{id}.dat");
			eval "flock(DAT, 2);";
			my $count = <DAT>;
			my ($count,$ip) = split(/:/,$count);
			seek(DAT, 0, 0);
			print DAT "$in{count}:$ip";
			truncate(DAT, tell(DAT));
			close(DAT);
		}
	}

	header("管理モード");
	print <<EOM;
<div align="right">
<form action="$cf{admin_cgi}">
<input type="submit" value="▲ログアウト">
</form>
</div>
<div class="ttl">■ ID管理</div>
<ul>
<li>処理を選択して送信ボタンを押してください。
</ul>
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="pass" value="$in{pass}">
処理： <select name="job">
<option value="new">新規
<option value="edit">修正
<option value="dele">削除
</select>
<input type="submit" value="送信する">
<table class="fm-tbl">
<tr>
	<th>選択</th>
	<th>ID名</th>
EOM

	print qq|<th>カテゴリー</th>\n| if (@{$cf{categ}} > 0);

	print <<EOM;
	<th>タイトル</th>
	<th>カウント</th>
</tr>
EOM

	# index展開
	open(IN,"$cf{idxfile}") or error("open err: $cf{idxfile}");
	while (<IN>) {
		my ($id,$sub,$link,$file,$cat) = split(/<>/);

		# カウンタ読み取り
		open(DB,"$cf{logdir}/$id.dat");
		my $count = <DB>;
		close(DB);

		my ($count,$ip) = split(/:/,$count);

		# 桁区切り
		$count = comma($count);

		print qq|<tr><td class="ta-c"><input type="radio" name="id" value="$id"></td>|;
		print qq|<td><b>$id</b></td>|;
		print qq|<td>$cf{categ}[$cat]</td>| if (@{$cf{categ}} > 0);
		print qq|<td>$sub</td>|;
		print qq|<td class="ta-c">$count</td></tr>\n|;
	}
	close(IN);

	print <<EOM;
</table>
</form>
</body>
</html>
EOM
	exit;
}

#-----------------------------------------------------------
#  新規画面
#-----------------------------------------------------------
sub new_form {
	my $log = shift;
	my ($id,$sub,$link,$file,$cat) = split(/<>/,$log);
	$link ||= 'https://anineco.org/';

	# カウンタ読み込み
	my $job;
	my $cnt = 0;
	if ($id) {
		$job = 'edit2';

		open(DB,"$cf{logdir}/$id.dat");
		my $data = <DB>;
		close(DB);

		($cnt,undef) = split(/:/,$data);

	} else {
		$job = 'new2';
	}

	header('登録フォーム');
	print <<EOM;
<div align="right">
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="pass" value="$in{pass}">
<input type="submit" value="&lt; 前に戻る">
</form>
</div>
<div class="ttl">■ 登録フォーム</div>
<ul>
<li>新規にID情報を発行します。
<li>ID名は任意の英数字で指定してください。大文字と小文字は別物として扱われます。
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="pass" value="$in{pass}">
<input type="hidden" name="mode" value="admin">
<input type="hidden" name="job" value="$job">
<table class="fm-tbl">
<tr>
	<th>ID名</th>
	<td>
EOM

	if ($id) {
		print "<b>$id</b>\n";
		print qq|<input type="hidden" name="id" value="$id">\n|;
	} else {
		print qq|<input type="text" name="id" value="" size="10">\n|;
		print qq|（英数字で指定）\n|;
	}

	print <<EOM;
	</td>
</tr><tr>
EOM

	# カテゴリ
	if (@{$cf{categ}} > 0) {
		print qq|<th>カテゴリー</th>|;
		print qq|<td><select name="cate">|;

		foreach (0 .. $#{$cf{categ}}) {
			if ($cat eq $_) {
				print qq|<option value="$_" selected>$cf{categ}[$_]\n|;
			} else {
				print qq|<option value="$_">$cf{categ}[$_]\n|;
			}
		}

		print qq|</td></tr><tr>\n|;
	}

	print <<EOM;
	<th>タイトル名</th>
	<td><input type="text" name="sub" value="$sub" size="30"></td>
</tr><tr>
	<th>カウンタ値</th>
	<td><input type="text" name="count" value="$cnt" size="10"></td>
</tr></tr>
EOM

	if ($cf{type} >= 2) {
		$file ||= 'http://';
		print qq|<th>DLファイル</th>\n|;
		print qq|<td><input type="text" name="file" value="$file" size="50"></td>\n|;
		print qq|</tr><tr>\n|;
	}

	print <<EOM;
	<th>リンクページ</th>
	<td>
		リストからリンクするページ（任意）<br>
		<input type="text" name="link" value="$link" size="50">
	</td>
</tr>
</table>
<input type="submit" value="送信する">
</form>
</ul>
</body>
</html>
EOM
	exit;
}

#-----------------------------------------------------------
#  HTMLヘッダー
#-----------------------------------------------------------
sub header {
	my $ttl = shift;

	print <<EOM;
Content-type: text/html; charset=utf-8

<html>
<head>
<meta http-equiv="content-type" content="text/html; charset=utf-8">
<meta http-equiv="content-style-type" content="text/css">
<style type="text/css">
<!--
body,td,th { font-size:80%; background:#f0f0f0; font-family:verdana,helvetica,arial; }
div.ttl { border-bottom:1px solid #004080; width:100%; padding:4px; color:#004080; font-weight:bold; }
p.err { color:#dd0000; }
p.msg { color:#006400; }
table.fm-tbl { border-collapse:collapse; margin:1em 0; }
table.fm-tbl th,table.fm-tbl td { padding:5px; border:1px solid #666; }
table.fm-tbl th { background:#ceceff; }
table.fm-tbl td { background:#fff; }
.ta-c { text-align:center; }
-->
</style>
<title>$ttl</title>
</head>
<body>
EOM
}

#-----------------------------------------------------------
#  パスワード認証
#-----------------------------------------------------------
sub check_passwd {
	# パスワードが未入力の場合は入力フォーム画面
	if ($in{pass} eq "") {
		enter_form();

	# パスワード認証
	} elsif ($in{pass} ne $cf{password}) {
		error("認証できません");
	}
}

#-----------------------------------------------------------
#  入室画面
#-----------------------------------------------------------
sub enter_form {
	header("入室画面");
	print <<EOM;
<div align="center">
<form action="$cf{admin_cgi}" method="post">
<table width="380" style="margin-top:50px">
<tr>
	<td height="40" align="center">
		<fieldset><legend>管理パスワード入力</legend><br>
		<input type="password" name="pass" value="" size="20">
		<input type="submit" value=" 認証 "><br><br>
		</fieldset>
	</td>
</tr>
</table>
</form>
<script language="javascript">
<!--
self.document.forms[0].pass.focus();
//-->
</script>
</div>
</body>
</html>
EOM
	exit;
}

#-----------------------------------------------------------
#  エラー処理
#-----------------------------------------------------------
sub error {
	my $err = shift;

	header("ERROR!");
	print <<EOM;
<div align="center">
<h3>ERROR !</h3>
<p><font color="#dd0000">$err</font></p>
<form>
<input type="button" value="前画面に戻る" onclick="history.back()">
</form>
</div>
</body>
</html>
EOM
	exit;
}

