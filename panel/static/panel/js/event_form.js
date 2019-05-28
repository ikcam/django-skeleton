/* global jQuery */
jQuery(document).ready(function($){
    $('[data-datetimepicker="datetime"]').datetimepicker({
        calendarWeeks: false,
        format: convert_format(get_format('DATETIME_INPUT_FORMATS')[2]),
        locale: $('html').attr('lang'),
        sideBySide: true,
        showClear: true,
        showClose: true,
        showTodayButton: true,
        useCurrent: false
    });

    $("#id_date_start").on("dp.change", function (e) {
        $('#id_date_finish').data("DateTimePicker").minDate(e.date);
    });
    $("#id_date_finish").on("dp.change", function (e) {
        $('#id_date_start').data("DateTimePicker").maxDate(e.date);
    });
});
