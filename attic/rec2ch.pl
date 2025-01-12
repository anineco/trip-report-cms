#!/usr/bin/env perl

use strict;
use warnings;
use utf8;
use open qw(:utf8 :std);

use DBI;
use Text::Xslate;
use Time::Piece;

sub fromYMD {
  my $s = shift;
  return Time::Piece->strptime($s, '%Y-%m-%d');
}

die "Usage: rec2ch <year>\n" if ($#ARGV != 0);
my $year = $ARGV[0];

my $vars = {
  year => $year,
  record => []
};

my $dbh = DBI->connect('dbi:SQLite:dbname=record.sqlite3', '', '',
  { RaiseError => 1, PrintError => 0, sqlite_unicode => 1 }
) or die $DBI::errstr;

my $sth = $dbh->prepare(<<'EOS');
SELECT start,end,issue,title,summary,link,img1x,img2x FROM record
WHERE start LIKE ? ORDER BY start
EOS

my $lm_year = 2022;
$sth->execute($year . '%');
while (my $row = $sth->fetch) {
  my ($start, $end, $issue, $title, $summary, $link, $img1x, $img2x) = @$row;

  if (defined($issue)) {
    my $t = fromYMD($issue);
    $lm_year = $t->year if ($lm_year < $t->year);
  }

  my $s = fromYMD($start);
  my $e = fromYMD($end);
  my $date = sprintf('%d月%d日', $s->mon, $s->mday);
  if ($e->year != $s->year || $e->mon != $s->mon) {
    $date .= sprintf("〜%d月%d日", $e->mon, $e->mday);
  } elsif ($e->mday != $s->mday) {
    $date .= sprintf("〜%d日", $e->mday);
  }

  push(@{$vars->{record}}, {
    date => $date,
    title => $title,
    summary => $summary,
    link => $link,
    img1x => $img1x,
    img2x => $img2x,
  });
}
$sth->finish;
$vars->{lm_year} = $lm_year;

$dbh->disconnect;

my $tx = Text::Xslate->new(syntax => 'TTerse');
print $tx->render('tmpl/ch.html', $vars);
__END__
