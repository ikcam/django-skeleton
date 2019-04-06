/* eslint-disable func-names */
(function (globals) {
    const django = globals.django || (globals.django = {});

    // eslint-disable-next-line prettier/prettier
    django.get_cookie = function (name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");
            cookies.forEach(function checkCookie(i) {
                // eslint-disable-next-line no-undef
                const cookie = jQuery.trim(i);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === `${name}=`) {
                    cookieValue = decodeURIComponent(
                        cookie.substring(name.length + 1)
                    );
                }
                return cookieValue !== null;
            });
        }
        return cookieValue;
    };

    const pythonToJsFormats = Object({
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

    // eslint-disable-next-line no-unused-vars
    // eslint-disable-next-line func-names
    django.convert_format = function (format) {
        let converted = format;

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


// eslint-disable-next-line no-undef
jQuery(document).ready(function ($) {
    $('[data-toggle="datetimepicker"]').each(function () {
        $(this).datetimepicker({
            calendarWeeks: false,
            format: django.convert_format(django.formats.DATE_INPUT_FORMATS[0]),
            locale: $("html").attr("lang"),
            showClear: true,
            showClose: true,
            showTodayButton: true,
            sideBySide: true,
            useCurrent: false
        });
    });
});
