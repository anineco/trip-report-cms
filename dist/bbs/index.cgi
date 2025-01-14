#!/usr/local/bin/perl

#┌─────────────────────────────────
#│ JOYFUL NOTE : joyful.cgi - 2021/07/24
#│ copyright (c) KentWeb, 1997-2021
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

# 処理分岐
if ($in{mode} eq 'find') { find_data(); }
if ($in{mode} eq 'note') { note_page(); }
if ($in{mode} eq 'past') { past_data(); }
if ($in{mode} eq 'view') { view_page(); }
bbs_list();

#-----------------------------------------------------------
#  記事表示部
#-----------------------------------------------------------
sub bbs_list {
	# 返信フォーム
	$in{res}  =~ s/\D//g;
	$in{read} =~ s/\D//g;
	res_form($in{res}) if ($in{res} || $in{read});
	
	# トピック表示
	bbs_topic() if ($in{bbs} == 1);
	
	# ページ数定義
	my $pg = $in{pg} || 0;
	
	# 記事展開
	my ($i,@log,%res,%nam,%sub,%dat,%com,%url,%col,%ext,%imw,%imh);
	open(IN,"$cf{datadir}/log.cgi") or error("open err: log.cgi");
	my $top = <IN>;
	while (<IN>) {
		my ($no,$reno,$date,$name,$eml,$sub,$com,$url,$host,$pw,$col,$ext,$w,$h,$chk) = split(/<>/);
		
		++$i if (!$reno);
		next if ($i < $pg + 1);
		next if ($i > $pg + $cf{max_thread});
		
		# 親記事
		if (!$reno) {
			push(@log,$no);
		# レス記事
		} else {
			$res{$reno} .= "$no,";
		}
		# リンク
		$name = qq|<a href="mailto:$eml">$name</a>| if ($eml);
		$url &&= qq|<a href="$url" target="_blank"><img src="$cf{cmnurl}/home.png" alt="Home" class="icon"></a>|;
		$com = auto_link($com) if ($cf{auto_link});
		
		# ハッシュ化
		$nam{$no} = $name;
		$sub{$no} = $sub;
		$dat{$no} = $date;
		$com{$no} = $com;
		$col{$no} = $col;
		$url{$no} = $url;
		if ($ext) {
			if ($cf{img_check} && $chk eq '0') {
				$ext{$no} = "hide";
			} else {
				$ext{$no} = $ext;
				$imw{$no} = $w;
				$imh{$no} = $h;
			}
		}
	}
	close(IN);
	
	# 繰越ボタン作成
	my $page_btn = make_pgbtn($i,$pg,'',$cf{max_thread});
	
	# クッキー取得
	my @cook = get_cookie();
	$cook[2] ||= 'http://';
	
	# 色選択ボタン
	my @col = split(/\s+/,$cf{colors});
	my $color;
	foreach (0 .. $#col) {
		if ($_ == $cook[3]) {
			$color .= qq|<input type="radio" name="color" value="$_" checked>|;
		} else {
			$color .= qq|<input type="radio" name="color" value="$_">|;
		}
		$color .= qq|<span style="color:$col[$_]">■</span>\n|;
	}
	
	# テンプレート読込
	open(IN,"$cf{tmpldir}/bbs.html") or error("open err: bbs.html");
	my $tmpl = join('',<IN>);
	close(IN);
	
	$tmpl =~ s/!bbs_title!/$cf{bbs_title}/g;
	$tmpl =~ s|!icon:(\w+\.\w+)!|<img src="$cf{cmnurl}/$1" alt="$1" class="icon">|g;
	$tmpl =~ s|!bbs_css!|$cf{cmnurl}/bbs.css|g;
	$tmpl =~ s|!bbs_js!|$cf{cmnurl}/bbs.js|g;
	
	open(IN,"$cf{tmpldir}/res.html") or error("open err: res.html");
	my $resloop = join('',<IN>);
	close(IN);
	
	$resloop =~ s|!icon:(\w+\.\w+)!|<img src="$cf{cmnurl}/$1" alt="$1" class="icon">|g;
	
	# テンプレート分割
	my ($head,$loop,$foot) = $tmpl =~ m|(.+)<!-- loop -->(.+?)<!-- /loop -->(.+)|s
			? ($1,$2,$3)
			: error("テンプレート不正");
	
	# 画像認証作成
	my ($str_plain,$str_crypt);
	if ($cf{use_captcha} > 0) {
		require $cf{captcha_pl};
		($str_plain,$str_crypt) = cap::make($cf{captcha_key},$cf{cap_len});
	} else {
		$head =~ s|<!-- captcha -->.+?<!-- /captcha -->||s;
	}
	
	# 文字置換
	for ($head,$foot) {
		s/!([a-z]+_cgi)!/$cf{$1}/g;
		s/!homepage!/$cf{homepage}/g;
		s/!page_btn!/$page_btn/g;
		s/!name!/$cook[0]/;
		s/!email!/$cook[1]/;
		s/!url!/$cook[2]/;
		s/!str_crypt!/$str_crypt/g;
		s/!color!/$color/g;
		s/!sub!//g;
		s/!reno!//g;
	}
	
	# ヘッダ表示
	print "Content-type: text/html; charset=utf-8\n\n";
	print $head;
	
	# 記事表示
	for (@log) {
		# レス
		my $res;
		foreach my $r ( split(/,/, $res{$_}) ) {
			# 添付
			$com{$r} = qq|<span style="color:$col[$col{$r}]">$com{$r}</span>|;
			if (defined($ext{$r})) {
				$com{$r} = att_file($r,$com{$r},$ext{$r},$imw{$r},$imh{$r});
			}
			my $tmp = $resloop;
			$tmp =~ s/!sub!/$sub{$r}/g;
			$tmp =~ s/!name!/$nam{$r}/g;
			$tmp =~ s/!url!/$url{$r}/g;
			$tmp =~ s/!date!/$dat{$r}/g;
			$tmp =~ s/!num!/$r/g;
			$tmp =~ s/!comment!/$com{$r}/g;
			$res .= $tmp;
		}
		# 添付
		$com{$_} = qq|<span style="color:$col[$col{$_}]">$com{$_}</span>|;
		if (defined($ext{$_})) {
			$com{$_} = att_file($_,$com{$_},$ext{$_},$imw{$_},$imh{$_});
		}
		my $tmp = $loop;
		$tmp =~ s/!sub!/$sub{$_}/g;
		$tmp =~ s/!name!/$nam{$_}/g;
		$tmp =~ s/!url!/$url{$_}/g;
		$tmp =~ s/!date!/$dat{$_}/g;
		$tmp =~ s/!num!/$_/g;
		$tmp =~ s/!comment!/$com{$_}/g;
		$tmp =~ s/!bbs_cgi!/$cf{bbs_cgi}/g;
		$tmp =~ s|<!-- res -->|<div class="ta-r">$res</div>|g if ($res);
		print $tmp;
	}
	
	# フッタ
	footer($foot);
}

