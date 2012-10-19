#!/usr/bin/perl

use strict;
use Template;
use lib '/data/www/rbtapi/modules';
use RBTAPI::External;
use CGI;

use constant {
    TT2_DIR => '/data/www/office.mmska.ru/perl-bin/rbt_megafon/catalog/tt2',
};

my $r = CGI->new;
my ( $in, $tpl );
#$in->{$_} = $r->param( $_ ) for qw..;
my $image = { in => $in };

$tpl = 'index.html';

servicePage();

exit 0;

sub servicePage {
    my $tt2 = Template->new( {
        INCLUDE_PATH => TT2_DIR,
#        COMPILE_DIR => $::as->config->param( 'template.compileDir' ),
        COMPILE_EXT => '.ttc',
        TRIM => 1, ABSOLUTE => 1,
                             } ) or die( "Template error " . Template->error() );
    print "Content-Type: text/html; charset=UTF-8\n\n";
    $tt2->process( $tpl, $image ) or die( "Template error " . $tt2->error );
}
