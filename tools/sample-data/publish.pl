#!/usr/bin/env perl

#   id,owner_id,mime_type,file_path,create_day_id,create_date,artist
#    0,       1,        2,        3,            4,          5,     6
# uuid,    uuid,      str,      str,          int,        str,   str

my @imgs = qw(
01.jpg
02.jpg
03.jpg
04.jpg
05.jpg
06.jpg
07.jpg
08.jpg
09.jpg
);

my $bucket = 'elektrum-media-development';
my $profile = 'elektrum-development';

my $headers = <>;
for(<>) {
    chomp;
    my @vals = split /,/;

    my $path = $vals[3];

    my $file = $imgs[rand @imgs];
    my $sz = (stat($file))[7];
    my $dim = `identify -format '%wx%h' $file`;
    my ($w,$h) = split /x/, $dim;

    #print "aws s3 cp $file s3://$bucket$path\n";
    `aws --profile=$profile s3 cp $file s3://$bucket$path`;

    print qq^
insert into media_item (id,owner_id,mime_type,file_path,create_day_id,create_date,artist,file_size,image_height,image_width)
	values (uuid('$vals[0]'), uuid('$vals[1]'), '$vals[2]', '$vals[3]', $vals[4], '$vals[5]', '$vals[6]', $sz, $h, $w);\n^;
}