#-----------------------------------------------------------
#  返信フォーム
#-----------------------------------------------------------
sub res_form {
	my $resnum = $in{res} ? $in{res} : $in{read};
#	my $bbs = $in{bbs} == 1 ? 1 : 0;
	
	my ($flg,$resub,@res,%nam,%sub,%dat,%com,%url,%ext,%chk,%col,%imw,%imh);
	open(IN,"$cf{datadir}/log.cgi");
	my $top = <IN>;
	while (<IN>) {
		my ($no,$reno,$date,$name,$eml,$sub,$com,$url,$host,$pw,$col,$ext,$w,$h,$chk) = split(/<>/);
		
		if ($resnum == $no) {
			$flg = 1;
			
			# タイトル名
			if ($sub =~ /^Re:/) {
				$resub = $sub;
			} else {
				$resub = "Re: $sub";
			}
		
		} elsif ($resnum == $reno) {
			push(@res,$no);
		} else {
			next;
		}
		# リンク
		$name = qq|<a href="mailto:$eml">$name</a>| if ($eml);
		$url &&= qq|<a href="$url" target="_blank"><img src="$cf{cmnurl}/home.png" class="icon" alt="Home"></a>|;
		$com = auto_link($com) if ($cf{auto_link});
		
		$nam{$no} = $name;
		$sub{$no} = $sub;
		$dat{$no} = $date;
		$com{$no} = $com;
		$col{$no} = $col;
		$url{$no} = $url;
		$chk{$no} = $chk;
		if ($ext) {
			if ($cf{img_check} && $chk eq '0') {
				$ext{$no} = "hide";
			} else {
				$ext{$no} = $ext;
				$imw{$no} = $w;
				$imh{$no} = $h;
			}
		}
	}
	close(IN);
	
	if (!$flg) { error("不正な返信要求です"); }
	
	# クッキー取得
	my @cook = get_cookie();
	$cook[2] ||= 'http://';
	
	# 色選択ボタン
	my @col = split(/\s+/,$cf{colors});
	my $color;
	foreach (0 .. $#col) {
		if ($_ == $cook[3]) {
			$color .= qq|<input type="radio" name="color" value="$_" checked>|;
		} else {
			$color .= qq|<input type="radio" name="color" value="$_">|;
		}
		$color .= qq|<span style="color:$col[$_]">■</span>\n|;
	}
	
	# テンプレート読込
	my $file = $in{read} ? 'topic2.html' : 'bbs.html';
	open(IN,"$cf{tmpldir}/$file") or error("open err: $file");
	my $tmpl = join('',<IN>);
	close(IN);
	
	$tmpl =~ s|!icon:(\w+\.\w+)!|<img src="$cf{cmnurl}/$1" alt="$1" class="icon">|g;
	$tmpl =~ s|!bbs_css!|$cf{cmnurl}/bbs.css|g;
	$tmpl =~ s|!bbs_js!|$cf{cmnurl}/bbs.js|g;
	$tmpl =~ s/!bbs!/$in{bbs} eq '' ? 0 : $in{bbs}/eg;
	$tmpl =~ s/!pg!/$in{pg} eq '' ? 0 : $in{pg}/eg;
	
	open(IN,"$cf{tmpldir}/res.html") or error("open err: res.html");
	my $resloop = join('',<IN>);
	close(IN);
	
	$resloop =~ s|!icon:(\w+\.\w+)!|<img src="$cf{cmnurl}/$1" alt="$1" class="icon">|g;
	
	# 過去ログ
#	$tmpl =~ s/<!-- past -->.+<!-- past -->//s if ($cf{pastkey} == 0);
	
	# テンプレート分割
		my ($head,$loop,$foot) = $tmpl =~ m|(.+)<!-- loop -->(.+)<!-- /loop -->(.+)|s
			? ($1,$2,$3)
			: error("テンプレート不正");
	
	# 画像認証作成
	my ($str_plain,$str_crypt);
	if ($cf{use_captcha} > 0) {
		require $cf{captcha_pl};
		($str_plain,$str_crypt) = cap::make($cf{captcha_key},$cf{cap_len});
	} else {
		$head =~ s|<!-- captcha -->.+?<!-- /captcha -->||s;
	}
	
	# 文字置換
	for ($head, $foot) {
		s/!bbs_title!/$cf{bbs_title}/g;
		s/!([a-z]+_cgi)!/$cf{$1}/g;
		s/!homepage!/$cf{homepage}/g;
		s/!name!/$cook[0]/;
		s/!email!/$cook[1]/;
		s/!url!/$cook[2]/;
		s/!str_crypt!/$str_crypt/g;
		s/!color!/$color/g;
		s/!sub!/$resub/g;
		s/!reno!/$resnum/g;
		s/!counter!//g;
		s/!page_btn!//g;
	}
	
	# ヘッダ表示
	print "Content-type: text/html; charset=utf-8\n\n";
	print $head;
	
	# レス
	my $res;
	foreach my $r (@res) {
		# 添付
		$com{$r} = qq|<span style="color:$col[$col{$r}]">$com{$r}</span>|;
		if (defined($ext{$r})) {
			$com{$r} = att_file($r,$com{$r},$ext{$r},$imw{$r},$imh{$r});
		}
		# 文字置換
		my $tmp = $resloop;
		$tmp =~ s/!sub!/$sub{$r}/g;
		$tmp =~ s/!name!/$nam{$r}/g;
		$tmp =~ s/!date!/$dat{$r}/g;
		$tmp =~ s/!url!/$url{$r}/g;
		$tmp =~ s/!num!/$r/g;
		$tmp =~ s|!comment!|$com{$r}|g;
		$res .= $tmp;
	}
	
	# 添付
	$com{$resnum} = qq|<span style="color:$col[$col{$resnum}]">$com{$resnum}</span>|;
	if (defined($ext{$resnum})) {
		$com{$resnum} = att_file($resnum,$com{$resnum},$ext{$resnum},$imw{$resnum},$imh{$resnum});
	}
	# 文字置換
	$loop =~ s/!sub!/$sub{$resnum}/g;
	$loop =~ s/!name!/$nam{$resnum}/g;
	$loop =~ s/!date!/$dat{$resnum}/g;
	$loop =~ s/!url!/$url{$resnum}/g;
	$loop =~ s/!num!/$resnum/g;
	$loop =~ s/!comment!/$com{$resnum}/g;
	$loop =~ s/!bbs_cgi!/$cf{bbs_cgi}/g;
	$loop =~ s|<!-- res -->|<div class="ta-r">$res</div>|g if ($res);
	print $loop;
	
	# フッタ
	footer($foot);
}

