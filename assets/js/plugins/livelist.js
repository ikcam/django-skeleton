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

    $('*[data-type="livelist"]').each(function(){
        $(this).change(function(){
            var object = $(this);
            var endpoint = $(this).attr('data-endpoint');
            var name = $(this).attr('data-name');
            var value = $(this).val();
            var data = {}

            data[name] = value;
            object.prop('disabled', true);

            $.ajax({
                type: 'PATCH',
                url: endpoint,
                data: data,
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                },
                success: function(response){
                    object.prop('disabled', false);
                },
                error: function(response){
                    jsonResponse = jQuery.parseJSON(response.responseText)
                    alert(jsonResponse.detail);
                    object.prop('disabled', false);
                },
            });
        });
    });
});
