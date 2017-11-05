jQuery(document).ready(function($){
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function changeProfileField(field, value){
        if(value === undefined) return;

        var endpoint = api_url_profile;
        var data = {};
        data[field] = value;

        $.ajax({
            type: 'PATCH',
            url: endpoint,
            data: data,
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            },
            error: function(response){
                jsonResponse = jQuery.parseJSON(response.responseText);
                alert(jsonResponse.detail);
            },
        });
    }

    $('.navbar-minimalize').on('click', function(event){
        changeProfileField('nav_expanded', !$('body').hasClass('mini-navbar'));
    });
});
