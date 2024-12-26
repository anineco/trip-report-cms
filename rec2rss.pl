#!/usr/bin/env perl

use strict;
use warnings;
use utf8;
use open qw(:utf8 :std);

use DBI;
use File::Basename;
use Text::Xslate;
use Time::Piece;

sub fromYMD {
  my $s = shift;
  return Time::Piece->strptime($s, '%Y-%m-%d');
}

my $prg = basename($0, '.pl');
my $rss = ($prg eq 'rec2rss') ? 'rss' : 'rss2';
die "Usage: $prg\n" if ($#ARGV >= 0);

my $dbh = DBI->connect('dbi:SQLite:dbname=record.sqlite3', '', '',
  { RaiseError => 1, PrintError => 0, sqlite_unicode => 1 }
) or die $DBI::errstr;

my $vars = {
  record => []
};

my $sth = $dbh->prepare(<<'EOS');
SELECT start,end,issue,title,summary,link,img1x,img2x FROM record
ORDER BY start DESC LIMIT 15
EOS
$sth->execute;
while (my $row = $sth->fetch) {
  my ($start, $end, $issue, $title, $summary, $link, $img1x, $img2x) = @$row;

  my $s = fromYMD($start);
  my $e = fromYMD($end);
  my $date = sprintf("%d年%d月%d日", $s->year, $s->mon, $s->mday);
  if ($e->year != $s->year) {
    $date .= sprintf("〜%d年%d月%d日", $e->year, $e->mon, $e->mday);
  } elsif ($e->mon != $s->mon) {
    $date .= sprintf("〜%d月%d日", $e->mon, $e->mday);
  } elsif ($e->mday != $s->mday) {
    $date .= sprintf("〜%d日", $e->mday);
  }

  push(@{$vars->{record}}, {
    date => $date,
    issue => $issue,
    title => $title,
    summary => $summary,
    link => $link,
    img1x => $img1x,
    img2x => $img2x
  });
}
$sth->finish;
$dbh->disconnect;

my $tx = Text::Xslate->new(syntax => 'TTerse');
print $tx->render("tmpl/$rss.rdf", $vars);
__END__
