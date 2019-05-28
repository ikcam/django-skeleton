/* global alert, jQuery, getCookie */
jQuery(document).ready(function ($) {
  $('*[data-type="livelist"]').each(function () {
    $(this).change(function () {
      var object = $(this)
      var endpoint = $(this).attr('data-endpoint')
      var name = $(this).attr('data-name')
      var value = $(this).val()
      var data = {}

      data[name] = value
      object.prop('disabled', true)

      $.ajax({
        type: 'PATCH',
        url: endpoint,
        data: data,
        headers: {
          'X-CSRFToken': getCookie('csrftoken')
        },
        success: function (response) {
          object.prop('disabled', false)
        },
        error: function (response) {
          var jsonResponse = jQuery.parseJSON(response.responseText)
          alert(jsonResponse.detail)
          object.prop('disabled', false)
        }
      })
    })
  })
})
