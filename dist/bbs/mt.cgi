#!/usr/local/bin/perl

#┌─────────────────────────────────
#│ JOYFUL NOTE : regist.cgi - 2021/07/24
#│ copyright (c) kentweb, 1997-2021
#│ https://www.kent-web.com/
#└─────────────────────────────────

# モジュール宣言
use strict;
use CGI::Carp qw(fatalsToBrowser);
use lib "./lib";
use CGI::Minimal;

# 設定ファイル認識
require "./init.cgi";
my %cf = set_init();

# データ受理
CGI::Minimal::max_read_size($cf{maxdata});
my $cgi = CGI::Minimal->new;
error('容量オーバー') if ($cgi->truncated);
my %in = parse_form($cgi);

# アクセス制限
passwd(%in) if ($cf{enter_pwd} ne '');

if ($in{mode} eq "regist") { regist(); }
if ($in{mode} eq "log_edit") { log_edit(); }
if ($in{mode} eq "log_dele") { log_dele(); }
error("不明な処理です");

#-----------------------------------------------------------
#  投稿記事受付
#-----------------------------------------------------------
sub regist {
	# フォーム入力チェック
	form_check();
	
	# 投稿キーチェック
	if ($cf{use_captcha} > 0) {
		require $cf{captcha_pl};
		if ($in{captcha} !~ /^\d{$cf{cap_len}}$/) {
			error("投稿キーが入力不備です。<br>投稿フォームに戻って再読込み後、再入力してください");
		}
		
		# 投稿キーチェック
		# -1 : キー不一致
		#  0 : 制限時間オーバー
		#  1 : キー一致
		my $chk = cap::check($in{captcha},$in{str_crypt},$cf{captcha_key},$cf{cap_time},$cf{cap_len});
		if ($chk == 0) {
			error("投稿キーが制限時間を超過しました。<br>投稿フォームに戻って再読込み後、指定の数字を再入力してください");
		} elsif ($chk == -1) {
			error("投稿キーが不正です。<br>投稿フォームに戻って再読込み後、再入力してください");
		}
	}
	
	# ホスト取得
	my ($host,$addr) = get_host();
	
	# 時間取得
	my ($date,$time) = get_time();
	
	# ログを開く
	my @data;
	open(DAT,"+< $cf{datadir}/log.cgi");
	eval "flock(DAT,2);";
	my $top = <DAT>;
	
	# 記事NO処理
	my ($no,$ip,$time2) = split(/<>/,$top);
	$no++;
	
	# 連続投稿チェック
	if ($addr eq $ip && $cf{wait} > $time - $time2) {
		close(DAT);
		error("連続投稿はもうしばらく時間をおいて下さい");
	}
	
	# アップロード
	my ($ext,$w,$h) = upload($no) if ($in{upfile});
	
	# 削除キー暗号化
	my $crypt = encrypt($in{pwd}) if ($in{pwd} ne "");
	
	# 親記事の場合
	my @past;
	if ($in{reno} eq "") {
		my ($i,$stop);
		while (<DAT>) {
			my ($no2,$reno2,$dat,$nam,$eml,$sub,$com,$url,$hos,$pw,$col,$ex2,$w2,$h2,$chk) = split(/<>/);
			if ($reno2 eq "") { $i++; }
			if ($i > $cf{max} - 1 && $reno2 eq "") { $stop = 1; }
			if (!$stop) {
				push(@data,$_);
			} else {
				# 過去ログ
				push(@past,$_);
				
				# 添付ファイル削除
				if ($ex2) {
					unlink("$cf{imgdir}/$no2$ex2") if ($ex2);
					unlink("$cf{imgdir}/$no2-s$ex2") if ($ex2 && -f "$cf{imgdir}/$no2-s$ex2");
				}
			}
		}
		unshift(@data,"$no<><>$date<>$in{name}<>$in{email}<>$in{sub}<>$in{comment}<>$in{url}<>$host<>$crypt<>$in{color}<>$ext<>$w<>$h<>0<>\n");
		unshift(@data,"$no<>$addr<>$time<>\n");
		
		# 過去ログ更新
		if (@past > 0) { make_past(@past); }
	
	# レス記事：トップソートあり
	} elsif ($in{reno} && $cf{topsort}) {
		
		my ($flg,$match,@tmp);
		while (<DAT>) {
			my ($no2,$reno2,$dat,$nam,$eml,$sub,$com,$url,$hos,$pw,$col,$ex2,$w2,$h2,$chk) = split(/<>/);
			
			# 親記事あり
			if ($in{reno} == $no2) {
				if ($reno2) { $flg = 1; last; }
				$match = 1;
				push(@data,$_);
			
			# レス記事あり
			} elsif ($in{reno} == $reno2) {
				push(@data,$_);
			
			# 親記事の直下に置く
			} elsif ($match == 1 && $in{reno} != $reno2) {
				$match = 2;
				push(@data,"$no<>$in{reno}<>$date<>$in{name}<>$in{email}<>$in{sub}<>$in{comment}<>$in{url}<>$host<>$crypt<>$in{color}<>$ext<>$w<>$h<>0<>\n");
				push(@tmp,$_);
			
			} else {
				push(@tmp,$_);
			}
		}
		if ($flg || !$match) {
			close(DAT);
			error("不正な返信要求です");
		}
		
		# 最初のレス記事のケース
		if ($match == 1) {
			push(@data,"$no<>$in{reno}<>$date<>$in{name}<>$in{email}<>$in{sub}<>$in{comment}<>$in{url}<>$host<>$crypt<>$in{color}<>$ext<>$w<>$h<>0<>\n");
		}
		# レス記事１式をトップへ
		push(@data,@tmp);
		unshift(@data,"$no<>$addr<>$time<>\n");
	
	# レス記事：トップソートなし
	} else {
		
		my ($flg,$match);
		while (<DAT>) {
			my ($no2,$reno2,$dat,$nam,$eml,$sub,$com,$url,$hos,$pw,$col,$ex2,$w2,$h2,$chk) = split(/<>/);
			
			if ($match == 0 && $in{reno} == $no2) {
				if ($reno2) { $flg = 1; last; }
				$match = 1;
			
			} elsif ($match == 1 && $in{reno} != $reno2) {
				$match = 2;
				push(@data,"$no<>$in{reno}<>$date<>$in{name}<>$in{email}<>$in{sub}<>$in{comment}<>$in{url}<>$host<>$crypt<>$in{color}<>$ext<>$w<>$h<>0<>\n");
			}
			push(@data,$_);
		}
		if ($flg || !$match) {
			close(DAT);
			error("不正な返信要求です");
		}
		
		if ($match == 1) {
			push(@data,"$no<>$in{reno}<>$date<>$in{name}<>$in{email}<>$in{sub}<>$in{comment}<>$in{url}<>$host<>$crypt<>$in{color}<>$ext<>$w<>$h<>0<>\n");
		}
		unshift(@data,"$no<>$addr<>$time<>\n");
	}
	
	# 更新
	seek(DAT,0,0);
	print DAT @data;
	truncate(DAT,tell(DAT));
	close(DAT);
	
	# クッキー格納
	set_cookie($in{name},$in{email},$in{url},$in{color});
	
	# メール通知
	if ($cf{mailing} == 1) {
		my $clip = "$no$ext" if ($ext);
		mail_to($date,$host,$clip);
	}
	
	# 完了画面
	message('ありがとうございます。記事を受理しました。');
}