#-----------------------------------------------------------
#  ワード検索
#-----------------------------------------------------------
sub find_data {
	# 条件/表示形式
	$in{cond} =~ s/\D//g;
	my $bbs = $in{bbs} == 1 ? 1 : 0;
	
	# 検索条件プルダウン
	my %op = (1 => 'AND', 0 => 'OR');
	my $op_cond;
	foreach (1,0) {
		if ($in{cond} eq $_) {
			$op_cond .= qq|<option value="$_" selected>$op{$_}</option>\n|;
		} else {
			$op_cond .= qq|<option value="$_">$op{$_}</option>\n|;
		}
	}
	
	# 検索実行
	my ($hit,@log) = search("$cf{datadir}/log.cgi") if ($in{word} ne '');
	
	# テンプレート
	open(IN,"$cf{tmpldir}/find.html") or error("open err: find.html");
	my $tmpl = join('',<IN>);
	close(IN);
	
	$tmpl =~ s/!bbs_title!/$cf{bbs_title}/g;
	$tmpl =~ s|!icon:(\w+\.\w+)!|<img src="$cf{cmnurl}/$1" alt="$1" class="icon">|g;
	$tmpl =~ s|!bbs_css!|$cf{cmnurl}/bbs.css|g;
	$tmpl =~ s|!bbs_js!|$cf{cmnurl}/bbs.js|g;
	
	# 分割
		my ($head,$loop,$foot) = $tmpl =~ m|(.+)<!-- loop -->(.+)<!-- /loop -->(.+)|s
			? ($1,$2,$3)
			: error("テンプレート不正");
	
	# 文字置換え
	for ($head, $foot) {
		s/!bbs_cgi!/$cf{bbs_cgi}/g;
		s/<!-- op_cond -->/$op_cond/;
		s/!word!/$in{word}/;
		s/!bbs!/$bbs/g;
	}
	
	# ヘッダ部
	print "Content-type: text/html; charset=utf-8\n\n";
	print $head;
	
	# ループ部
	foreach my $log (@log) {
		my ($no,$reno,$date,$name,$eml,$sub,$com,$url,$host,$pw,$col,$ext,$w,$h,$chk) = split(/<>/,$log);
		$name = qq|<a href="mailto:$eml">$name</a>| if ($eml);
		$com  = auto_link($com) if ($cf{auto_link});
		$url  = qq|<a href="$url" target="_blank"><img src="$cf{cmnurl}/home.png" class="icon" alt="Home"></a>| if ($url);
		if ($ext) {
			if ($cf{img_check} && $chk eq '0') {
				$ext = "hide";
			}
			$com = att_file($no,$com,$ext,$w,$h);
		}
		
		my $tmp = $loop;
		$tmp =~ s/!num!/$no/g;
		$tmp =~ s/!sub!/$sub/g;
		$tmp =~ s/!date!/$date/g;
		$tmp =~ s/!name!/$name/g;
		$tmp =~ s/!home!/$url/g;
		$tmp =~ s/!comment!/$com/g;
		print $tmp;
	}
	
	# フッタ
	footer($foot);
}

