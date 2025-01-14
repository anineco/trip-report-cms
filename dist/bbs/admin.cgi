#!/usr/local/bin/perl

#┌─────────────────────────────────
#│ JOYFUL NOTE : admin.cgi - 2021/07/24
#│ copyright (c) kentweb, 1997-2021
#│ https://www.kent-web.com/
#└─────────────────────────────────

# モジュール宣言
use strict;
use CGI::Carp qw(fatalsToBrowser);
use vars qw(%in %cf);
use lib "./lib";
use CGI::Minimal;
use CGI::Session;
use Digest::SHA::PurePerl qw(sha256_base64);

# 設定ファイル認識
require "./init.cgi";
%cf = set_init();

# データ受理
CGI::Minimal::max_read_size($cf{maxdata});
my $cgi = CGI::Minimal->new;
cgi_err('容量オーバー') if ($cgi->truncated);
%in = parse_form($cgi);

# 認証
require "./lib/login.pl";
auth_login();

# 処理分岐
if ($in{data_men}) { data_men(); }
if ($in{pass_mgr}) { pass_mgr(); }

# メニュー画面
menu_html();

#-----------------------------------------------------------
#  メニュー画面
#-----------------------------------------------------------
sub menu_html {
	header("メニューTOP");
	print <<EOM;
<div id="body">
<div class="menu-msg">選択ボタンを押してください。</div>
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="sid" value="$in{sid}">
<table class="form-tbl">
<tr>
	<th>選択</th>
	<th width="280">処理メニュー</th>
</tr><tr>
	<td><input type="submit" name="data_men" value="選択"></td>
	<td>データ管理</td>
</tr><tr>
	<td><input type="submit" name="pass_mgr" value="選択"></td>
	<td>パスワード管理</td>
</tr><tr>
	<td><input type="submit" name="logoff" value="選択"></td>
	<td>ログアウト</td>
</tr>
</table>
</form>
</div>
</body>
</html>
EOM
	exit;
}