#-----------------------------------------------------------
#  ユーザ記事削除
#-----------------------------------------------------------
sub log_dele {
	$in{no} =~ s/\D//g;
	if ($in{no} eq '' || $in{pwd} eq '') {
		error("記事Noまたは削除キーが入力モレです");
	}
	
	my ($top,$flg,$oya_flg,@data);
	open(DAT,"+< $cf{datadir}/log.cgi");
	eval "flock(DAT,2);";
	my $top = <DAT>;
	while (<DAT>) {
		my ($no,$reno,$date,$name,$eml,$sub,$com,$url,$host,$pw,$col,$ext,$w,$h,$chk) = split(/<>/);
		
		# 該当記事
		if ($in{no} == $no) {
			$oya_flg = 1;
			$flg = 1;
			if ($pw eq '') {
				$flg = 2;
				last;
			}
			# 削除キー照合
			if (decrypt($in{pwd},$pw) != 1) {
				$flg = 3;
				last;
			}
			# 添付ファイル削除
			if ($ext) {
				unlink("$cf{imgdir}/$no$ext");
				unlink("$cf{imgdir}/$no-s$ext") if (-f "$cf{imgdir}/$no-s$ext");
			}
			next;
		
		# 親記事を削除した場合はレス記事削除
		} elsif ($oya_flg && $in{no} == $reno) {
			
			# 添付ファイル削除
			if ($ext) {
				unlink("$cf{imgdir}/$no$ext");
				unlink("$cf{imgdir}/$no-s$ext") if (-f "$cf{imgdir}/$no-s$ext");
			}
			next;
		}
		push(@data,$_);
	}
	if (!$flg) {
		close(DAT);
		error("該当記事が見当たりません");
	} elsif ($flg == 2) {
		close(DAT);
		error("該当記事には削除キーが設定されていません");
	} elsif ($flg == 3) {
		close(DAT);
		error("削除キーが違います");
	}
	
	# 更新
	seek(DAT,0,0);
	print DAT $top;
	print DAT @data;
	truncate(DAT,tell(DAT));
	close(DAT);
	
	# 完了
	message("記事を削除しました");
}

