#!/usr/bin/env perl

use strict;
use warnings;
use utf8;
use open qw(:utf8 :std);

use DBI;
use Text::Xslate qw(mark_raw);
use Time::Piece;

sub fromYMD {
  my $s = shift;
  return Time::Piece->strptime($s, '%Y-%m-%d');
}

die 'Usage: rec2hist <year>' if ($#ARGV != 0);
my $year = $ARGV[0];

my $dbh = DBI->connect('dbi:SQLite:dbname=record.sqlite3', '', '',
  { RaiseError => 1, PrintError => 0, sqlite_unicode => 1 }
) or die $DBI::errstr;

my %items;

#
# 山行記録の更新履歴
#
my $sth1 = $dbh->prepare(<<'EOS');
SELECT start,end,issue,title,link FROM record
WHERE issue IS NOT NULL AND issue LIKE ?
ORDER BY issue DESC,start
EOS

$sth1->execute($year . '%');
while (my $row = $sth1->fetch) {
  my ($start, $end, $issue, $title, $link) = @$row;

  my $s = fromYMD($start);
  my $e = fromYMD($end);
  my $date = $start;
  if ($e->year != $s->year) {
    $date .= $e->strftime('/%Y-%m-%d');
  } elsif ($e->mon != $s->mon) {
    $date .= $e->strftime('/%m-%d');
  } elsif ($e->mday != $s->mday) {
    $date .= $e->strftime('/%d');
  }
  my $content = qq{$date <a href="$link">$title</a> の山行記録を追加。};
  push(@{$items{$issue}}, $content);
}
$sth1->finish;

#
# その他の更新履歴
#
my $sth2 = $dbh->prepare(<<'EOS');
SELECT issue,content FROM changelog WHERE issue LIKE ?
EOS

$sth2->execute($year . '%');
while (my $row = $sth2->fetch) {
  my ($issue, $content) = @$row;
  push(@{$items{$issue}}, $content);
}
$sth2->finish;

$dbh->disconnect;

#
# テンプレートからHTMLを生成
#
my $vars = {
  year => $year,
  lm_year => $year,
  record => []
};

for my $issue (reverse sort keys %items) {
  my $content = join('<br>', @{$items{$issue}});
  $content =~ s/<br>/<br>\n/g;
  push(@{$vars->{record}}, {
    issue => $issue,
    content => mark_raw($content)
  });
}

my $tx = Text::Xslate->new(syntax => 'TTerse');
print $tx->render('tmpl/hist.html', $vars);
__END__