#-----------------------------------------------------------
#  記事管理
#-----------------------------------------------------------
sub data_men {
	# 修正フォーム
	if ($in{job} eq "edit" && $in{no}) {
		
		my @log;
		open(DAT,"$cf{datadir}/log.cgi");
		my $top = <DAT>;
		while (<DAT>) {
			my ($no,$reno,$date,$name,$eml,$sub,$com,$url,$host,$pw,$col,$ext,$w,$h,$chk) = split(/<>/);
			
			if ($in{no} == $no) {
				@log = ($name,$eml,$sub,$com,$url,$col,$ext);
				last;
			}
		}
		close(DAT);
		
		if (@log == 0) { cgi_err("該当記事は存在しません"); }
		
		# 修正フォーム
		edit_form(@log);
	
	# 修正実行
	} elsif ($in{job} eq "edit2") {
		
		# 入力値補正
		if ($in{url} eq 'http://') { $in{url} = ''; }
		$in{sub} ||= '無題';
		
		# データオープン
		my @data;
		open(DAT,"+< $cf{datadir}/log.cgi");
		eval "flock(DAT,2);";
		my $top = <DAT>;
		while (<DAT>) {
			my ($no,$reno,$date,$name,$eml,$sub,$com,$url,$host,$pw,$col,$ex,$w,$h,$chk) = split(/<>/);
			
			if ($no == $in{no}) {
				
				# 添付削除
				if ($in{imgdel}) {
					unlink("$cf{imgdir}/$in{no}$ex");
					unlink("$cf{imgdir}/$in{no}-s$ex") if (-f "$cf{imgdir}/$in{no}-s$ex");
					$ex = $w = $h = '';
				}
				$_ = "$no<>$reno<>$date<>$in{name}<>$in{email}<>$in{sub}<>$in{comment}<>$in{url}<>$host<>$pw<>$in{color}<>$ex<>$w<>$h<>$chk<>\n";
			}
			push(@data,$_);
		}
		
		# 更新
		unshift(@data,$top);
		seek(DAT,0,0);
		print DAT @data;
		truncate(DAT,tell(DAT));
		close(DAT);
	
	# 削除処理
	} elsif ($in{job} eq "dele" && $in{no}) {
		
		# 削除
		my @data;
		open(DAT,"+< $cf{datadir}/log.cgi");
		eval "flock(DAT,2);";
		my $top = <DAT>;
		while (<DAT>) {
			my ($no,$reno,$date,$name,$eml,$sub,$com,$url,$host,$pw,$col,$ex,$w,$h,$chk) = split(/<>/);
			
			# 削除
			if ($in{no} == $no || $in{no} == $reno) {
				unlink("$cf{imgdir}/$no$ex") if ($ex);
				unlink("$cf{imgdir}/$no-s$ex") if (-f "$cf{imgdir}/$no-s$ex");
				next;
			}
			push(@data,$_);
		}
		
		# 更新
		unshift(@data,$top);
		seek(DAT,0,0);
		print DAT @data;
		truncate(DAT,tell(DAT));
		close(DAT);
	
	# 画像許可
	} elsif ($in{job} eq "perm" && $in{no}) {
		
		# 許可情報をマッチングし更新
		my @data;
		open(DAT,"+< $cf{datadir}/log.cgi");
		eval "flock(DAT,2);";
		my $top = <DAT>;
		while (<DAT>) {
			my ($no,$reno,$date,$name,$eml,$sub,$com,$url,$host,$pw,$col,$ex,$w,$h,$chk) = split(/<>/);
			
			if ($no == $in{no}) {
				if ($chk == 1) { $chk = 0; } else { $chk = 1; }
				$_ = "$no<>$reno<>$date<>$name<>$eml<>$sub<>$com<>$url<>$host<>$pw<>$col<>$ex<>$w<>$h<>$chk<>\n";
			}
			push(@data,$_);
		}
		
		# 更新
		unshift(@data,$top);
		seek(DAT,0,0);
		print DAT @data;
		truncate(DAT,tell(DAT));
		close(DAT);
	}
	
	# 管理を表示
	header("管理画面");
	print <<EOM;
<div id="body">
<div class="back-btn">
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="sid" value="$in{sid}">
<input type="submit" value="&lt; メニュー">
</form>
</div>
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="data_men" value="1">
<input type="hidden" name="sid" value="$in{sid}">
<p>処理を選択して送信ボタンを押してください。</p>
処理：
<select name="job">
<option value="edit">編集
<option value="dele">削除
EOM

	if ($cf{img_check}) {
		print qq|<option value="perm">許可\n|;
	}
	
	print <<EOM;
</select>
<input type="submit" value="送信する">
EOM

	open(IN,"$cf{datadir}/log.cgi") or cgi_err("open err: log.cgi");
	my $top = <IN>;
	while (<IN>) {
		my ($no,$reno,$date,$name,$eml,$sub,$com,$url,$host,$pw,$col,$ex,$w,$h,$chk) = split(/<>/);
		$name = qq|<a href="mailto:$eml">$name</a>| if ($eml);
		
		if (!$reno) {
			print qq|<div class="main">|;
		} else {
			print qq|<div class="sub">|;
		}
		
		print qq|<input type="radio" name="no" value="$no">[$no]\n|;
		print qq|<b class="sub">$sub</b> 名前：<b>$name</b> 日時：$date\n|;
		if ($ex) {
			print qq|[<a href="$cf{imgurl}/$no$ex" target="_blank">添付</a>]\n|;
			if ($cf{img_check}) {
				if ($chk == 1) {
					print qq|[<span class="grn">承認済</span>]\n|;
				} else {
					print qq|[<span class="red">未承認</span>]\n|;
				}
			}
		}
		print qq|[$host]\n|;
		print qq|<div class="com">| . strcutbytes_utf8($com,100) . qq|</div>\n|;
		print qq|</div>\n|;
	}
	close(IN);
	
	print <<EOM;
</form>
</div>
</body>
</html>
EOM
	exit;
}

