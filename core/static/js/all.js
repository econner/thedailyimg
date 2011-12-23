$(document).ready(function(){
    var path = window.location.pathname;
    
    var listings = Listings();
});

/*
* Enables csrf on all ajax views
*/
$(document).ajaxSend(function(event, xhr, settings) {
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    function sameOrigin(url) {
        // url could be relative or scheme relative or absolute
        var host = document.location.host; // host + port
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        // Allow absolute or scheme relative URLs to same origin
        return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
            // or any other URL that isn't scheme relative or absolute i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url));
    }
    function safeMethod(method) {
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    if (!safeMethod(settings.type) && sameOrigin(settings.url)) {
        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
    }
});

function Listings() {
    var that = {};
    var voters = [];
    
    that.setup = function() {
        $('.image-rating').each(function() {
            var self = this;
            var cur_voter = Voter({
                "container": self
            });
            voters.push(cur_voter);
        });
    }
    
    that.setup();
    return that;
}


function Voter(options) {
    var that = {}
    
    var container = $(options.container);
    var image_id = $("input[name='image-id']", container).val();
    
    that.get_data = function(arrow){
        var action = arrow.attr('data-action');
        var cat = arrow.attr('data-id');
        var image = image_id;
        
        return {
            action: action,
            cat: cat,
            image: image
        }
    }
    
    that.get_vote_count = function(arrow) {
        return $(".vote-count[data-id='" + arrow.attr('data-id') + "']", container);
    }
    
    that.deselect_votes = function(arrow){
        $('.vote-arrow[data-id="'+arrow.attr('data-id')+'"]', container).removeClass('voted');
    }
    
    that.setup = function() {
        $('.vote-arrow', container).bind("click", function(e){
            var self = $(this);
            e.preventDefault();
            
            var vote_count = that.get_vote_count($(this));
            $.ajax({
                type: 'POST',
                url: '/ajax/vote',
                dataType: 'JSON',
                data: that.get_data(self),
                success: function(result){
                    console.info("HERE");
                    if(result.status == 'ok') {
                        vote_count.html(result.votes);
                        already_selected = self.hasClass('voted');
                        that.deselect_votes(self);
                        if(already_selected){
                            self.removeClass('voted');
                        }else{
                            self.addClass('voted');
                        }
                    } else {
                        // assume they're not logged in, forward to login url
                        console.info("here");
                        window.location.href = "/login"
                    }
                }
            });
        });
        
    }
    
    that.setup();
    return that;
}