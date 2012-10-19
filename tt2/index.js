$( function() {
    function fillRow( item ) {
        if ( item.comment ) 
            $( '#placeHere' ).prepend( $('<tr><td></td><td colspan=100>'+ item.comment +'</td></tr>') );

        var tr = $('<tr>'); 
        $.map( 
            ['content_id', 'song_name', 'song_performer_name', 'ready', 'pl_1', 'pl_6', 'pl_7', 'pl_8', 'pl_9', 'pl_2', 'pl_4', 'pl_5', 'superhit', 'partner', 'sale_count', 'sale_sum' ], 
            function ( i ) {
                tr.append( $('<td>').text( item[ i ] ) );
            } );
        $( '#placeHere' ).prepend( tr );
            
    }

   function createNew( item ) {
       $.ajax({
           url: "/perl-bin/rbt_megafon/catalog/item_ajax.cgi",
           dataType: "json",
           data: { id: item.content_id },
           success: fillRow
       });
   }

   $( "#city" ).autocomplete({
       source: function( request, response ) {
           $.ajax({
               url: "/perl-bin/rbt_megafon/catalog/search_ajax.cgi",
               dataType: "json",
               data: {
                   search: request.term
               },
               success: function( data ) {
                   response( $.map( data.out, function( item ) {
                       item.label = "["+item.content_id + "]" + " " + item.song_name + ", " + item.song_performer_name;
                       item.value = item.song_name + ", " + item.song_performer_name;
                       return item;
                   }));
               }
           });
       },
       minLength: 2,
       select: function( event, ui ) {
           createNew( ui.item );
       },
       open: function() {
           $( this ).removeClass( "ui-corner-all" ).addClass( "ui-corner-top" );
       },
       close: function() {
           $( this ).removeClass( "ui-corner-top" ).addClass( "ui-corner-all" );
       }
   });
 });