#-----------------------------------------------------------
#  検索実行
#-----------------------------------------------------------
sub search {
	my ($file,$list,$stat) = @_;
	
	# キーワードを配列化
	$in{word} =~ s/　/ /g;
	my @wd = split(/\s+/,$in{word});
	
	# UTF-8定義
	my $byte1 = '[\x00-\x7f]';
	my $byte2 = '[\xC0-\xDF][\x80-\xBF]';
	my $byte3 = '[\xE0-\xEF][\x80-\xBF]{2}';
	my $byte4 = '[\xF0-\xF7][\x80-\xBF]{3}';
	
	# 検索処理
	my ($i,@log);
	open(IN,"$file") or error("open err: $file");
	my $top = <IN> if (!$stat);
	while (<IN>) {
		my ($no,$reno,$date,$nam,$eml,$sub,$com,$url,$hos,$pw,$col,$ext,$w,$h,$chk) = split(/<>/);
		
		my $flg;
		foreach my $wd (@wd) {
			if ("$nam $eml $sub $com $url" =~ /^(?:$byte1|$byte2|$byte3|$byte4)*?\Q$wd\E/i) {
				$flg++;
				if ($in{cond} == 0) { last; }
			} else {
				if ($in{cond} == 1) { $flg = 0; last; }
			}
		}
		next if (!$flg);
		
		$i++;
		if ($list > 0) {
			next if ($i < $in{pg} + 1);
			next if ($i > $in{pg} + $list);
		}
		
		push(@log,$_);
	}
	close(IN);
	
	# 検索結果
	return ($i,@log);
}

#-----------------------------------------------------------
#  留意事項表示
#-----------------------------------------------------------
sub note_page {
	# 許可拡張子（表示用）
	my $ext = ext_file();
	
	open(IN,"$cf{tmpldir}/note.html") or error("open err: note.html");
	my $tmpl = join('',<IN>);
	close(IN);
	
	$tmpl =~ s/!bbs_title!/$cf{bbs_title}/g;
	$tmpl =~ s/!file!/$ext/g;
	$tmpl =~ s/!maxdata!/$cf{maxdata}バイト/g;
	$tmpl =~ s/!max_w!/$cf{max_img_w}/g;
	$tmpl =~ s/!max_h!/$cf{max_img_h}/g;
	$tmpl =~ s|!bbs_css!|$cf{cmnurl}/bbs.css|g;
	$tmpl =~ s|!bbs_js!|$cf{cmnurl}/bbs.js|g;
	
	print "Content-type: text/html; charset=utf-8\n\n";
	print $tmpl;
	exit;
}

