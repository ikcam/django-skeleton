from django.contrib import admin

from .models import Event, Link, Message


class EventModelAdmin(admin.ModelAdmin):
    model = Event


admin.site.register(Event, EventModelAdmin)


class LinkModelAdmin(admin.ModelAdmin):
    model = Link


admin.site.register(Link, LinkModelAdmin)


class MessageModelAdmin(admin.ModelAdmin):
    model = Message
    list_display = (
        'from_', 'to', 'company', 'date_creation', 'direction'
    )
    list_filter = ('company', 'direction')


admin.site.register(Message, MessageModelAdmin)
