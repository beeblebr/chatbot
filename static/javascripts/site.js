$( document ).ready(function() {    
    $('a').click(handleClick);

    function handleClick(e) {
        var target = $(e.target).closest('a');
        if( target ) {
            e.preventDefault();
            window.location = target.attr('href');
        }
    }
});