#-----------------------------------------------------------
#  アルバム機能
#-----------------------------------------------------------
sub view_page {
	# ページ数/表示形式
	my $pg = $in{pg} || 0;
	my $bbs = $in{bbs} == 1 ? 1 : 0;
	
	# 画像サイズ再定義
	$cf{max_img_w} = $cf{alb_img_w};
	$cf{max_img_h} = $cf{alb_img_h};
	
	# テンプレート認識
	open(IN,"$cf{tmpldir}/view.html") or error("open err: view.html");
	my $tmpl = join('',<IN>);
	close(IN);
	
	$tmpl =~ s/!bbs_title!/$cf{bbs_title}/g;
	$tmpl =~ s|!bbs_css!|$cf{cmnurl}/bbs.css|g;
	$tmpl =~ s|!bbs_js!|$cf{cmnurl}/bbs.js|g;
	$tmpl =~ s|!cmnurl!|$cf{cmnurl}|g;
	
	# テンプレート分割
		my ($head,$loop,$foot) = $tmpl =~ m|(.+)<!-- loop -->(.+?)<!-- /loop -->(.+)|s
			? ($1,$2,$3)
			: error("テンプレート不正");
	
	# データ読み込み
	my ($i,@img);
	open(IN,"$cf{datadir}/log.cgi");
	my $top = <IN>;
	while (<IN>) {
		my ($no,$reno,$date,$name,$eml,$sub,$com,$url,$host,$pw,$col,$ex,$w,$h,$chk) = split(/<>/);
		next if ($cf{img_check} && $chk eq '0');
		next if ($ex !~ /(jpg|png|gif)$/);
		
		$i++;
		next if ($i < $pg + 1);
		next if ($i > $pg + $cf{max_albums});
		
		# 画像データ収集
		push(@img,"$no\t$sub\t$ex\t$w\t$h");
	}
	close(IN);
	
	# 繰越ボタン
	my $page_btn = make_pgbtn($i,$pg,'&amp;mode=view',$cf{max_albums});
	
	# 文字置換
	for ($head, $foot) {
		s/!([a-z]+_cgi)!/$cf{$1}/g;
		s/!page_btn!/$page_btn/g;
		s/!bbs!/$bbs/g;
	}
	
	# 画面展開
	print "Content-type: text/html; charset=utf-8\n\n";
	print $head;
	
	for (@img) {
		my ($no,$sub,$ex,$w,$h) = split(/\t/);
		($w,$h) = resize($w,$h);
		
		my $tmp = $loop;
		$tmp =~ s|!image!|<img src="$cf{imgurl}/$no$ex" alt="$sub" title="$sub" width="$w" height="$h">|;
		print $tmp;
	}
	
	# フッタ
	footer($foot);
}

#-----------------------------------------------------------
#  過去ログ画面
#-----------------------------------------------------------
sub past_data {
	# 過去ログ番号
	open(IN,"$cf{nofile}") or error("open err: $cf{nofile}");
	my $pastnum = <IN>;
	close(IN);
	
	my $pastnum = sprintf("%04d", $pastnum);
	$in{pno} =~ s/\D//g;
	$in{pno} ||= $pastnum;
	
	# プルダウンタグ作成
	my $op_pno;
	for ( my $i = $pastnum; $i > 0; $i-- ) {
		$i = sprintf("%04d", $i);
		
		if ($in{pno} == $i) {
			$op_pno .= qq|<option value="$i" selected>$i</option>\n|;
		} else {
			$op_pno .= qq|<option value="$i">$i</option>\n|;
		}
	}
	
	# ページ数
	my $pg = $in{pg} || 0;
	
	# 初期化
	my ($hit,$page_btn,$hit,@log,%res);
	
	# 対象ログ定義
	my $file = "$cf{pastdir}/" . sprintf("%04d", $in{pno}) . ".cgi";
	
	# ワード検索
	if ($in{find} && $in{word} ne '') {
		# 検索
		($hit,@log) = search($file,$in{list},'past');
		
		# 結果
		$page_btn = "検索結果：<b>$hit</b>件 &nbsp;&nbsp;" . pgbtn_old($hit,$in{pno},$pg,$in{list},'find');
	
	# ログ一覧
	} else {
		my $pg_max = $cf{max_thread} * 2;
		
		# 過去ログオープン
		my $i = 0;
		open(IN,"$file") or error("open err: $file");
		while(<IN>) {
			my ($no,$reno,$date,$nam,$eml,$sub,$com,$url,$hos,$pw,$col,$ext,$w,$h,$chk) = split(/<>/);
			++$i if ($reno eq '');
			next if ($i < $pg + 1);
			next if ($i > $pg + $pg_max);
			
			if ($reno) {
				$res{$reno} .= "$no<>$reno<>$date<>$nam<>$eml<>$sub<>$com<>$url<>$col\0";
				next;
			}
			push(@log,$_);
		}
		close(IN);
		
		# 繰越ボタン作成
		$page_btn = pgbtn_old($i,$in{pno},$pg,$pg_max);
	}
	
	# プルダウン作成（検索条件）
	my %op = make_op();
	
	# テンプレート読み込み
	open(IN,"$cf{tmpldir}/past.html") or error("open err: past.html");
	my $tmpl = join('',<IN>);
	close(IN);
	
	$tmpl =~ s|!icon:(\w+\.\w+)!|<img src="$cf{cmnurl}/$1" alt="$1" class="icon">|g;
	$tmpl =~ s/!bbs_title!/$cf{bbs_title}/g;
	$tmpl =~ s|!bbs_css!|$cf{cmnurl}/bbs.css|g;
	$tmpl =~ s|!bbs_js!|$cf{cmnurl}/bbs.js|g;
	
	open(IN,"$cf{tmpldir}/res.html") or error("open err: res.html");
	my $restmpl = join('', <IN>);
	close(IN);
	
	$restmpl =~ s|!icon:(\w+\.\w+)!|<img src="$cf{cmnurl}/$1" alt="$1" class="icon">|g;
	
	# テンプレート分割
		my ($head,$loop,$foot) = $tmpl =~ m|(.+)<!-- loop -->(.+)<!-- /loop -->(.+)|s
			? ($1,$2,$3)
			: error("テンプレート不正");
	
	if ($in{change}) { $in{word} = ''; }
	
	my @col = split(/\s+/,$cf{colors});
	
	# 文字置換
	for ($head, $foot) {
		s/!past_num!/$in{pno}/g;
		s/!bbs_url!//g;
		s/!([a-z]+_cgi)!/$cf{$1}/g;
		s/<!-- op_pno -->/$op_pno/g;
		s/<!-- op_(\w+) -->/$op{$1}/g;
		s/!word!/$in{word}/g;
		s/!page_btn!/$page_btn/g;
	}
	
	# 画面表示
	print "Content-type: text/html; charset=utf-8\n\n";
	print $head;
	
	foreach (@log) {
		my ($no,$reno,$date,$nam,$eml,$sub,$com,$url,$hos,$pw,$col,$ext,$w,$h,$chk) = split(/<>/);
		$nam = qq|<a href="mailto:$eml">$nam</a>| if ($eml);
		$com = auto_link($com) if ($cf{auto_link});
		$url = qq|<a href="$url" target="_blank"><img src="$cf{cmnurl}/home.png" class="icon" alt="Home"></a>| if ($url);
		
		# レス
		my $res;
		foreach my $log ( split(/\0/,$res{$no}) ) {
			my ($no,$reno,$date,$nam,$eml,$sub,$com,$url,$col) = split(/<>/, $log);
			$nam = qq|<a href="mailto:$eml">$nam</a>| if ($eml);
			$com = auto_link($com) if ($cf{auto_link});
			$url = qq|<a href="$url" target="_blank"><img src="$cf{cmnurl}/home.png" class="icon" alt="Home"></a>| if ($url);
			
			my $tmp = $restmpl;
			$tmp =~ s/!sub!/$sub/g;
			$tmp =~ s/!name!/$nam/g;
			$tmp =~ s/!date!/$date/g;
			$tmp =~ s/!url!/$url/g;
			$tmp =~ s/!num!/$no/g;
			$tmp =~ s/!comment!/<span style="color:$col[$col]">$com<\/span>/g;
			$res .= $tmp;
		}
		
		my $tmp = $loop;
		$tmp =~ s/!num!/$no/g;
		$tmp =~ s/!sub!/$sub/g;
		$tmp =~ s/!date!/$date/g;
		$tmp =~ s/!name!/$nam/g;
		$tmp =~ s/!url!/$url/g;
		$tmp =~ s/!comment!/$com/g;
		$tmp =~ s/<!-- res -->/<blockquote>$res<\/blockquote>/g if ($res);
		
		print $tmp;
	}
	
	# フッタ
	footer($foot);
}

