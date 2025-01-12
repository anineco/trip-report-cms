package IconLut;
use strict;
use warnings;
use utf8;
my %iconlut = (
951001 => 'Flag_Blue',
951002 => 'Flag_Green',
951003 => 'Flag_Red',
951004 => 'Pin_Blue',
951005 => 'Pin_Green',
951006 => 'Pin_Red',
951007 => 'Block_Blue',
951008 => 'Block_Green',
951009 => 'Block_Red',
951010 => 'City_Small',
951011 => 'City_Medium',
951012 => 'City_Large',
952001 => 'Campground',
952002 => 'Trail_Head',
952003 => 'Park',
952004 => 'Forest',
952005 => 'Hunting_Area',
952006 => 'Fishing_Area',
952007 => 'Geocache',
952008 => 'Geocache_Found',
952009 => 'Picnic_Area',
952010 => 'Restroom',
952011 => 'Shower',
952012 => 'Beach',
952013 => 'RV_Park',
952014 => 'Scenic_Area',
952015 => 'Summit',
952016 => 'Ski_Resort',
952017 => 'Swimming_Area',
952018 => 'Golf_Course',
952019 => 'Bike_Trail',
952020 => 'Drinking_Water',
952021 => 'Tunnel',
952022 => 'Parachute_Area',
952023 => 'Glider_Area',
952024 => 'Ultralight_Area',
953001 => 'Anchor',
953002 => 'Man_Overboard',
953003 => 'Diver_Down_Flag_1',
953004 => 'Diver_Down_Flag_2',
953005 => 'Skull_And_Crossbones',
953006 => 'Light',
953007 => 'Buoy_White',
953008 => 'Shipwreck',
953009 => 'Horn',
953010 => 'Controlled_Area',
953011 => 'Restricted_Area',
953012 => 'Danger_Area',
954001 => 'Residence',
954002 => 'Fishing_Hot_Spot_Facility',
954003 => 'Building',
954004 => 'Church',
954005 => 'Cemetery',
954006 => 'Tall_Tower',
954007 => 'Short_Tower',
954008 => 'Radio_Beacon',
954009 => 'Oil_Field',
954010 => 'Mine',
954011 => 'School',
954012 => 'Crossing',
954013 => 'Civil',
954014 => 'Police_Station',
954015 => 'Bell',
954016 => 'Car',
954017 => 'Car_Rental',
954018 => 'Car_Repair',
954019 => 'Gas_Station',
954020 => 'Convenience_Store',
954021 => 'Scales',
954022 => 'Truck_Stop',
954023 => 'Wrecker',
954024 => 'Toll_Booth',
954025 => 'Parking_Area',
955001 => 'Navaid_Amber',
955002 => 'Navaid_Black',
955003 => 'Navaid_Blue',
955004 => 'Navaid_Green_White',
955005 => 'Navaid_Green',
955006 => 'Navaid_Green_Red',
955007 => 'Navaid_Orange',
955008 => 'Navaid_Red_Green',
955009 => 'Navaid_Red_White',
955010 => 'Navaid_Red',
955011 => 'Navaid_Violet',
955012 => 'Navaid_White',
955013 => 'Navaid_White_Green',
955014 => 'Navaid_White_Red',
956001 => 'Shopping_Center',
956002 => 'Telephone',
956003 => 'Airport',
956004 => 'Information',
956005 => 'Restaurant',
956006 => 'Lodging',
956007 => 'Boat_Ramp',
956008 => 'Skiing_Area',
956009 => 'Fitness_Center',
956010 => 'Ice_Skating',
956011 => 'Medical_Facility',
956012 => 'Pharmacy',
956013 => 'Bridge',
956014 => 'Dam',
956015 => 'Bank',
956016 => 'Bar',
956017 => 'Department_Store',
956018 => 'Movie_Theater',
956019 => 'Fast_Food',
956020 => 'Pizza',
956021 => 'Live_Theater',
956022 => 'Post_Office',
956023 => 'Museum',
956024 => 'Ball_Park',
956025 => 'Bowling',
956026 => 'Amusement_Park',
956027 => 'Stadium',
956028 => 'Zoo'
);
sub IconUrl {
  my $icon = shift;
  return 'symbols/' . $iconlut{$icon} . '.png';
}
sub IconSize {
  my $icon = shift;
  return [24, 24];
}
sub IconAnchor {
  my $icon = shift;
  return [12, 12];
}
1;