#!/usr/bin/perl -CSA
#
# json2tsv.pl - Convert WebQuestion json lines to the TREC-style TSV format
#
# Usage: json2tsv.pl PREFIX
#
# PREFIX is a prefix to the sequentially assigned IDs.

use warnings;
use strict;
use v5.10;
use utf8;

use JSON;

my $prefix = shift @ARGV;

my $i = 1;
while (<>) {
	# {"url": "http://www.freebase.com/view/en/ryan_gosling", "targetValue": "(list (description \"The United States of Leland\") (description \"Half Nelson\") (description \"The Slaughter Rule\") (description Stay) (description \"Lars and the Real Girl\") (description \"The Believer\") (description Fracture) (description \"Murder by Numbers\") (description \"The Notebook\") (description \"All Good Things\"))", "utterance": "what other movies has ryan gosling been in?"},
	chomp;
	s/,$//;
	my $q = decode_json $_;

	(my $regex = $q->{targetValue}) =~ s/^\(list \(description|\)\)$//g;
	$regex =~ s/\) \(description /|/g;
	$regex =~ s/"//g;

	my $id = sprintf '%s%05d', $prefix, $i;
	say(join("\t", $id, 'factoid', $q->{utterance}, $regex));
	$i++;
}