#-----------------------------------------------------------
#  トピックス画面
#-----------------------------------------------------------
sub bbs_topic {
	# クッキー取得
	my @cook = get_cookie();
	$cook[2] ||= 'http://';
	
	# 色選択ボタン
	my @col = split(/\s+/,$cf{colors});
	my $color;
	foreach (0 .. $#col) {
		if ($_ == $cook[3]) {
			$color .= qq|<input type="radio" name="color" value="$_" checked>|;
		} else {
			$color .= qq|<input type="radio" name="color" value="$_">|;
		}
		$color .= qq|<span style="color:$col[$_]">■</span>\n|;
	}
	
	# ページ数
	my $pg = $in{pg} || 0;
	
	# データ認識
	my ($i,@log,%res,%last);
	open(IN,"$cf{datadir}/log.cgi");
	while(<IN>) {
		my ($no,$reno,$date,$name,$eml,$sub,$com,$url,$host,$pw,$col,$ext,$w,$h,$chk) = split(/<>/);
		if (!$reno) { $i++; }
		next if ($i < $pg + 1);
		next if ($i > $pg + $cf{max_topics});
		
		if ($reno) { $res{$reno}++; $last{$reno} = "$date<br>$name"; }
		else { $last{$no} = "$date<br>$name"; }
		
		push(@log,$_) if (!$reno);
	}
	close(IN);
	
	# 繰越ボタン作成
	my $pg_btn = make_pgbtn($i,$pg,'&amp;bbs=1',$cf{max_topics});
	
	# テンプレート読み込み
	open(IN,"$cf{tmpldir}/topic.html") or error("open err: topic.html");
	my $tmpl = join('',<IN>);
	close(IN);
	
	$tmpl =~ s|!bbs_css!|$cf{cmnurl}/bbs.css|g;
	$tmpl =~ s|!bbs_js!|$cf{cmnurl}/bbs.js|g;
	
	# 画像認証作成
	my ($str_plain,$str_crypt);
	if ($cf{use_captcha} > 0) {
		require $cf{captcha_pl};
		($str_plain,$str_crypt) = cap::make($cf{captcha_key},$cf{cap_len});
	} else {
		$tmpl =~ s|<!-- captcha -->.+?<!-- /captcha -->||s;
	}
	
	# 文字置換え
	$tmpl =~ s/!bbs_title!/$cf{bbs_title}/g;
	$tmpl =~ s/!([a-z]+_cgi)!/$cf{$1}/g;
	$tmpl =~ s/!page_btn!/$pg_btn/g;
	$tmpl =~ s/!homepage!/$cf{homepage}/g;
	$tmpl =~ s/!color!/$color/g;
	$tmpl =~ s/!sub!//g;
	$tmpl =~ s/!name!/$cook[0]/;
	$tmpl =~ s/!email!/$cook[1]/;
	$tmpl =~ s/!url!/$cook[2]/;
	$tmpl =~ s/!str_crypt!/$str_crypt/g;
	$tmpl =~ s/\?mode=(view|find)/?mode=$1&amp;bbs=1/g;
	
	# 分解
	my ($head,$loop,$foot) = $tmpl =~ m|(.+)<!-- loop -->(.+?)<!-- /loop -->(.+)|s
			? ($1,$2,$3)
			: error("テンプレート不正");
	
	# ヘッダ表示
	print "Content-type: text/html; charset=utf-8\n\n";
	print $head;
	
	# 親記事展開
	foreach (@log) {
		my ($no,$reno,$date,$name,$eml,$sub,$com,$url,$host,$pw,$col,$ext,$w,$h,$chk) = split(/<>/);
		
		if ($res{$no} eq '') { $res{$no} = 0; }
		
		my $tmp = $loop;
		$tmp =~ s/!topi-num!/$no/g;
		$tmp =~ s|!topi-ttl!|<a href="$cf{bbs_cgi}?read=$no&amp;bbs=1&amp;pg=$pg">$sub</a>|g;
		$tmp =~ s/!topi-nam!/$name/g;
		$tmp =~ s/!topi-res!/$res{$no}/g;
		$tmp =~ s/!topi-last!/$last{$no}/g;
		print $tmp;
	}
	
	# フッタ
	footer($foot);
}

