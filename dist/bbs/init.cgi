# モジュール宣言/変数初期化
use strict;
my %cf;
#┌─────────────────────────────────
#│ JOYFUL NOTE : init.cgi - 2021/07/24
#│ copyright (c) kentweb, 1997-2021
#│ https://www.kent-web.com/
#└─────────────────────────────────
$cf{version} = 'JoyfulNote v7.3';
#┌─────────────────────────────────
#│ [注意事項]
#│ 1. このプログラムはフリーソフトです。このプログラムを使用した
#│    いかなる損害に対して作者は一切の責任を負いません。
#│ 2. 設置に関する質問はサポート掲示板にお願いいたします。
#│    直接メールによる質問は一切お受けいたしておりません。
#└─────────────────────────────────

#===========================================================
# ■ 設定項目
#===========================================================

# パスワード制限をする場合入室パスワード設定
# → 空欄の場合はパスワード制限なし
$cf{enter_pwd} = '';

# パスワード制限時のセッションの許容時間（分単位）
# → 入室後からアクセス可能時間
$cf{sestime} = 60;

# サムネイル画像を作成する（要：Image::Magick）
# → 縮小画像を自動生成し、画像記事の表示速度を軽くする機能
# 0=no 1=yes
$cf{thumbnail} = 1;

# 掲示板タイトル
$cf{bbs_title} = "あにねこ登山日誌 - 掲示板";

# アップロードファイル管理者チェック機能 (0=no 1=yes)
# → アップロードファイルは管理者がチェック後表示
$cf{img_check} = 0;

# 最大記事数 (親記事+レス記事も含めた数）
$cf{max} = 50;

# 返信がつくと親記事をトップへ移動 (0=no 1=yes)
$cf{topsort} = 1;

# 画像の位置
# 1 : コメントの下
# 2 : コメントの左（廻り込み）
$cf{image_position} = 2;

# 本体CGIのURL【URLパス】
$cf{bbs_cgi} = './index.cgi';

# 書込CGIのURL【URLパス】
$cf{regist_cgi} = './mt.cgi';

# 管理CGIのURL【URLパス】
$cf{admin_cgi} = './admin.cgi';

# データディレクトリ【サーバパス】
$cf{datadir} = './data';

# アップロードディレクトリ【サーバパス】
$cf{imgdir} = './img';

# アップロードディレクトリ【URLパス】
$cf{imgurl} = "./img";

# テンプレートディレクトリ【サーバパス】
$cf{tmpldir} = './tmpl';

# 共通ディレクトリ【URLパス】
$cf{cmnurl} = './cmn';

# 戻り先のURL【URLパス】
$cf{homepage} = "../index.html";

# 記事 [タイトル] 部の最大文字数
$cf{sub_len} = 30;

# 同一IPアドレスからの連続投稿時間（秒数）
# → 値を 0 にするとこの機能は無効になります
$cf{wait} = 30;

# １画面当たりの記事表示数 (親記事基準)
# → 順に、スレッド表示、トピック表示、アルバム表示
$cf{max_thread} = 5;
$cf{max_topics} = 10;
$cf{max_albums} = 10;

# メール通知機能
# → 0=no  1=yes
$cf{mailing} = 1;

# メール通知先アドレス（メール通知する場合）
$cf{mailto} = 'anineco@gmail.com';

# sendmailのパス（メール通知する場合）
$cf{sendmail} = '/usr/sbin/sendmail';

# sendmailの -fコマンドが必要な場合
# 0=no 1=yes
$cf{sendm_f} = 0;

# 文字色の設定（半角スペースで区切る）
$cf{colors} = '#800000 #DF0000 #008040 #0000FF #C100C1 #FF80C0 #FF8040 #000080 #808000';

# URLの自動リンク (0=no 1=yes)
$cf{auto_link} = 1;

# アイコン画像【URLパス】
# → 順に [eメール] [ホームページ]
$cf{ico_mail} = "./icon/mail.gif";
$cf{ico_home} = "./icon/home.gif";

# ホスト取得方法
# 0 : gethostbyaddr関数を使わない
# 1 : gethostbyaddr関数を使う
$cf{gethostbyaddr} = 0;

# アクセス制限（半角スペースで区切る、アスタリスク可）
#  → 拒否ホスト名を記述（後方一致）【例】*.anonymizer.com
$cf{deny_host} = '';
#  → 拒否IPアドレスを記述（前方一致）【例】210.12.345.*
$cf{deny_addr} = '103.208.220.*';

# 禁止ワード
# → 投稿時禁止するワードをコンマで区切る
$cf{no_wd} = '';

# 日本語チェック（投稿時日本語が含まれていなければ拒否する）
# 0=No  1=Yes
$cf{jp_wd} = 1;

