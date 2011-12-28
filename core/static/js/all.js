$(document).ready(function(){
    var path = window.location.pathname;
    
    if(path == "/" || path.indexOf("/list/") != -1) {
        var listings = Listings();
    }
    
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

function Listings(options) {
    var that = {};
    var voters = [];
    var cur_page = 1;
    var loading_page = false;
    var on_last_page = false;
    
    var category = 0;
    
    function get_data() {
        return {
            page: cur_page,
            category: category
        }
    }
    
    function append_listings(images) {        
        $(images).each(function() {
            var data = $("#listing-template").tmpl(this);
            for(var idx in this.categories) {
                var category = this.categories[idx];
                console.info(category);
                var cat_vote = $("#vote-template").tmpl(category);
                $(".voter", data).append(cat_vote);
            }
            
            var cur_voter = Voter({
                "container": $(".image-rating", data)
            });
            voters.push(cur_voter);
            data.appendTo("#objects-container");
        });
    }
    
    
    function retrieve_images() {
        if(!loading_page && !on_last_page) {
            cur_page++;
            loading_page = true;
            
            $("#aux-info").html("Loading...");
            $.ajax({
                type: 'GET',
                url: '/ajax/page',
                dataType: 'JSON',
                data: get_data(),
                success: function(result){
                    loading_page = false;
                    append_listings(result.images);
                     $("#aux-info").html("");
                    
                    if(!result.has_more_pages) on_last_page = true;
                }
            });
        }
    }
    
    that.setup = function() {
        $('.image-rating').each(function() {
            var self = this;
            var cur_voter = Voter({
                "container": self
            });
            voters.push(cur_voter);
        });
        
        category = $("#viewing-category").val();
        
        // setup infinite scroll
        that.see_more();
    }
    
    that.see_more = function() {
        var SCROLL_LEEWAY = 500;
        $(window).scroll(function(){
            var diff = $(document).height() - $(window).scrollTop() - $(window).height();
            
            if(diff < SCROLL_LEEWAY){
                retrieve_images();
            }
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