#-----------------------------------------------------------
#  URLエンコード
#-----------------------------------------------------------
sub url_enc {
	local($_) = @_;
	
	s/(\W)/'%' . unpack('H2', $1)/eg;
	s/\s/+/g;
	$_;
}

#-----------------------------------------------------------
#  ペイジャー作成 [ 過去ログ ]
#-----------------------------------------------------------
sub pgbtn_old {
	my ($i,$pno,$pg,$list,$stat) = @_;
	
	# ページ繰越定義
	my $next = $pg + $list;
	my $back = $pg - $list;
	
	my $link;
	if ($stat eq 'find') {
		my $wd = url_enc($in{word});
		$link = "$cf{bbs_cgi}?mode=$in{mode}&amp;pno=$pno&amp;find=1&amp;word=$wd&amp;list=$list";
	} else {
		$link = "$cf{bbs_cgi}?mode=$in{mode}&amp;pno=$pno";
	}
	
	# ページ繰越ボタン作成
	my @pg;
	if ($back >= 0 || $next < $i) {
		my $flg;
		my ($w,$x,$y,$z) = (0,1,0,$i);
		while ($z > 0) {
			if ($pg == $y) {
				$flg++;
				push(@pg,qq!<span class="page active">$x</span>!);
			} else {
				push(@pg,qq!<a href="$link&amp;pg=$y" class="page gradient">$x</a>!);
			}
			$x++;
			$y += $list;
			$i -= $list;
			
			if ($flg) { $w++; }
			last if ($w >= 5 && @pg >= 10);
		}
	}
	while( @pg >= 11 ) { shift(@pg); }
	my $ret = join('', @pg);
	if ($back >= 0) {
		$ret = qq!<a href="$link&amp;pg=$back" class="page gradient">&laquo;</a>\n! . $ret;
	}
	if ($next < $i) {
		$ret .= qq!<a href="$link&amp;pg=$next" class="page gradient">&raquo;</a>\n!;
	}
	
	# 結果を返す
	return $ret ? qq|<div class="ta-c"><div class="pagination">$ret</div></div>| : '';
}

#-----------------------------------------------------------
#  プルダウン作成 [ 検索条件 ]
#-----------------------------------------------------------
sub make_op {
	my %op;
	my %cond = (1 => 'AND', 0 => 'OR');
	foreach (1,0) {
		if ($in{cond} eq $_) {
			$op{cond} .= qq|<option value="$_" selected>$cond{$_}</option>\n|;
		} else {
			$op{cond} .= qq|<option value="$_">$cond{$_}</option>\n|;
		}
	}
	for ( my $i = 10; $i <= 30; $i += 5 ) {
		if ($in{list} == $i) {
			$op{list} .= qq|<option value="$i" selected>$i件</option>\n|;
		} else {
			$op{list} .= qq|<option value="$i">$i件</option>\n|;
		}
	}
	return %op;
}