#-----------------------------------------------------------
#  記事修正処理
#-----------------------------------------------------------
sub log_edit {
	$in{no} =~ s/\D//g;
	if ($in{no} eq '' || $in{pwd} eq '') {
		error("記事Noまたは暗証キーが入力モレです");
	}
	
	# 実行
	if ($in{job} eq "edit") {
		
		# フォーム入力チェック
		form_check();
		
		my ($flg,$ext2,$w2,$h2,@data);
		open(DAT,"+< $cf{datadir}/log.cgi");
		eval "flock(DAT,2);";
		my $top = <DAT>;
		while (<DAT>) {
			my ($no,$reno,$date,$name,$eml,$sub,$com,$url,$host,$pw,$col,$ext,$w,$h,$chk) = split(/<>/);
			
			if ($in{no} == $no) {
				$flg = 1;
				if ($pw eq '') {
					$flg = -1;
					last;
				}
				# 削除キー照合
				if (decrypt($in{pwd},$pw) != 1) {
					$flg = -2;
					last;
				}
				
				# アップロード
				if ($in{upfile}) { ($ext2,$w2,$h2) = upload($in{no}); }
				
				# 画像削除
				if ($in{attdel}) {
					unlink("$cf{imgdir}/$in{no}$ext");
					unlink("$cf{imgdir}/$in{no}-s$ext") if (-f "$cf{imgdir}/$in{no}-s$ext");
					$ext = $w = $h = '';
				}
				
				# 添付アップロードの場合
				if ($ext2) {
					# 拡張子変更の場合旧ファイル削除
					if ($ext && $ext2 ne $ext) {
						unlink("$cf{imgdir}/$in{no}$ext");
						unlink("$cf{imgdir}/$in{no}-s$ext") if (-f "$cf{imgdir}/$in{no}-s$ext");
					}
					# 新添付ファイル情報
					($ext,$w,$h) = ($ext2,$w2,$h2);
				}
				$_ = "$no<>$reno<>$date<>$in{name}<>$in{email}<>$in{sub}<>$in{comment}<>$in{url}<>$host<>$pw<>$in{color}<>$ext<>$w<>$h<>$chk<>\n";
			}
			push(@data,$_);
		}
		
		if ($flg < 1) {
			close(DAT);
			error("不正な処理です");
		}
		
		# 更新
		seek(DAT,0,0);
		print DAT $top;
		print DAT @data;
		truncate(DAT,tell(DAT));
		close(DAT);
		
		# 完了メッセージ
		message("修正が完了しました");
	}
	
	my ($flg,$log);
	open(IN,"$cf{datadir}/log.cgi");
	my $top = <IN>;
	while (<IN>) {
		my ($no,$reno,$date,$name,$eml,$sub,$com,$url,$host,$pw,$col,$ext,$w,$h,$chk) = split(/<>/);
		
		if ($in{no} == $no) {
			$flg = 1;
			if ($pw eq '') {
				$flg = -1;
			}
			# 削除キー照合
			if (decrypt($in{pwd},$pw) != 1) {
				$flg = -2;
			}
			$log = $_;
			last;
		}
	}
	close(IN);
	
	# 判定
	if (!$flg) {
		error("該当記事が見当たりません");
	} elsif ($flg == -1) {
		error("該当記事には削除キーが設定されていません");
	} elsif ($flg == -2) {
		error("削除キーが違います");
	}
	
	# 改行復元
	my ($no,$reno,$date,$name,$eml,$sub,$com,$url,$host,$pw,$col,$ext,$w,$h,$chk) = split(/<>/,$log);
	$com =~ s|<br( /)?>|\n|g;
	$url ||= 'http://';
	
	# 色選択ボタン
	my @col = split(/\s+/, $cf{colors});
	my $color;
	foreach (0 .. $#col) {
		if ($_ == $col) {
			$color .= qq|<input type="radio" name="color" value="$_" checked>|;
		} else {
			$color .= qq|<input type="radio" name="color" value="$_">|;
		}
		$color .= qq|<span style="color:$col[$_]">■</span>\n|;
	}
	
	# 添付ファイル
	my $attach;
	if ($ext) {
		$attach .= qq|&nbsp; [<a href="$cf{imgdir}/$no$ext" target="_blank">添付</a>]\n|;
		$attach .= qq|<input type="checkbox" name="attdel" value="1">削除\n|;
	}
	
	# トピック画面用
	$in{bbs} ||= 0;
	my $read = $in{bbs} == 1 ? $in{no} : 0;
	
	# 修正フォーム
	open(IN,"$cf{tmpldir}/edit.html") or error("open err: edit.html");
	my $tmpl = join('',<IN>);
	close(IN);
	
	$tmpl =~ s/!bbs_title!/$cf{bbs_title}/g;
	$tmpl =~ s|!bbs_css!|$cf{cmnurl}/bbs.css|g;
	$tmpl =~ s|!bbs_js!|$cf{cmnurl}/bbs.js|g;
	$tmpl =~ s/!([a-z]+_cgi)!/$cf{$1}/g;
	$tmpl =~ s/!num!/$in{no}/g;
	$tmpl =~ s/!pwd!/$in{pwd}/g;
	$tmpl =~ s/!name!/$name/g;
	$tmpl =~ s/!email!/$eml/g;
	$tmpl =~ s/!sub!/$sub/g;
	$tmpl =~ s/!comment!/$com/g;
	$tmpl =~ s/!url!/$url/g;
	$tmpl =~ s/!color!/$color/g;
	$tmpl =~ s/!bbs!/$in{bbs}/g;
	$tmpl =~ s/!read!/$read/g;
	$tmpl =~ s/<!-- attach -->/$attach/g;
	
	print "Content-type: text/html; charset=utf-8\n\n";
	print $tmpl;
	exit;
}

