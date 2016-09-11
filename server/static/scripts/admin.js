var Collection, Book, Sequence, User, search;

(function() {
    var redux = {
	last_search: "",
	triggered: false
    };

    var debounce = function (func, threshold, execAsap) {
	var timeout;
	return function debounced () {
	    var obj = this, args = arguments;
	    function delayed () {
		if (!execAsap)
		    func.apply(obj, args);
		timeout = null;
	    };
	    
	    if (timeout)
		clearTimeout(timeout);
	    else if (execAsap)
		func.apply(obj, args);
	    
	    timeout = setTimeout(delayed, threshold || 100);
	};
    }

    // On search typing
    $('#book_form').submit(function(event) {
	// bring up more comprehensive results in resultsbox
	event.preventDefault();
	Book.create({
	    archive_id: $('#book_form input[name=archive_id]').val(),
	    aids: $('#book_form input[name=aids]').val(),
	    cids: $('#book_form input[name=cids]').val()
	}, function(resp) {
	    location.reload();
	});
    });

    // On search typing
    $('#author_form').submit(function(event) {
	// bring up more comprehensive results in resultsbox
	event.preventDefault();
	Author.create({
	    name: $('#author_form input[name=name]').val(),
	    olid: $('#author_form input[name=olid]').val(),
	    aka: $('#author_form input[name=aka]').val(),
	    bids: $('#author_form input[name=bids]').val()
	}, function(resp) {
	    location.reload();
	});
    });

}());