#-----------------------------------------------------------
#  自動リンク
#-----------------------------------------------------------
sub auto_link {
	my $text = shift;
	
	$text =~ s/(s?https?:\/\/([\w-.!~*'();\/?:\@=+\$,%#]|&amp;)+)/<a href="$1" target="_blank">$1<\/a>/g;
	return $text;
}

#-----------------------------------------------------------
#  フッター
#-----------------------------------------------------------
sub footer {
	my $foot = shift;
	
	# 著作権表記（削除・改変禁止）
	my $copy = <<EOM;
<p style="margin-top:2.5em;text-align:center;font-family:Verdana,Helvetica,Arial;font-size:10px;">
	- <a href="https://www.kent-web.com/" target="_top">JoyfulNote</a> -
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
#  ペイジャー作成
#-----------------------------------------------------------
sub make_pgbtn {
	my ($i,$pg,$stat,$max) = @_;
	
	# ページ繰越定義
	$max ||= 5;
	my $next = $pg + $max;
	my $back = $pg - $max;
	
	# ページ繰越ボタン作成
	my @pg;
	if ($back >= 0 || $next < $i) {
		my $flg;
		my ($w,$x,$y,$z) = (0,1,0,$i);
		while ($z > 0) {
			if ($pg == $y) {
				$flg++;
				push(@pg,qq!<span class="page active">$x</span>!);
			} else {
				push(@pg,qq!<a href="$cf{bbs_cgi}?pg=$y$stat" class="page gradient">$x</a>!);
			}
			$x++;
			$y += $max;
			$z -= $max;
			
			if ($flg) { $w++; }
			last if ($w >= 5 && @pg >= 10);
		}
	}
	while( @pg >= 11 ) { shift(@pg); }
	my $ret = join('', @pg);
	if ($back >= 0) {
		$ret = qq!<a href="$cf{bbs_cgi}?pg=$back$stat" class="page gradient">&laquo;</a>\n! . $ret;
	}
	if ($next < $i) {
		$ret .= qq!<a href="$cf{bbs_cgi}?pg=$next$stat" class="page gradient">&raquo;</a>\n!;
	}
	
	# 結果を返す
	return $ret ? qq|<div class="pagination">$ret</div>| : '';
}

#-----------------------------------------------------------
#  クッキー取得
#-----------------------------------------------------------
sub get_cookie {
	# クッキー取得
	my $cook = $ENV{HTTP_COOKIE};
	
	# 該当IDを取り出す
	my %cook;
	foreach ( split(/;/, $cook) ) {
		my ($key,$val) = split(/=/);
		$key =~ s/\s//g;
		$cook{$key} = $val;
	}
	
	# URLデコード
	my @cook;
	foreach ( split(/<>/,$cook{$cf{cookie_id}}) ) {
		s/%([0-9A-Fa-f][0-9A-Fa-f])/pack("H2", $1)/eg;
		s/[&"'<>]//g;
		
		push(@cook,$_);
	}
	return @cook;
}

#-----------------------------------------------------------
#  添付リンク
#-----------------------------------------------------------
sub att_file {
	my ($no,$com,$ex,$w,$h) = @_;
	
	# 未公開
	if ($ex eq 'hide') {
		$com .= qq|<p>[添付]: 認証待ち</p>|;
	
	# 画像のとき
	} elsif ($ex =~ /(jpg|png|gif)$/) {
		
		my $op;
		if (-f "$cf{imgdir}/$no-s$ex") {
			$op = qq|src="$cf{imgurl}/$no-s$ex"|;
		} else {
			($w,$h) = resize($w,$h);
			$op = qq|src="$cf{imgurl}/$no$ex" width="$w" height="$h"|;
		}
		
		# 画像はコメントの下
		if ($cf{image_position} == 1) {
			$com .= qq|<p><a href="$cf{imgurl}/$no$ex" target="_blank"><img $op alt="$no"></a></p>|;
		
		# 画像はコメントの左（廻り込み）
		} else {
			$com = qq|<a href="$cf{imgurl}/$no$ex" target="_blank"><img $op align="left" alt="$no"></a>$com<br clear="all">|;
		}
	
	# 画像以外のとき
	} else {
		my $size = -s "$cf{imgdir}/$no$ex" || 0;
		$com .= qq|<p>[<a href="$cf{imgurl}/$no$ex" target="_blank">添付</a>]: $size bytes</p>|;
	}
	
	return $com;
}

#-----------------------------------------------------------
#  取り扱いファイル
#-----------------------------------------------------------
sub ext_file {
	my $ext;
	foreach ( keys %cf ) {
		next if ($_ !~ /^ok_(\w+)/);
		my $file = $1;
		next if (!$cf{$_});
		
		$file =~ tr/a-z/A-Z/;
		$ext .= "$file, ";
	}
	$ext =~ s/, $//;
	
	return $ext;
}

#-----------------------------------------------------------
#  画像表示
#-----------------------------------------------------------
sub image {
	my ($no,$ex,$w,$h) = @_;
	
	my $image;
	if (-f "$cf{imgdir}/$no-s$ex") {
		$image = qq|<img src="$cf{imgurl}/$no-s$ex" alt="$no">|;
		
	} else {
		($w,$h) = resize($w,$h);
		$image = qq|<img src="$cf{imgurl}/$no$ex" width="$w" height="$h" alt="$no">|;
	}
	return qq|<a href="$cf{imgurl}/$no$ex" target="_blank">$image</a>\n|;
}

