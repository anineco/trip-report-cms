# モジュール宣言/変数初期化
use strict;
use warnings;
use utf8;
my %cf;
#┌─────────────────────────────────
#│ アクセス解析システム
#│ Access Report : init.cgi - 2013/03/24
#│ Copyright (c) KentWeb
#│ http://www.kent-web.com/
#└─────────────────────────────────
$cf{version} = 'Access Report v5.5';
#┌─────────────────────────────────
#│ [注意事項]
#│ 1. このスクリプトはフリーソフトです。このスクリプトを使用した
#│    いかなる損害に対して作者は一切の責任を負いません。
#│ 2. 設置に関する質問はサポート掲示板にお願いいたします。
#│    直接メールによる質問は一切お受けいたしておりません。
#└─────────────────────────────────
#
# [ (1) CGIモード : タグの貼り付け方例 ]
#  ＊以下のタグを、必ず <body>〜</body> 間に記述して下さい
# <script type="text/javascript">
# <!--
# document.write("<img src='http://www.example.com/report.cgi?");
# document.write(escape(document.referrer)+"' width='1' height='1'>");
# // -->
# </script>
# <noscript>
# <img src="http://www.example.com/report.cgi" width="1" height="1">
# </noscript>
#
# [ (2) SSIモード : タグの貼り付け方例 ]
#
# <!--#exec cgi="./cgi-bin/report.cgi"-->

#===========================================================
# ■ 基本設定
#===========================================================

# 閲覧画面の入室パスワード
# → パスワードを空欄にすると入室画面なしで閲覧可能
$cf{pass} = 'K32532';

# SSIモード (0=no 1=yes)
# → SSIの利用可能なサーバ限定（呼び出しタグに注意）
$cf{ssi} = 0;

# ログファイル【サーバパス】
$cf{logfile} = './data/log.cgi';

# テンプレートディレクトリ
$cf{tmpldir} = './tmpl';

# 最大ログ保持数（これ以上大きくしない方が無難）
$cf{maxlog} = 1000;

# アトランダム機能
# → 0以外で有効。その数値の確率でしかログ保存を行わない。
# → 1日当りの訪問回数が上記$cf{maxlog}回を超えるサイトの場合、時間帯の平準化を行う機能。
# → 例：$cf{rand} = 100; であれば、確率的に100回に1度しか集計を行わない。
$cf{rand} = 0;

# リンク元除外ページ（半角スペースで区切る）
# → ここで指定したURLは「リンク元」集計から除外されます
# → 例：$cf{myurl} = 'http://www.example.com/ http://www.example.jp/';
$cf{myurl} = 'https://anineco.org/';

# ホスト/IPアドレスによる除外（半角スペースで区切る）
# → ここで指定したURLは「リンク元」集計から除外されます
# → 例：$cf{deny_host} = '.anonymizer.com 225.12.23.';
$cf{deny_host} = '';

# IPアドレスチェックによる二重記録排除 (0=no 1=yes)
$cf{ip_chk} = 1;

## --- < ここより下は一覧リストの設定 > --- ##

# リストファイル【URLパス】
$cf{list_cgi} = './list.cgi';

# ホームページタイトル
$cf{list_title} = "あにねこ登山日誌";

# リスト一覧からの戻り先 (絶対パスなら http://からのURLで記述）
$cf{homepage} = "../index.html";

# グラフ画像（絶対パスなら http://からのURLで記述）
$cf{graph1} = "./img/graph1.gif";  # 横軸
$cf{graph2} = "./img/graph2.gif";  # 縦軸

# リスト最低表示件数（これに満たない情報は非表示）
$cf{max_ref} = 2;	# リンク元
$cf{max_os}  = 1;	# OS情報
$cf{max_ag}  = 1;	# ブラウザ
$cf{max_hos} = 2;	# ホスト名

#===========================================================
# ■ 設定完了
#===========================================================

# 設定値を返す
sub init {
	return %cf;
}



1;