# URL個数チェック
# → 投稿コメント中に含まれるURL個数の最大値
$cf{urlnum} = 5;

# アップロードを許可するファイル（0=no 1=yes）
$cf{ok_text}  = 0;  # TEXT
$cf{ok_gif}   = 1;  # GIF
$cf{ok_jpeg}  = 1;  # JPEG
$cf{ok_excel} = 0;  # EXCEL
$cf{ok_word}  = 0;  # WORD
$cf{ok_ppt}   = 0;  # POWER POINT
$cf{ok_zip}   = 0;  # ZIP
$cf{ok_pdf}   = 0;  # PDF

# 投稿受理最大サイズ (bytes)
# → 例 : 102400 = 100KB
$cf{maxdata} = 1024000;

# 画像ファイルの最大表示の大きさ（単位：ピクセル）
# → これを超える画像は縮小表示します
$cf{max_img_w} = 240;
$cf{max_img_h} = 180;

# クッキーID名（特に変更しなくてよい）
$cf{cookie_id}  = "joyfulbbs";
$cf{cookie_id3} = "joyfulpwd";

# 管理パスワードの最大間違い制限
# → この回数以上パスワードを間違うとロックします
$cf{max_failpass} = 5;

# -------------------------------------------------------------- #
# [ 以下は「過去ログ」機能を使用する場合の設定 ]
#
# 過去ログ用NOファイル【サーバパス】
$cf{nofile}  = './data/pastno.dat';

# 過去ログのディレクトリ【サーバパス】
# → パスの最後に / をつけない
$cf{pastdir} = './data/past';

# 過去ログ１ファイルの行数
# → この行数を超えると次ページを自動生成します
$cf{pastmax} = 600;

# -------------------------------------------------------------- #
# [ 以下は「画像認証機能」機能を使用する場合の設定 ]
#
# 画像認証機能の使用
# 0 : しない
# 1 : ライブラリ版（pngren.pl）
# 2 : モジュール版（GD::SecurityImage + Image::Magick）→ Image::Magick必須
$cf{use_captcha} = 1;

# 認証用画像生成ファイル【URLパス】
$cf{captcha_cgi} = './captcha.cgi';

# 画像認証プログラム【サーバパス】
$cf{captcha_pl} = './lib/captcha.pl';
$cf{captsec_pl} = './lib/captsec.pl';
$cf{pngren_pl}  = './lib/pngren.pl';

# 画像認証機能用暗号化キー（暗号化/復号化をするためのキー）
# → 適当に変更してください。
$cf{captcha_key} = '04c3a00f';

# 投稿キー許容時間（分単位）
# → 投稿フォーム表示後、送信ボタンが押されるまでの可能時間。
$cf{cap_time} = 30;

# 投稿キーの文字数
# ライブラリ版 : 4～8文字で設定
# モジュール版 : 6～8文字で設定
$cf{cap_len} = 4;

# 画像/フォント格納ディレクトリ【サーバパス】
$cf{bin_dir} = './lib/bin';

# [ライブラリ版] 画像ファイル [ ファイル名のみ ]
$cf{si_png} = "stamp.png";

# [モジュール版] 画像フォント [ ファイル名のみ ]
$cf{font_ttl} = "tempest.ttf";

#===========================================================
# ■ 設定完了
#===========================================================

# 設定内容を返す
sub set_init { return %cf; }

#-----------------------------------------------------------
#  フォームデコード
#-----------------------------------------------------------
sub parse_form {
	my $cgi = shift;
	
	my %in;
	foreach ( $cgi->param() ) {
		my $val = $cgi->param($_);
		
		if ($_ ne 'upfile') {
			# 無効化
			$val =~ s/&/&amp;/g;
			$val =~ s/</&lt;/g;
			$val =~ s/>/&gt;/g;
			$val =~ s/"/&quot;/g;
			$val =~ s/'/&#39;/g;
			
			# 改行変換
			$val =~ s|\r\n|<br>|g;
			$val =~ s|[\n\r]|<br>|g;
		}
		
		$in{$_} = $val;
	}
	return %in;
}

#-----------------------------------------------------------
#  エラー画面
#-----------------------------------------------------------
sub error {
	my $err = shift;

	open(IN,"$cf{tmpldir}/error.html") or die;
	my $tmpl = join('',<IN>);
	close(IN);
	
	$tmpl =~ s/!error!/$err/g;
	$tmpl =~ s/!bbs_title!/$cf{bbs_title}/g;
	$tmpl =~ s|!bbs_css!|$cf{cmnurl}/bbs.css|g;
	$tmpl =~ s|!bbs_js!|$cf{cmnurl}/bbs.js|g;

	print "Status: 410 Gone\n";
	print "Content-type: text/html; charset=utf-8\n\n";
	print $tmpl;
	exit;
}

