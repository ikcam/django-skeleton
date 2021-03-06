/* global jQuery, alert */
jQuery(document).ready(function ($) {
  var currentEvent

  $('#event-detail').on('show.bs.modal', function () {
    var modal = $(this)
    modal.find('.modal-title').text(currentEvent.title)
    modal.find('.event-user').text(currentEvent.user || '')
    modal.find('.modal-body .event-date').text(
      moment(currentEvent.start).format('LLLL')
    )
    modal.find('.modal-body .event-end').text(function () {
      if (currentEvent.end) {
        return moment(currentEvent.end).format('LLLL')
      } else {
        return ''
      }
    })
    modal.find('.modal-body .event-content').text(currentEvent.content)
    modal.find('a.event-url').attr('href', currentEvent.url)

    if (currentEvent.is_public) {
      modal.find('span.event-public').show()
      modal.find('span.event-non-public').hide()
    } else {
      modal.find('span.event-non-public').show()
      modal.find('span.event-public').hide()
    }
  })

  const $calendar = $('#calendar')
  $calendar.fullCalendar({
    header: {
      left: 'prev,next today',
      center: 'title',
      right: 'month,agendaWeek,agendaDay,listWeek'
    },
    editable: false,
    locale: $('html').attr('lang'),
    timezone: $('html').attr('tz'),
    eventClick: function (calEvent, jsEvent, view) {
      jsEvent.preventDefault()
      currentEvent = calEvent
      $('#event-detail').modal('show')
    },
    events: {
      url: $calendar.data('remote'),
      type: 'GET',
      startParam: 'date_since',
      endParam: 'date_until',
      data: {
        limit: 1000,
      },
      success: function (data) {
        events = []
        data.results.forEach(function (item) {
          data = {
            id: item.id,
            title: item.subject,
            start: item.date_start || item.date_creation,
            finish: item.date_finish,
            content: item.content,
            color: item.type_color,
            is_public: item.is_public,
            user: item.user,
            creation: item.date_creation,
            url: item.action_list.view.url,
          }
          events.push(data)
        })
        return events
      },
      error: function () {
        alert('there was an error while fetching events!')
      },
    },
  })
})
