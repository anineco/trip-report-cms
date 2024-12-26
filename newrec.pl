#!/usr/bin/env perl

use strict;
use warnings;
use utf8;
use open qw(:utf8 :std);

use File::Basename;
use DBI;
use Text::CSV;

# データベースをオープン
my $dbh = DBI->connect('dbi:SQLite:dbname=record.sqlite3', '', '',
  { RaiseError => 1, PrintError => 0, sqlite_unicode => 1 }
) or die $DBI::errstr;

# テーブルを作成
$dbh->do(<<'EOS');
CREATE TABLE IF NOT EXISTS record (
  start TEXT NOT NULL PRIMARY KEY, -- 開始日
  end TEXT NOT NULL,   -- 終了日
  issue TEXT,          -- 公開日
  title TEXT NOT NULL, -- タイトル
  summary TEXT,        -- 概略
  link TEXT,           -- 山行記録URL
  img1x TEXT,          -- 画像URL
  img2x TEXT           -- 画像URL
)
EOS

# データベースが空の場合
my $sth = $dbh->prepare('SELECT COUNT(*) FROM record');
$sth->execute;
my ($count) = $sth->fetchrow_array;
$sth->finish;
if ($count == 0) {
  # データベースを初期化
  my $csv = Text::CSV->new();
  while (my $row = $csv->getline(<DATA>)) {
    $dbh->do('INSERT INTO record VALUES (?,?,?,?,?,?,?,?)', undef, @$row);
  }
}

# オプションを解析
if ($#ARGV >= 0 && $ARGV[0] eq '-d') {
  shift(@ARGV);
  # 山行記録を削除
  my $sth = $dbh->prepare('DELETE FROM record WHERE link=?');
  foreach my $file (@ARGV) {
    my $link = basename $file;
    $sth->execute($link);
    $sth->finish;
  }
  $dbh->disconnect;
  exit;
}

