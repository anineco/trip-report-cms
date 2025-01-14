# モジュール宣言/変数初期化
use strict;
my %cf;
#┌─────────────────────────────────
#│ LimeCounter : init.cgi - 2013/08/14
#│ Copyright (c) KentWeb
#│ http://www.kent-web.com/
#└─────────────────────────────────
$cf{version} = 'LimeCounter v5.01';
#┌─────────────────────────────────
#│ [注意事項]
#│ 1. このスクリプトはフリーソフトです。このスクリプトを使用した
#│    いかなる損害に対して作者は一切の責任を負いません。
#│ 2. 設置に関する質問はサポート掲示板にお願いいたします。
#│    直接メールによる質問は一切お受けいたしておりません。
#└─────────────────────────────────
#
# ▼ページカウンタの記述例
# <img src="http://www.example.com/lime/lime.cgi?[ID]">
#
# ▼ダウンロードカウンタの記述例
# <a href="http://www.example.com/lime/lime.cgi?[ID]">ダウンロード</a>
#
# ▼集計リストの閲覧
# http://www.example.com/lime/list.cgi

#===========================================================
# ■ 設定項目
#===========================================================

# 管理用パスワード（英数字で指定）
$cf{password} = 'K32532';

# カテゴリー
# → カテゴリを使用しない場合は空にする : $cf{categ} = [];
#$cf{categ} = ['分類A','分類C','分類C'];
$cf{categ} = ['その他','山行記録'];

# インデックスファイル【サーバパス】
$cf{idxfile} = './data/lime.log';

# ログディレクトリ【サーバパス】
$cf{logdir} = './data/log';

# テンプレートディレクトリ
$cf{tmpldir} = './tmpl';

# IPチェックによる重複カウント防止 (0=no 1=yes)
$cf{ip_chk} = 1;

# カウンタ形式
#  1 : ページカウンタ
#  2 : ダウンロードカウンタ (ジャンプはLocationヘッダ)
#  3 : ダウンロードカウンタ (ジャンプはMETAタグ)
$cf{type} = 1;

# 集計プログラム【URLパス】
$cf{list_cgi} = './list.cgi';

# 管理プログラム【URLパス】
$cf{admin_cgi} = './admin.cgi';

# 円グラフの3D表示
# 0=no 1=yes
$cf{solid} = 0;

# 集計リストからの戻り先【URLパス】
$cf{homepage} = '../index.html';

# 集計リストグラフ画像【URLパス】
$cf{graph} = './img/graph.gif';

# 管理画面の最大受理サイズ（バイト）
$cf{maxdata} = 10240;

#===========================================================
# ■ 設定完了
#===========================================================

# 設定値を返す
sub init {
	return %cf;
}

#-----------------------------------------------------------
#  フォームデコード
#-----------------------------------------------------------
sub parse_form {
	my ($buf,%in);
	if ($ENV{REQUEST_METHOD} eq "POST") {
		error('受理できません') if ($ENV{CONTENT_LENGTH} > $cf{maxdata});
		read(STDIN, $buf, $ENV{CONTENT_LENGTH});
	} else {
		$buf = $ENV{QUERY_STRING};
	}
	foreach ( split(/&/, $buf) ) {
		my ($key,$val) = split(/=/);
		$val =~ tr/+/ /;
		$val =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("H2", $1)/eg;

		# 無効化
		$val =~ s/&/&amp;/g;
		$val =~ s/</&lt;/g;
		$val =~ s/>/&gt;/g;
		$val =~ s/"/&quot;/g;
		$val =~ s/'/&#39;/g;
		$val =~ s/[\r\n]//g;

		$in{$key} .= "\0" if (defined($in{$key}));
		$in{$key} .= $val;
	}
	return %in;
}

#-----------------------------------------------------------
#  桁区切り
#-----------------------------------------------------------
sub comma {
	local($_) = @_;

	1 while s/(.*\d)(\d\d\d)/$1,$2/;
	$_;
}



1;

