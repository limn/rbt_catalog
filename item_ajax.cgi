#!/usr/bin/perl

use strict;
use CGI;
use JSON::Syck;
use Data::Dumper;
use lib '/data/www/rbtapi/modules';
use RBTAPI::External;

use lib '/data/www/rbtcpa/modules';
use RBTCPA::Const;


my $r = CGI->new;

print "Content-Type: application/json;charset=UTF-8\n\n";
my $id = $r->param( 'id' ) || $ARGV[0] ;

my $res;

RBTAPI::External::indbh( sub {
    my $dbh = shift;
    $res = makeOUT( $id, $dbh );
                         });

print JSON::Syck::Dump( $res );

# warn( $sph->GetLastError );

exit;

sub makeOUT {
    my ( $id, $dbh ) = @_;
    my $res = $dbh->( hash => q{SELECT * FROM rbt_megafon.all_tones WHERE content_id=?}, $id );
    return $res unless $res->{content_id} == $id;

    my $h = $dbh->( hash => q{SELECT * FROM content.content_ready WHERE area_id=1 AND content_id=?}, $id );
    $res->{ready} = $h->{content_status} == 1 ? 'Да' : $h->{content_id} == $id ? 'Условно' : 'Нет';
    $res->{partner} = ( 1392 ~~ @{ $h->{related_treaty} } ) ? 'Нет' : 'Да';

    my $pl = {};
    my ( %prices, %names, %perform );
    $dbh->( each => sub {
        my $h = shift;
        $pl->{ $h->{platform_id} } = $h;
        push @{ $prices{$h->{price}} }, $h->{platform_id};
        push @{ $names{$h->{tonename}} }, $h->{platform_id};
        push @{ $perform{$h->{singername}} }, $h->{platform_id};

            }, q{SELECT * FROM rbt_megafon.tones WHERE content_id=?}, $id );
    $res->{comment} .= sprintf "<p>Ошибка в ценах: %s</p>", join( ',', keys %prices )  if scalar keys %prices > 1;
    $res->{comment} .= sprintf "<p>Ошибка в названии песни: '%s'</p>", join( "','", keys %names )  if scalar keys %names > 1;
    $res->{comment} .= sprintf "<p>Ошибка в исполнителе: '%s'</p>", join( "','", keys %perform )  if scalar keys %perform > 1;

    $res->{porting} = 'Да';
    for my $p (1,6,7,8,9,2,4,5) {
        $res->{"pl_$p"} = +{ 
            1 => 'Да',
            2 => 'Выкл',
            3 => 'Стран'
        }->{ $pl->{$p}->{status} } || 'Нет';
        $res->{porting} = 'Нет' if $res->{"pl_$p"} ne 'Да';
    }

    my $superhit = $dbh->( value => sprintf( q{SELECT content_id FROM r2.treaty t JOIN r2.content_right c on (c.treaty_id=t.treaty_id) 
                                                 WHERE t.supplier_id IN (%s) AND c.related_right > 0 AND c.area_id = 1 AND content_id=?},  RBTCPA::Const::get_suppliers() ),
                           $id
        );
    $res->{superhit} =  $superhit == $id ? 'Да' : 'Нет';

    my $sale = $dbh->( hash => q{SELECT content_id, count(*) as count, sum( total ) as sum FROM rbt_megafon.sale s LEFT JOIN rbt_megafon.tones t ON (t.toneId=s.platform_item_id and s.platform_id=t.platform_id) WHERE created > now() - interval '1 month' AND content_id=? GROUP BY 1}, $id );
    $res->{sale_count} = int $sale->{count};
    $res->{sale_sum} = int $sale->{sum};

    $res->{superhit_diagnose} .= "Не проходит по правам<br>" if $res->{ready} eq 'Нет';
    $res->{superhit_diagnose} .= "Условные права<br>" if $res->{ready} eq 'Условно';
    $res->{superhit_diagnose} .= "Проблемы с портацией<br>" unless $res->{porting} eq 'Да';
    $res->{superhit_diagnose} .= "Проблемы с поставщиком<br>" unless $res->{superhit} eq 'Да';
    $res->{superhit_diagnose} .= "Проблемы на платформе<br>"if $res->{comment};

    $res->{superhit_diagnose} ||= 'OK';
    

    return $res;
}
