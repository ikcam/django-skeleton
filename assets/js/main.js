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

    $('[data-toggle="tooltip"]').tooltip();

    var pythonToJsFormats = Object.freeze({
      '%a': 'ddd',
      '%A': 'dddd',
      '%w': 'd',
      '%d': 'DD',
      '%b': 'MMM',
      '%B': 'MMMM',
      '%m': 'MM',
      '%y': 'YY',
      '%Y': 'YYYY',
      '%H': 'HH',
      '%I': 'hh',
      '%p': 'A',
      '%M': 'mm',
      '%S': 'ss',
      '%f': 'SSS',
      '%z': 'ZZ',
      '%Z': 'z',
      '%j': 'DDDD',
      '%U': 'ww',		    // Week day of the year, Sunday first - not supported
      '%W': 'ww',		    // Week day of the year, Monday first
      '%c': 'ddd MMM DD HH:mm:ss YYYY',
      '%x': 'MM/DD/YYYY',
      '%X': 'HH:mm:ss',
      '%%': '%'
    });

    var convertFormat = function(format) {
      var converted = format;
      for(var name in pythonToJsFormats) {
        if (pythonToJsFormats.hasOwnProperty(name)) {
          converted = converted.split(name).join(pythonToJsFormats[name]);
        }
      }

      return converted;
    };

    $('.navbar-minimalize').on('click', function(event){
      changeProfileField('nav_expanded', !$('body').hasClass('mini-navbar'));
    });

    $('input[type="date-local"]').datetimepicker({
      calendarWeeks: false,
      format: convertFormat(get_format('DATE_INPUT_FORMATS')[0]),
      showClear: true,
      showClose: true,
      showTodayButton: true,
      useCurrent: false,
    });

    $('input[type="time-local"]').clockpicker({
      autoclose: true,
    });

    $('input[type="datetime"]').datetimepicker({
      calendarWeeks: false,
      format: convertFormat(get_format('DATETIME_INPUT_FORMATS')[2]),
      sideBySide: true,
      showClear: true,
      showClose: true,
      showTodayButton: true,
      useCurrent: false,
    });

    new ClipboardJS('.btn[data-clipboard-target^="#"]');

    $('#profileDropdown').on('show.bs.dropdown', function(event){
      console.log(event);
    });
});