#-----------------------------------------------------------
#  過去ログ生成
#-----------------------------------------------------------
sub make_past {
	my @past = @_;
	
	# 過去ログNOファイル
	open(NO,"+< $cf{nofile}") or error("open err: $cf{nofile}");
	eval "flock(NO,2);";
	my $num = <NO>;
	
	# 過去ログを定義
	my $pastfile = "$cf{pastdir}/" . sprintf("%04d",$num) . ".cgi";
	
	# 過去ログを開く
	open(LOG,"+< $pastfile") or error("open err: $pastfile");
	eval "flock(LOG,2);";
	my @data = <LOG>;
	
	# 規定行数オーバー時、次ファイル生成
	if (@data > $cf{pastmax}) {
		
		# 過去ログを閉じる
		@data = ();
		close(LOG);
		
		# 過去NO更新
		seek(NO,0,0);
		print NO ++$num;
		truncate(NO,tell(NO));
		close(NO);
		
		$pastfile = "$cf{pastdir}/" . sprintf("%04d",$num) . ".cgi";
		
		open(LOG,"+> $pastfile");
		eval "flock(LOG,2);";
		print LOG @past;
		close(LOG);
		
		chmod(0666, $pastfile);
	
	# 規定内
	} else {
		
		# 過去NOファイルを閉じる
		close(NO);
		
		# 過去ログ更新
		seek(LOG,0,0);
		print LOG @past;
		print LOG @data;
		truncate(LOG,tell(LOG));
		close(LOG);
	}
}

