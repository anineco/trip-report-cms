#!/usr/bin/env perl

use strict;
use warnings;
use utf8;
use open qw(:utf8 :std);

use File::Basename;
use DBI;
use Text::CSV_XS;

# データベースをオープン
my $dbh = DBI->connect('dbi:SQLite:dbname=record.sqlite3', '', '',
  { RaiseError => 1, PrintError => 0, sqlite_unicode => 1 }
) or die $DBI::errstr;

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
my $sth = $dbh->prepare('REPLACE INTO record VALUES (?,?,?,?,?,?,?,?)');
foreach my $file (@ARGV) {
  my $link = basename $file;
  my ($start, $end, $issue, $title, $summary, $img1x, $img2x);
  open(my $in, '<', $file) or die "$file $!";
  while (my $line = <$in>) {
    if ($line =~ m|^<div><time datetime="(.*)">.*</time>(.*)</div>|) {
      $start = $1;
      my ($y, $m, $d) = split(/-/, $start);
      my $e = $2;
      if ($e =~ m|^〜(\d+)年(\d+)月(\d+)日|) {
        $y = $1;
        $m = $2;
        $d = $3;
      } elsif ($e =~ m|^〜(\d+)月(\d+)日|) {
        $m = $1;
        $d = $2;
      } elsif ($e =~ m|^〜(\d+)日|) {
        $d = $1;
      }
      $end = sprintf("%d-%02d-%02d", $y, $m, $d);
    } elsif ($line =~ m|^<title>(.*)</title>|) {
      $title = $1;
    } elsif ($line =~ m|^<meta name="description" content="(.*)">|) {
      $summary = $1;
    } elsif ($line =~ m|^<meta property="og:image" content="https://anineco.org/(.*)/2x/(.*)">|) {
      $img1x = $1 . '/S' . $2;
      $img2x = $1 . '/2x/S' . $2;
      die $! unless (-e $img1x && -e $img2x);
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
