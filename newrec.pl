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

=pod
Webページのない山行記録をCSVファイルで読み込む場合は次を実行
$ sqlite3 record.sqlite3
sqlite> .mode csv
sqlite> .import record_no_page.csv recode
sqlite> .exit
=cut 

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
__END__
