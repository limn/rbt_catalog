#!/usr/bin/perl

use strict;
use CGI;
use JSON::Syck;
use Sphinx::Search;
use Data::Dumper;
use lib '/data/www/rbtapi/modules';
use RBTAPI::External;

my $r = CGI->new;

my $sph = Sphinx::Search->new()->SetServer( '172.16.0.1', 6666 );
$sph->SetEncoders( sub { shift }, sub { shift });

print "Content-Type: application/json;charset=UTF-8\n\n";
my $search = $r->param( 'search' ) || $ARGV[0] ;
my $res = $sph->Query( $search );
$res = {} unless $res;

$res->{out} = [];

RBTAPI::External::indbh( sub {
    my $dbh = shift;

    makeOUT( $search, $res->{out}, $dbh ) if $search =~ m|^\d+$|; # exact content_id
    for my $e ( @{$res->{matches}} ) {
        makeOUT( $e->{doc}, $res->{out}, $dbh );
    }

                         });

print JSON::Syck::Dump( $res );

# warn( $sph->GetLastError );

exit;

sub makeOUT {
    my ( $id, $out, $dbh ) = @_;
    my $h = $dbh->( hash => q{SELECT * FROM rbt_megafon.all_tones WHERE content_id=?}, $id );
    return unless $h->{content_id} == $id;
    push @$out, $h;
}
