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
my $YEAR = $cf->{_}->{VITE_YEAR};
my $LM_YEAR = $cf->{_}->{VITE_LM_YEAR};

my $vars = {
  lm_year => $LM_YEAR,
  hist => [],
  chron => []
};

# 年別更新履歴

for (my $year = $LM_YEAR; $year >= 2004; $year--) {
  push(@{$vars->{hist}}, {
    year => $year,
    url => sprintf('hist%02d.html', $year - 2000)
  });
}

# 年別山行記録

my $dbh = DBI->connect('dbi:SQLite:dbname=record.sqlite3', '', '',
  { RaiseError => 1, PrintError => 0, sqlite_unicode => 1 }
) or die $DBI::errstr;

my $sth = $dbh->prepare(<<'EOS');
SELECT start,end,title,link FROM record
WHERE start LIKE ? ORDER BY start
EOS

for (my $year = $YEAR; $year >= 1998; $year--) {
  my $record = [],
  $sth->execute($year . '%');
  while (my $row = $sth->fetch) {
    my ($start, $end, $title, $link) = @$row;

    my $date = $start;
    my $s = fromYMD($start);
    my $e = fromYMD($end);
    if ($e->year != $s->year) {
      $date .= $e->strftime('/%Y-%m-%d');
    } elsif ($e->mon != $s->mon) {
      $date .= $e->strftime('/%m-%d');
    } elsif ($e->mday != $s->mday) {
      $date .= $e->strftime('/%d');
    }

    push(@{$record}, {
      date => $date,
      title => $title,
      link => $link
    });
  }
  $sth->finish;

  push(@{$vars->{chron}}, {
    year => $year,
    url => "ch$year.html",
    record => $record
  });
}
$dbh->disconnect;

my $tx = Text::Xslate->new(syntax => 'TTerse');
print $tx->render('tmpl/toc.html', $vars);
__END__
