#!/usr/bin/env perl

use strict;
use warnings;
use utf8;
use open qw(:utf8 :std);

use JSON qw(decode_json);
use DBI;
use Math::Round;

die "Usage: mkexplored <CID>…\n" if ($#ARGV < 0);

my $sqlite = DBI->connect('dbi:SQLite:dbname=record.sqlite3', '', '',
  { RaiseError => 1, PrintError => 0, sqlite_unicode => 1 }
) or die $DBI::errstr;

my $dsn = 'DBI:mysql:anineco_tozan;mysql_read_default_file=~/.my.cnf'; # 🔖
my $dbh = DBI->connect($dsn, undef, undef,
  {mysql_enable_utf8mb4 => 1}
) or die $DBI::errstr;

my $sth1 = $dbh->prepare(<<'EOS');
SET @p=ST_GeomFromText(?,4326/*!80003 ,'axis-order=long-lat'*/)
EOS
my $sth2 = $dbh->prepare(<<'EOS');
SELECT id,name,ST_Distance_Sphere(pt,@p) AS d FROM geom ORDER BY d LIMIT 1
EOS

sub read_json {
  my $file = shift;

  open(my $in, '<:raw', $file) or die "Can't open $file: $!\n";
  my $text = do { local $/; <$in> };
  close($in);
  my $root = decode_json($text);
  foreach my $feature (@{$root->{features}}) {
    my $geometry = $feature->{geometry};
    my $properties = $feature->{properties};
    next unless ($geometry->{type} eq 'Point' && $properties->{_iconUrl} eq 'symbols/Summit.png');
    my $coordinates = $geometry->{coordinates};
    my $name = $properties->{name};
    my $lon = $coordinates->[0];
    my $lat = $coordinates->[1];
    $sth1->execute("POINT($lon $lat)");
    $sth1->finish;
    $sth2->execute;
    while (my $row = $sth2->fetch) {
      my ($id, $yama, $d) = @$row;
      next if ($d >= 40);
      $d = nearest(0.1, $d);
      print <<EOS;
INSERT INTO explored VALUES (\@rec,NULL,$id); -- $yama,${d}m
EOS
    }
    $sth2->finish;
  }
}

my $sth = $sqlite->prepare(<<'EOS');
SELECT start,end,issue,title,summary,link,img1x FROM record WHERE link=?
EOS

foreach my $cid (@ARGV) {
  my ($start, $end, $issue, $title, $summary, $link, $img1x);
  $sth->execute($cid . '.html');
  while (my $row = $sth->fetch) {
    ($start, $end, $issue, $title, $summary, $link, $img1x) = @$row;
  }
  $sth->finish;
  print <<EOS;
INSERT INTO record VALUES (NULL,"$start","$end","$issue","$title","$summary","$link","$img1x");
SET \@rec=LAST_INSERT_ID();
EOS
  foreach my $file (glob "docs/$cid/routemap*.geojson") {
    read_json($file);
  }
}
$sqlite->disconnect;
$dbh->disconnect;

__END__
