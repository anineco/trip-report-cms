#!/usr/bin/env -S perl -CA
# mkroutemap.pl - create geojson
use strict;
use warnings;
use utf8;
use open qw(:utf8 :std);
use feature qw(say);

use Config::Tiny;
use File::Basename;
use JSON;
use XML::Simple qw(:strict);

use FindBin;
use lib $FindBin::Bin;
use Extensions;
use ToGeojson;
require IconLut;

# conversion parameters
our %param = (
  line_style => 13,
  line_size => 3,
  opacity => 0.5,
  xt_error => 0.005, # allowable cross-track error in kilometer
);

# load configuration file
my $cf = Config::Tiny->read('config.ini');
my $workspace = $cf->{_}->{workspace};
my $material_gpx = $cf->{material}->{gpx};
my $material_img = $cf->{material}->{img};

# parse command line argument
if ($#ARGV < 0) {
  my $script = basename($0);
  die "Usage: $script <CID>";
}
my $cid = $ARGV[0]; # content ID

# load resource json
my $file = "$workspace/$cid.json";
open(my $in, '<:raw', $file) or die "Can't open $file: $!";
my $text = do { local $/; <$in> };
close($in);
my $resource = decode_json($text);

my $xs = XML::Simple->new(
  ForceArray => 1,
  KeepRoot => 1,
  KeyAttr => [],
  XMLDecl => '<?xml version="1.0" encoding="UTF-8"?>'
);

my $js = JSON->new->utf8(0); # disable UTF-8 encoding

sub convert {
  my ($gpx, $routemap) = @_;
  my $input = join ' -f ', @{$gpx};
  my $cmd = "gpsbabel -r -t -i gpx -f $input -x simplify,error=$param{xt_error}k -o gpx,gpxver=1.1 -F -";
  open(my $in, '-|', $cmd) or die "Can't execute '$cmd': $!";
  my $xml = $xs->XMLin($in);
  close($in);
  my $geojson = ToGeoJSON::convert($xml);
  open(my $out, '>', $routemap) or die "Can't open $routemap: $!";
  print $out $js->encode($geojson), "\n";
  close($out);
}

foreach my $s (@{$resource->{section}}) {
  my $routemap = "$workspace/$cid/$s->{routemap}";
  say $routemap;
  convert($s->{gpx}, $routemap);
}
__END__
