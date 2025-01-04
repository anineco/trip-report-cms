#!/usr/bin/env perl

use strict;
use warnings;
use utf8;
use open qw(:utf8 :std);

use Config::Tiny;
use DBI;
use Text::Xslate;
use Time::Piece;

sub fromYMD {
  my $s = shift;
  return Time::Piece->strptime($s, '%Y-%m-%d');
}

my $cf = Config::Tiny->read('.env.local');
my $LM_DATE = $cf->{_}->{VITE_LM_DATE};
my $LM_YEAR = $cf->{_}->{VITE_LM_YEAR};
my $LMYY = $cf->{_}->{VITE_LMYY};

my $vars = {
  lm_date => $LM_DATE,
  lm_year => $LM_YEAR,
  lmyy => $LMYY,
  record => []
};

# 最近の山行
my $dbh = DBI->connect('dbi:SQLite:dbname=record.sqlite3', '', '',
  { RaiseError => 1, PrintError => 0, sqlite_unicode => 1 }
) or die $DBI::errstr;

my $sth = $dbh->prepare(<<'EOS');
SELECT start,end,issue,title,summary,link,img1x,img2x FROM record
ORDER BY start DESC LIMIT 3
EOS

my $lm = fromYMD($LM_DATE);
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

  my $td = $lm - fromYMD($issue);
  my $new = $td->days <= 7;

  push(@{$vars->{record}}, {
    date => $date,
    title => $title,
    link => $link,
    summary => $summary,
    img1x => $img1x,
    img2x => $img2x,
    new => $new
  });
}
$sth->finish;
$dbh->disconnect;

my $tx = Text::Xslate->new(syntax => 'TTerse');
print $tx->render('tmpl/index.html', $vars);
__END__