#-----------------------------------------------------------
#  画像リサイズ
#-----------------------------------------------------------
sub resize {
	my ($w,$h) = @_;
	
	# 画像表示縮小
	if ($w > $cf{max_img_w} || $h > $cf{max_img_h}) {
		my $w2 = $cf{max_img_w} / $w;
		my $h2 = $cf{max_img_h} / $h;
		my $key;
		if ($w2 < $h2) { $key = $w2; } else { $key = $h2; }
		$w = int ($w * $key) || 1;
		$h = int ($h * $key) || 1;
	}
	return ($w,$h);
}

#-----------------------------------------------------------
#  パスワード制限
#-----------------------------------------------------------
sub passwd {
	my %in = @_;
	
	# 入室フォーム指定のとき
	if ($in{mode} eq 'enter') { pwd_form(); }
	
	# 時間取得
	my $now = time;
	
	# ログインのとき
	if ($in{login}) {
		# 認証
		if ($in{pw} ne $cf{enter_pwd}) { error("認証できません"); }
		
		# セッション発行
		my @wd = (0 .. 9, 'a' .. 'z', 'A' .. 'Z', '_');
		my $ses;
		for (1 .. 25) {	$ses .= $wd[int(rand(@wd))]; }
		
		# セッション更新
		my @log;
		open(DAT,"+< $cf{datadir}/ses.cgi") or error("open err: ses.cgi");
		eval 'flock(DAT,2);';
		while(<DAT>) {
			chomp;
			my ($id,$time) = split(/\t/);
			next if ($now - $time > $cf{sestime} * 60);
			
			push(@log,"$_\n");
		}
		unshift(@log,"$ses\t$now\n");
		seek(DAT,0,0);
		print DAT @log;
		truncate(DAT,tell(DAT));
		close(DAT);
		
		# クッキー格納
		print "Set-Cookie: $cf{cookie_id3}=$ses\n";
	
	# セッション確認
	} else {
		
		# クッキー取得
		my $cook = $ENV{HTTP_COOKIE};
		
		# 該当IDを取り出す
		my %cook;
		foreach ( split(/;/,$cook) ) {
			my ($key,$val) = split(/=/);
			$key =~ s/\s//g;
			$cook{$key} = $val;
		}
		
		# クッキーなし
		if ($cook{$cf{cookie_id3}} eq '') { pwd_form(); }
		
		# ログオフのとき
		if ($in{mode} eq 'logoff') {
			
			my @log;
			open(DAT,"+< $cf{datadir}/ses.cgi") or error("open err: ses.cgi");
			eval 'flock(DAT,2);';
			while(<DAT>) {
				my ($id,undef) = split(/\t/);
				next if ($cook{$cf{cookie_id3}} eq $id);
				
				push(@log,$_);
			}
			seek(DAT,0,0);
			print DAT @log;
			truncate(DAT,tell(DAT));
			close(DAT);
			
			if ($ENV{PERLXS} eq "PerlIS") {
				print "HTTP/1.0 302 Temporary Redirection\r\n";
				print "Content-type: text/html\n";
			}
			print "Set-Cookie: $cf{cookie_id3}=;\n";
			print "Location: $cf{homepage}\n\n";
			exit;
		}
		
		# セッションチェック
		my $flg;
		open(DAT,"$cf{datadir}/ses.cgi") or error("open err: ses.cgi");
		while(<DAT>) {
			chomp;
			my ($id,$time) = split(/\t/);
			
			if ($cook{$cf{cookie_id3}} eq $id) {
				# 時間オーバー
				if ($now - $time > $cf{sestime} * 60) {
					$flg = -1;
				# OK
				} else {
					$flg = 1;
				}
				last;
			}
		}
		close(DAT);
		
		# 時間オーバー
		if ($flg == -1) {
			my $msg = qq|入室時間が経過しました。再度ログインしてください<br>\n|;
			$msg .= qq|[<a href="$cf{bbs_cgi}?mode=enter">ログイン</a>]\n|;
			error($msg);
		
		# セッション情報なし
		} elsif (!$flg) {
			pwd_form();
		}
	}
}

#-----------------------------------------------------------
#  入室画面
#-----------------------------------------------------------
sub pwd_form {
	open(IN,"$cf{tmpldir}/enter.html") or error('open err: enter.html');
	my $tmpl = join('',<IN>);
	close(IN);
	
	$tmpl =~ s/!bbs_cgi!/$cf{bbs_cgi}/g;
	$tmpl =~ s|!bbs_css!|$cf{cmnurl}/bbs.css|g;
	
	print "Content-type: text/html; charset=utf-8\n\n";
	footer($tmpl,'pform');
}


1;

