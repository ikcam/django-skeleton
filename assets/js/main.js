(function(globals) {
    var django = globals.django || (globals.django = {});

    django.get_cookie = function(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== "") {
            var cookies = document.cookie.split(";");
            cookies.forEach(function checkCookie(i) {
                var cookie = jQuery.trim(i);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(
                        cookie.substring(name.length + 1)
                    );
                }
                return cookieValue !== null;
            });
        }
        return cookieValue;
    };

    var pythonToJsFormats = Object({
        "%a": "ddd",
        "%A": "dddd",
        "%w": "d",
        "%d": "DD",
        "%b": "MMM",
        "%B": "MMMM",
        "%m": "MM",
        "%y": "YY",
        "%Y": "YYYY",
        "%H": "HH",
        "%I": "hh",
        "%p": "A",
        "%M": "mm",
        "%S": "ss",
        "%f": "SSS",
        "%z": "ZZ",
        "%Z": "z",
        "%j": "DDDD",
        "%U": "ww",
        "%W": "ww",
        "%c": "ddd MMM DD HH:mm:ss YYYY",
        "%x": "MM/DD/YYYY",
        "%X": "HH:mm:ss",
        "%%": "%"
    });

    django.convert_format = function(format) {
        var converted = format;

        for (name in pythonToJsFormats) {
            if (Object.prototype.hasOwnProperty.call(pythonToJsFormats, name)) {
                converted = converted.split(name).join(pythonToJsFormats[name]);
            }
        }

        return converted;
    };

    if (!django.djaneiro_initialized) {
        globals.get_cookie = django.get_cookie;
        globals.convert_format = django.convert_format;

        django.djaneiro_initialized = true;
    }
}(this));


jQuery(document).ready(function($){
    function angularInit(){
        var ngApps = $('html').attr('ng-apps').split(',');
        angular.bootstrap(document, ngApps);
    }

    angularInit();
});