#-----------------------------------------------------------
#  修正フォーム
#-----------------------------------------------------------
sub edit_form {
	my ($name,$eml,$sub,$com,$url,$col,$ext) = @_;
	$com =~ s|<br( /)?>|\n|g;
	$url ||= 'http://';
	
	my @col = split(/\s+/,$cf{colors});
	my $color;
	foreach (0 .. $#col) {
		if ($col == $_) {
			$color .= qq|<input type="radio" name="color" value="$_" checked>|;
		} else {
			$color .= qq|<input type="radio" name="color" value="$_">|;
		}
		$color .= qq|<span style="color:$col[$_]">■</span>\n|;
	}
	
	header("管理モード &gt; 修正フォーム");
	print <<EOM;
<div id="body">
<div class="back-btn">
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="data_men" value="1">
<input type="hidden" name="sid" value="$in{sid}">
<input type="submit" value="&lt; 戻る">
</form>
</div>
<div class="ttl">■ 編集フォーム</div>
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="data_men" value="1">
<input type="hidden" name="sid" value="$in{sid}">
<input type="hidden" name="job" value="edit2">
<input type="hidden" name="no" value="$in{no}">
<table class="form-tbl">
<tr>
	<th>名前</th>
	<td><input type="text" name="name" value="$name" size="30"></td>
</tr><tr>
	<th>E-mail</th>
	<td><input type="text" name="email" value="$eml" size="30"></td>
</tr><tr>
	<th>件名</th>
	<td><input type="text" name="sub" value="$sub" size="40"></td>
</tr><tr>
	<th>コメント</th>
	<td><textarea name="comment" cols="50" rows="6">$com</textarea></td>
EOM

	if ($ext) {
		print qq|</tr><tr>\n|;
		print qq|<th>添付</th><td>\n|;
		print qq|[<a href="$cf{imgurl}/$in{no}$ext" target="_blank">添付</a>]&nbsp;\n|;
		print qq|<input type="checkbox" name="imgdel" value="1">削除</td>\n|;
	}
	
	print <<EOM;
</tr><tr>
	<th>URL</th>
	<td><input type="text" name="url" value="$url" size="50"></td>
</tr><tr>
	<th>文字色</th>
	<td>$color</td>
</tr><tr>
	<th></th>
	<td><input type="submit" value="送信する"></td>
</tr>
</table>
</form>
</div>
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

<!doctype html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<link href="$cf{cmnurl}/admin.css" rel="stylesheet">
<title>$ttl</title>
</head>
<body>
<div id="head"> :: JoyfulNote 管理画面 :: </div>
EOM
}

#-----------------------------------------------------------
#  エラー画面
#-----------------------------------------------------------
sub cgi_err {
	my $err = shift;
	
	header("ERROR");
	print <<EOM;
<div id="body">
<div align="center">
<hr width="350">
<h3>ERROR!</h3>
<p class="red">$err</p>
<hr width="350">
</div>
</div>
</body>
</html>
EOM
	exit;
}

#-----------------------------------------------------------
#  文字カット for UTF-8
#  [quote] http://linkage.white-void.net/development/server/perl-utf8-strcut.html
#-----------------------------------------------------------
sub strcutbytes_utf8 {
	my ($src,$maxlen) = @_;
	$src =~ s/[\t\n]//g;
	$src =~ s|<br( /)?>|\n|g;
	
	my $srclen = length($src);
	my $srcpos = 0;
	while($srcpos < $srclen) {
		my $character = substr($src, $srcpos, 1);
		my $value = ord($character);
		if($value < 0x80) { # ASCII characters
			$srcpos++;
			next;
		}
		my $width = 6;
		$width = 5 if ($value < 0xFC);
		$width = 4 if ($value < 0xF8);
		$width = 3 if ($value < 0xF0);
		$width = 2 if ($value < 0xE0);
		my $nextpos = $srcpos + $width;
		last if($nextpos > $maxlen);
		last if($nextpos > $srclen); # sequence is incomplete
		$srcpos = $nextpos;
	}
	return substr($src, 0, $srcpos);
}