#-----------------------------------------------------------
#  フォーム入力チェック
#-----------------------------------------------------------
sub form_check {
	# 不要改行カット
	$in{sub}  =~ s|<br>||g;
	$in{name} =~ s|<br>||g;
	$in{pwd}  =~ s|<br>||g;
	$in{captcha} =~ s|<br>||g;
	$in{color} =~ s/\D//g;
	$in{comment} =~ s|(<br>)+$||g;
	
	# チェック
	if ($cf{no_wd}) { no_wd(); }
	if ($cf{jp_wd}) { jp_wd(); }
	if ($cf{urlnum} > 0) { urlnum(); }
	
	# 入力値調整
	if ($in{url} eq 'http://') { $in{url} = ''; }
	$in{sub} ||= "無題";
	
	# 入力項目チェック
	my $err;
	if (count_str($in{sub}) > $cf{sub_len}) {
		$err .= "タイトル名は$cf{sub_len}文字以内です<br>";
	}
	if ($in{name} eq "") { $err .= "名前が入力されていません<br>"; }
	if ($in{comment} eq "") { $err .= "コメントが入力されていません<br>"; }
	if ($in{email} ne '' && $in{email} !~ /^[\w\.\-]+\@[\w\.\-]+\.[a-zA-Z]{2,6}$/) {
		$err .= "Ｅメールの入力内容が不正です<br>";
	}
	if ($in{url} ne '' && $in{url} !~ /^https?:\/\/[\w-.!~*'();\/?:\@&=+\$,%#]+$/) {
		$err .= "URL情報が不正です<br>";
	}
	error($err) if ($err);
}

#-----------------------------------------------------------
#  メール送信
#-----------------------------------------------------------
sub mail_to {
	my ($date,$host,$clip) = @_;
	
	# 件名をMIMEエンコード
	require './lib/jacode.pl';
	my $msub = mime_unstructured_header("BBS: $in{sub}");
	
	# コメント内の改行復元
	my $com = $in{comment};
	$com =~ s|<br>|\n|g;
	$com =~ s/&lt;/>/g;
	$com =~ s/&gt;/</g;
	$com =~ s/&quot;/"/g;
	$com =~ s/&amp;/&/g;
	$com =~ s/&#39;/'/g;
	
	# メール本文を定義
	my $mbody = <<EOM;
掲示板に投稿がありました。

投稿日：$date
ホスト：$host

件名  ：$in{sub}
お名前：$in{name}
E-mail：$in{email}
URL   ：$in{url}
添付  ：$clip

$com
EOM

	# JISコード変換
	my $body;
	for my $tmp ( split(/\n/,$mbody) ) {
		jcode::convert(\$tmp,'jis','utf8');
		$body .= "$tmp\n";
	}
	
	# メールアドレスがない場合は管理者メールに置き換え
	$in{email} ||= $cf{mailto};
	
	# sendmailコマンド
	my $scmd = "$cf{sendmail} -t -i";
	if ($cf{sendm_f}) { $scmd .= " -f $in{email}"; }
	
	# 送信
	open(MAIL,"| $scmd") or error("送信失敗");
	print MAIL "To: $cf{mailto}\n";
	print MAIL "From: $in{email}\n";
	print MAIL "Subject: $msub\n";
	print MAIL "MIME-Version: 1.0\n";
	print MAIL "Content-type: text/plain; charset=ISO-2022-JP\n";
	print MAIL "Content-Transfer-Encoding: 7bit\n";
	print MAIL "X-Mailer: $cf{version}\n\n";
	print MAIL "$body\n";
	close(MAIL);
}

#-----------------------------------------------------------
#  時間取得
#-----------------------------------------------------------
sub get_time {
	$ENV{TZ} = "JST-9";
	my $time = time;
	my ($min,$hour,$mday,$mon,$year,$wday) = (localtime($time))[1..6];
	my @week = qw|Sun Mon Tue Wed Thu Fri Sat|;
	
	# 日時のフォーマット
	my $date = sprintf("%04d/%02d/%02d(%s) %02d:%02d",
			$year+1900,$mon+1,$mday,$week[$wday],$hour,$min);
	
	return ($date, $time);
}

#-----------------------------------------------------------
#  禁止ワードチェック
#-----------------------------------------------------------
sub no_wd {
	my $flg;
	foreach ( split(/,/,$cf{no_wd}) ) {
		if (index("$in{name} $in{sub} $in{comment}", $_) >= 0) {
			$flg = 1;
			last;
		}
	}
	if ($flg) { error("禁止ワードが含まれています"); }
}

#-----------------------------------------------------------
#  日本語チェック
#-----------------------------------------------------------
sub jp_wd {
	if ($in{comment} !~ /(?:[\xC0-\xDF][\x80-\xBF]|[\xE0-\xEF][\x80-\xBF]{2}|[\xF0-\xF7][\x80-\xBF]{3})/x) {
		error("メッセージに日本語が含まれていません");
	}
}

#-----------------------------------------------------------
#  URL個数チェック
#-----------------------------------------------------------
sub urlnum {
	my $com = $in{comment};
	my ($num) = ($com =~ s|(https?://)|$1|ig);
	if ($num > $cf{urlnum}) {
		error("コメント中のURLアドレスは最大$cf{urlnum}個までです");
	}
}

#-----------------------------------------------------------
#  ホスト名取得
#-----------------------------------------------------------
sub get_host {
	# IP&ホスト取得
	my $host = $ENV{REMOTE_HOST};
	my $addr = $ENV{REMOTE_ADDR};
	
	if ($cf{gethostbyaddr} && ($host eq "" || $host eq $addr)) {
		$host = gethostbyaddr(pack("C4",split(/\./,$addr)), 2);
	}
	
	# IPチェック
	my $flg;
	foreach ( split(/\s+/,$cf{deny_addr}) ) {
		s/\./\\\./g;
		s/\*/\.\*/g;
		
		if ($addr =~ /^$_/i) { $flg = 1; last; }
	}
	if ($flg) {
		error("アクセスを許可されていません");
	
	# ホストチェック
	} elsif ($host) {
		foreach ( split(/\s+/, $cf{deny_host}) ) {
			s/\./\\\./g;
			s/\*/\.\*/g;
			
			if ($host =~ /$_$/i) { $flg = 1; last; }
		}
		if ($flg) {
			error("アクセスを許可されていません");
		}
	}
	$host ||= $addr;
	return ($host,$addr);
}

#-----------------------------------------------------------
#  crypt暗号
#-----------------------------------------------------------
sub encrypt {
	my $in = shift;
	
	my @wd = ('a'..'z', 'A'..'Z', '0'..'9', '.', '/');
	my $salt = $wd[int(rand(@wd))] . $wd[int(rand(@wd))];
	crypt($in,$salt) || crypt ($in,'$1$' . $salt);
}

#-----------------------------------------------------------
#  crypt照合
#-----------------------------------------------------------
sub decrypt {
	my ($in, $dec) = @_;
	
	my $salt = $dec =~ /^\$1\$(.*)\$/ ? $1 : substr($dec, 0, 2);
	if (crypt($in, $salt) eq $dec || crypt($in, '$1$' . $salt) eq $dec) {
		return 1;
	} else {
		return 0;
	}
}

#-----------------------------------------------------------
#  完了メッセージ
#-----------------------------------------------------------
sub message {
	my ($msg) = @_;
	my $bbs = $in{bbs} == 1 ? 1 : 0;
	
	open(IN,"$cf{tmpldir}/msg.html") or error("open err: msg.html");
	my $tmpl = join('',<IN>);
	close(IN);
	
	$tmpl =~ s/!bbs_cgi!/$cf{bbs_cgi}/g;
	$tmpl =~ s/!message!/$msg/g;
	$tmpl =~ s/!bbs!/$bbs/g;
	$tmpl =~ s|!bbs_css!|$cf{cmnurl}/bbs.css|g;
	$tmpl =~ s|!bbs_js!|$cf{cmnurl}/bbs.js|g;
	
	print "Content-type: text/html; charset=utf-8\n\n";
	print $tmpl;
	exit;
}

#-----------------------------------------------------------
#  クッキー発行
#-----------------------------------------------------------
sub set_cookie {
	my @data = @_;
	
	my ($sec,$min,$hour,$mday,$mon,$year,$wday,undef,undef) = gmtime(time + 60*24*60*60);
	my @mon  = qw|Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec|;
	my @week = qw|Sun Mon Tue Wed Thu Fri Sat|;
	
	# 時刻フォーマット
	my $gmt = sprintf("%s, %02d-%s-%04d %02d:%02d:%02d GMT",
				$week[$wday],$mday,$mon[$mon],$year+1900,$hour,$min,$sec);
	
	# URLエンコード
	my $cook;
	foreach (@data) {
		s/(\W)/sprintf("%%%02X", unpack("C", $1))/eg;
		$cook .= "$_<>";
	}
	
	print "Set-Cookie: $cf{cookie_id}=$cook; expires=$gmt\n";
}

#-----------------------------------------------------------
#  添付アップロード
#-----------------------------------------------------------
sub upload {
	my $num = shift;
	
	# サムネイル機能
	require './lib/thumb.pl' if ($cf{thumbnail});
	
	# 拡張子取得
	my $ex = $cgi->param_filename('upfile') =~ /(\.[^\\\/:\.]+)$/ ? $1 : error("拡張子不明");
	$ex =~ tr/A-Z/a-z/;
	if ($ex eq '.jpeg') { $ex = '.jpg'; }
	
	# ファイルチェック
	check_upl($ex);
	
	# 添付ファイル定義
	my $upfile = "$cf{imgdir}/$num$ex";
	
	# アップロード書き込み
	my $buf;
	open(UP,"+> $upfile") or error("up err: $upfile");
	binmode(UP);
	print UP $in{upfile};
	close(UP);
	
	# パーミッション付与
	chmod(0666,$upfile);
	
	# 画像サイズ取得
	my ($flg,$w,$h);
	if ($ex eq ".jpg") { ($w,$h) = j_size($upfile); $flg++; }
	elsif ($ex eq ".gif") { ($w,$h) = g_size($upfile); $flg++; }
	elsif ($ex eq ".png") { ($w,$h) = p_size($upfile); $flg++; }
	
	# サムネイル化
	if ($flg && $cf{thumbnail}) {
		($w,$h) = resize($w,$h);
		my $thumb = "$cf{imgdir}/$num-s$ex";
		make_thumb($upfile,$thumb,$w,$h);
	}
	
	# 結果を返す
	return ($ex,$w,$h);
}

#-----------------------------------------------------------
#  JPEGサイズ認識
#-----------------------------------------------------------
sub j_size {
	my $jpg = shift;
	
	my ($h, $w, $t);
	open(IMG,"$jpg");
	binmode(IMG);
	read(IMG,$t,2);
	while (1) {
		read(IMG, $t, 4);
		my ($m,$c,$l) = unpack("a a n",$t);
		
		if ($m ne "\xFF") {
			$w = $h = 0;
			last;
		} elsif ((ord($c) >= 0xC0) && (ord($c) <= 0xC3)) {
			read(IMG, $t, 5);
			($h, $w) = unpack("xnn",$t);
			last;
		} else {
			read(IMG,$t,($l - 2));
		}
	}
	close(IMG);
	
	return ($w,$h);
}

#-----------------------------------------------------------
#  GIFサイズ認識
#-----------------------------------------------------------
sub g_size {
	my $gif = shift;
	
	my $data;
	open(IMG,"$gif");
	binmode(IMG);
	sysread(IMG,$data,10);
	close(IMG);
	
	if ($data =~ /^GIF/) { $data = substr($data,-4); }
	my $w = unpack("v",substr($data,0,2));
	my $h = unpack("v",substr($data,2,2));
	
	return ($w,$h);
}

#-----------------------------------------------------------
#  PNGサイズ認識
#-----------------------------------------------------------
sub p_size {
	my $png = shift;
	
	my $data;
	open(IMG,"$png");
	binmode(IMG);
	read(IMG,$data,24);
	close(IMG);
	
	my $w = unpack("N",substr($data,16,20));
	my $h = unpack("N",substr($data,20,24));
	
	return ($w,$h);
}

#-----------------------------------------------------------
#  ファイルチェック
#-----------------------------------------------------------
sub check_upl {
	my ($ext) = @_;
	
	# mimeタイプ
	my $mime = $cgi->param_mime('upfile');
	
	my $flg;
	if ($cf{ok_gif}) {
		if ($mime =~ /^image\/gif$/i and $ext eq '.gif') { $flg++; }
	}
	if (!$flg and $cf{ok_jpeg}) {
		if ($mime =~ /^image\/p?jpe?g$/i and $ext eq '.jpg') { $flg++; }
	}
	if (!$flg and $cf{ok_pdf}) {
		if ($mime =~ /^application\/pdf$/i and $ext eq '.pdf') { $flg++; }
	}
	if (!$flg and $cf{ok_zip}) {
		if ($mime =~ /^application\/(x-)?zip(-compressed)?$/i and $ext eq '.zip') { $flg++; }
	}
	if (!$flg and $cf{ok_text}) {
		if ($mime =~ /^text\/plain$/i and $ext =~ /^\.te?xt$/) { $flg++; }
	}
	if (!$flg and $cf{ok_word}) {
		if ($mime =~ /^application\/(vnd\.)?ms-?word$/i and $ext eq '.doc') { $flg++; }
		elsif ($mime =~ /^application\/vnd\.openxmlformats-officedocument\.wordprocessingml\.document$/i and $ext eq '.docx') { $flg++; }
	}
	if (!$flg and $cf{ok_excel}) {
		if ($mime =~ /^application\/(vnd\.)?ms-?excel$/i and $ext eq '.xls') { $flg++; }
		elsif ($mime =~ /^application\/vnd\.openxmlformats-officedocument\.spreadsheetml\.sheet$/i and $ext eq '.xlsx') { $flg++; }
	}
	if (!$flg and $cf{ok_ppt}) {
		if ($mime =~ /^application\/(vnd\.)?ms-?powerpoint$/i and $ext eq '.ppt') { $flg++; }
		elsif ($mime =~ /^application\/vnd\.openxmlformats-officedocument\.presentationml\.presentation$/i and $ext eq '.pptx') { $flg++; }
	}
	
	if (!$flg) { error('このファイルは取り扱いできません'); }
}

#-----------------------------------------------------------
#  mimeエンコード
#  [quote] http://www.din.or.jp/~ohzaki/perl.htm#JP_Base64
#-----------------------------------------------------------
sub mime_unstructured_header {
  my $oldheader = shift;
  jcode::convert(\$oldheader,'euc','utf8');
  my ($header,@words,@wordstmp,$i);
  my $crlf = $oldheader =~ /\n$/;
  $oldheader =~ s/\s+$//;
  @wordstmp = split /\s+/, $oldheader;
  for ($i = 0; $i < $#wordstmp; $i++) {
    if ($wordstmp[$i] !~ /^[\x21-\x7E]+$/ and
	$wordstmp[$i + 1] !~ /^[\x21-\x7E]+$/) {
      $wordstmp[$i + 1] = "$wordstmp[$i] $wordstmp[$i + 1]";
    } else {
      push(@words, $wordstmp[$i]);
    }
  }
  push(@words, $wordstmp[-1]);
  foreach my $word (@words) {
    if ($word =~ /^[\x21-\x7E]+$/) {
      $header =~ /(?:.*\n)*(.*)/;
      if (length($1) + length($word) > 76) {
	$header .= "\n $word";
      } else {
	$header .= $word;
      }
    } else {
      $header = add_encoded_word($word, $header);
    }
    $header =~ /(?:.*\n)*(.*)/;
    if (length($1) == 76) {
      $header .= "\n ";
    } else {
      $header .= ' ';
    }
  }
  $header =~ s/\n? $//mg;
  $crlf ? "$header\n" : $header;
}
sub add_encoded_word {
  my ($str, $line) = @_;
  my $result;
  my $ascii = '[\x00-\x7F]';
  my $twoBytes = '[\x8E\xA1-\xFE][\xA1-\xFE]';
  my $threeBytes = '\x8F[\xA1-\xFE][\xA1-\xFE]';
  while (length($str)) {
    my $target = $str;
    $str = '';
    if (length($line) + 22 +
	($target =~ /^(?:$twoBytes|$threeBytes)/o) * 8 > 76) {
      $line =~ s/[ \t\n\r]*$/\n/;
      $result .= $line;
      $line = ' ';
    }
    while (1) {
      my $encoded = '=?ISO-2022-JP?B?' .
      b64encode(jcode::jis($target,'euc','z')) . '?=';
      if (length($encoded) + length($line) > 76) {
	$target =~ s/($threeBytes|$twoBytes|$ascii)$//o;
	$str = $1 . $str;
      } else {
	$line .= $encoded;
	last;
      }
    }
  }
  $result . $line;
}
# [quote] http://www.tohoho-web.com/perl/encode.htm
sub b64encode {
    my $buf = shift;
    my ($mode,$tmp,$ret);
    my $b64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                . "abcdefghijklmnopqrstuvwxyz"
                . "0123456789+/";
	
    $mode = length($buf) % 3;
    if ($mode == 1) { $buf .= "\0\0"; }
    if ($mode == 2) { $buf .= "\0"; }
    $buf =~ s/(...)/{
        $tmp = unpack("B*", $1);
        $tmp =~ s|(......)|substr($b64, ord(pack("B*", "00$1")), 1)|eg;
        $ret .= $tmp;
    }/eg;
    if ($mode == 1) { $ret =~ s/..$/==/; }
    if ($mode == 2) { $ret =~ s/.$/=/; }
    
    return $ret;
}

#-----------------------------------------------------------
#  文字数カウント for UTF-8
#-----------------------------------------------------------
sub count_str {
	my ($str) = @_;
	
	# UTF-8定義
	my $byte1 = '[\x00-\x7f]';
	my $byte2 = '[\xC0-\xDF][\x80-\xBF]';
	my $byte3 = '[\xE0-\xEF][\x80-\xBF]{2}';
	my $byte4 = '[\xF0-\xF7][\x80-\xBF]{3}';
	
	my $i = 0;
	while ($str =~ /($byte1|$byte2|$byte3|$byte4)/gx) {
		$i++;
	}
	return $i;
}


1;