# 山行記録を登録
$sth = $dbh->prepare('REPLACE INTO record VALUES (?,?,?,?,?,?,?,?)');
foreach my $file (@ARGV) {
  my $link = basename $file;
  my $dir = dirname $file;
  my ($start, $end, $issue, $title, $summary, $img1x, $img2x);
  $issue = $img1x = $img2x = '';
  open(my $in, '<', $file) or die "Can't open $file: $!\n";
  while (my $line = <$in>) {
    if ($line =~ /"temporalCoverage":"(.*)"/) {
      ($start, $end) = split /\//, $1;
      if ($end) {
        my ($y, $m, $d) = split /-/, $start;
        if ($end =~ m|^(\d+)-(\d+)-(\d+)$|) {
          $y = $1;
          $m = $2;
          $d = $3;
        } elsif ($end =~ m|^(\d+)-(\d+)$|) {
          $m = $1;
          $d = $2;
        } elsif ($end =~ m|^(\d+)$|) {
          $d = $1;
        }
        $end = sprintf("%d-%02d-%02d", $y, $m, $d);
      } else {
        $end = $start;
      }
    } elsif ($line =~ m|^<title>(.*)</title>|) {
      $title = $1;
    } elsif ($line =~ m|^<meta name="description" content="(.*)">|) {
      $summary = $1;
    } elsif ($line =~ m|^<meta property="og:image" content="https://anineco.org/(.*)/2x/(.*)">|) {
      $img1x = $1 . '/S' . $2;
      $img2x = $1 . '/2x/S' . $2;
      die "Image $img1x, $img2x not found: $!\n" unless (-e "$dir/$img1x" && -e "$dir/$img2x");
    } elsif ($line =~ m|"datePublished":"(.*)"|) {
      $issue = $1;
    }
  }
  close($in);
  $sth->execute($start, $end, $issue, $title, $summary, $link, $img1x, $img2x);
  $sth->finish;
}
$dbh->disconnect;
__DATA__
1975-03-21,1975-03-21,,"宝満山",,,,
1975-04-29,1975-04-29,,"丹沢表尾根",,,,
1975-06-08,1975-06-08,,"大山（丹沢山地）",,,,
1975-07-27,1975-07-28,,"谷川岳・苗場山",,,,
1975-09-14,1975-09-15,,"塔ノ岳〜丹沢山〜蛭ヶ岳〜檜洞丸",,,,
1975-09-28,1975-09-28,,"葛葉川本谷",,,,
1975-11-09,1975-11-09,,"高畑倉山〜倉岳山",,,,
1975-11-30,1975-11-30,,"モミソ沢",,,,
1976-01-02,1976-01-02,,"御岳山",,,,
1976-07-25,1976-07-25,,"鷹ノ巣山",,,,
1976-08-15,1976-08-17,,"西沢渓谷・甲武信岳〜十文字峠",,,,
1976-09-23,1976-09-23,,"御前山",,,,
1976-10-10,1976-10-10,,"蕎麦粒山〜川乗山",,,,
1976-11-03,1976-11-03,,"高柄山",,,,
1977-03-06,1977-03-06,,"日川渓谷",,,,
1977-03-26,1977-03-28,,"御正体山〜石割山・杓子山",,,,
1977-05-01,1977-05-01,,"酉谷山",,,,
1977-07-30,1977-08-06,,"北海道旅行：旭岳、羅臼岳",,,,
1977-10-09,1977-10-10,,"両神山",,,,
1977-11-23,1977-11-23,,"三頭山",,,,
1978-01-16,1978-01-16,,"高尾山〜陣馬山",,,,
1978-04-01,1978-04-02,,"大菩薩嶺",,,,
1978-08-05,1978-08-07,,"甲斐駒ヶ岳〜仙丈ヶ岳",,,,
1978-08-30,1978-08-30,,"三ッ峠",,,,
1978-09-24,1978-09-24,,"乾徳山〜黒金山",,,,
1979-03-27,1979-03-28,,"小金沢山〜黒岳",,,,
1979-05-06,1979-05-06,,"滝子山〜大谷ヶ丸",,,,
1979-07-12,1979-07-12,,"越前岳",,,,
1979-09-23,1979-09-23,,"盆掘川石津窪",,,,
1980-04-02,1980-04-04,,"雲取山〜飛竜山",,,,
1980-06-22,1980-06-22,,"新茅ノ沢・前大沢",,,,
1980-07-13,1980-07-13,,"源次郎沢・戸沢",,,,
1980-10-02,1980-10-03,,"大谷ヶ丸〜黒岳〜雁ヶ腹摺山",,,,
1980-12-28,1980-12-28,,"大菩薩峠",,,,
1981-03-01,1981-03-01,,"権現山〜扇山",,,,
1981-04-19,1981-04-19,,"十二ヶ岳〜鬼ヶ岳",,,,
1981-04-26,1981-04-26,,"四十八瀬川小草平ノ沢",,,,
1981-07-12,1981-07-12,,"日原川鷹ノ巣谷",,,,
1981-07-21,1981-07-24,,"越後三山",,,,
1981-09-06,1981-09-06,,"水根沢谷",,,,
1981-10-25,1981-10-25,,"矢平山",,,,
1981-12-31,1982-01-02,,"霧積温泉から剣ノ峰・鼻曲山",,,,
1982-04-17,1982-04-18,,"女峰山",,,,
1982-05-09,1982-05-09,,"盆掘川棡葉窪",,,,
1982-07-04,1982-07-04,,"丹沢三ッ峰",,,,
1982-07-14,1982-07-16,,"荒沢岳〜兎岳〜丹後山",,,,
1982-08-02,1982-08-03,,"妙高山〜火打山",,,,
1982-08-08,1982-08-08,,"飯縄山",,,,
1982-12-31,1983-01-02,,"岩下温泉から兜山・岩堂峠",,,,
1983-06-26,1983-06-26,,"大山川（丹沢山地）",,,,
1983-07-21,1983-07-27,,"石狩岳〜トムラウシ山〜大雪山",,,,
1983-10-02,1983-10-02,,"畦ヶ丸",,,,
1984-05-05,1984-05-06,,"未丈ヶ岳（敗退）",,,,
1984-07-29,1984-08-01,,"ペテガリ岳〜ヤオロマップ岳〜コイカクシュサツナイ岳",,,,
1984-09-01,1984-09-02,,"赤岳〜権現岳",,,,
1984-09-08,1984-09-09,,"火打山",,,,
1984-12-09,1984-12-09,,"男体山（日光）",,,,
1984-12-16,1984-12-16,,"日光白根山",,,,
1984-12-31,1985-01-02,,"湯船温泉から矢倉岳・不老山〜湯船山",,,,
1985-05-19,1985-05-19,,"太郎山",,,,
1985-06-02,1985-06-02,,"大真名子山〜小真名子山",,,,
1985-07-28,1985-08-03,,"カムイエクウチカウシ山〜エサオマントッタベツ山〜幌尻岳",,,,
1985-08-27,1985-08-28,,"赤岳〜横岳",,,,
1986-04-27,1986-04-27,,"十枚山",,,,
1986-04-30,1986-05-03,,"妙高山スキー：澄川、焼山北面",,,,
1986-06-01,1986-06-01,,"塔ノ岳",,,,
1986-06-08,1986-06-08,,"玄倉川女郎小屋沢",,,,
1986-07-20,1986-07-20,,"谷太郎川鳥屋待沢",,,,
1986-07-27,1986-07-30,,"ヌピナイ川〜ピリカヌプリ",,,,
1986-09-06,1986-09-07,,"平標山〜仙ノ倉山〜谷川岳",,,,
1986-09-14,1986-09-15,,"鬼怒川野門沢",,,,
1986-09-29,1986-09-29,,"ニペソツ山",,,,
1986-10-10,1986-10-12,,"高谷池ヒュッテ",,,,
1986-12-31,1987-01-02,,"大子温泉から八溝山・男体山",,,,
1987-04-25,1987-04-29,,"妙高山スキー：惣兵衛落、澄川、焼山北面",,,,
1987-05-31,1987-05-31,,"海沢",,,,
1987-06-07,1987-06-07,,"小川谷廊下",,,,
1987-07-18,1987-07-19,,"ガラン沢",,,,
1987-08-02,1987-08-05,,"中の川〜ソエマツ岳〜北東面直登沢〜神威岳",,,,
1987-09-19,1987-09-21,,"湯檜曽川本谷",,,,
1987-09-27,1987-09-27,,"天城山",,,,
1988-04-17,1988-04-17,,"天祖山",,,,
1988-04-28,1988-05-01,,"妙高山スキー：焼山〜昼闇山",,,,
1988-06-04,1988-06-04,,"巳ノ戸谷",,,,
1988-09-17,1988-09-18,,"北岳",,,,
1988-12-31,1989-01-02,,"下部温泉から身延山・毛無山",,,,
1989-04-29,1989-05-04,,"妙高山スキー：焼山北面",,,,
1989-06-03,1989-06-04,,"武尊山",,,,
1989-07-23,1989-07-23,,"滝郷沢",,,,
1989-07-29,1989-08-02,,"コタキ川〜知床岳",,,,
1989-08-04,1989-08-04,,"斜里岳",,,,
1989-10-02,1989-10-02,,"粟ヶ岳",,,,
1990-06-24,1990-06-24,,"荒島岳",,,,
1990-08-18,1990-08-18,,"ヒツゴー沢",,,,
1990-08-25,1990-08-27,,"余別川〜余別岳（敗退）",,,,
1990-11-18,1990-11-18,,"秩父御岳山",,,,
1990-11-24,1990-11-24,,"熊倉山",,,,
1991-07-21,1991-07-21,,"大朝日岳",,,,
1992-07-29,1992-07-29,,"祖母山",,,,
1992-09-05,1992-09-06,,"鳳凰三山",,,,
1992-09-27,1992-09-27,,"白山（両白山地）",,,,
1992-10-11,1992-10-11,,"日留賀岳",,,,
1995-05-06,1995-05-06,,"鍋割山",,,,
1995-06-17,1995-06-18,,"キュウハ沢",,,,
1995-08-03,1995-08-03,,"雄鉾岳",,,,
1995-08-19,1995-08-20,,"蝶ヶ岳〜常念岳",,,,
1995-08-26,1995-08-27,,"小雲取谷",,,,
1995-10-22,1995-10-22,,"西ゼン",,,,
1995-11-04,1995-11-05,,"大無間山",,,,
1996-01-15,1996-01-15,,"吾妻山〜鳴神山",,,,
1996-01-28,1996-01-28,,"仙人ヶ岳",,,,
1996-02-04,1996-02-04,,"残馬山",,,,
1996-03-10,1996-03-10,,"三境山〜根本山",,,,
1996-03-16,1996-03-16,,"熊鷹山〜地蔵岳",,,,
1996-04-14,1996-04-14,,"備前楯山",,,,
1996-04-28,1996-04-28,,"半月山",,,,
1996-05-06,1996-05-06,,"座間峠〜鳴神山",,,,
1996-05-18,1996-05-18,,"富士山スキー",,,,
1996-07-06,1996-07-06,,"庚申山",,,,
1996-07-13,1996-07-14,,"袈裟丸山",,,,
1996-07-27,1996-07-27,,"伯耆大山",,,,
1996-08-18,1996-08-19,,"爺ヶ岳〜鹿島槍ヶ岳",,,,
1996-08-24,1996-08-24,,"蓼科山",,,,
1996-09-06,1996-09-07,,"笛吹川ヌク沢",,,,
1996-09-20,1996-09-20,,"LaDôle（スイス）",,,,
1996-11-17,1996-11-17,,"茅ヶ岳",,,,
1996-12-31,1997-01-02,,"いわき湯本温泉から二ッ箭山",,,,
1997-02-10,1997-02-10,,"栗生山",,,,
1997-04-12,1997-04-12,,"石裂山",,,,
1997-08-23,1997-08-24,,"餓鬼岳",,,,
1997-12-13,1997-12-13,,"社山",,,,
1998-01-02,1998-01-02,,"角田山","正月を弥彦・観音寺温泉で過ごし、灯台コースから登頂。",,,
1998-05-16,1998-05-16,,"富士山山スキー","久須志岳の下から吉田大沢の標高2800m付近まで滑る。",,,
1998-05-31,1998-05-31,,"黒檜山（赤城）","水沼温泉から利平茶屋を経て黒檜山山頂まで往復ラン。",,,
1998-06-21,1998-06-21,,"庚申山","お山巡りコースを歩き、コウシンソウを見る。",,,
1998-08-01,1998-08-04,,"栂海新道","親不知から白馬岳を目指すも、豪雨のため、途中の朝日岳から北又小屋に下山。",,,
1998-09-19,1998-09-19,,"谷川岳","紅葉を目当てに天神平から往復。",,,
1998-11-03,1998-11-03,,"根本山〜熊鷹山","根本沢から登る。山頂付近は紅葉が見事。",,,
1999-05-22,1999-05-22,,"富士山山スキー","頂上から吉田大沢へ標高差1000mを滑降。",,,
1999-12-04,1999-12-04,,"長者ヶ岳","田貫湖から往復のハイキング。山頂からの展望はガスの中。",,,
2001-01-01,2001-01-02,,"真富士山・浜石山","真富士山は歩く距離は短いが、安倍川流域の山の例にもれず急峻だ。南アや富士山の眺めが良い",,,
2002-05-05,2002-05-05,,"袈裟丸山","弓の手コースからアカヤシオをめでつつ、前袈裟往復。",,,
__END__
