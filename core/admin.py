from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db import models
from django.utils.translation import ugettext_lazy as _

from .models import (
    Colaborator, Company, Event, Invite, Invoice, Link, Message, Payment,
    Notification, Role, User
)


# TabularInline

class ColaboratorInline(admin.TabularInline):
    autocomplete_fields = ('user', 'company', )
    extra = 0
    fields = ('user', 'company', 'is_active', 'roles', 'permissions')
    model = Colaborator


class LinkInline(admin.TabularInline):
    extra = 0
    model = Link


class PaymentInline(admin.TabularInline):
    extra = 1
    formfield_overrides = {
        models.TextField: {'widget': forms.TextInput},
    }
    model = Payment


# ModelAdmin

class ColaboratorAdmin(admin.ModelAdmin):
    list_display = ('user', 'company', 'date_joined', 'is_active', )
    list_filter = ('company', )


class CompanyAdmin(admin.ModelAdmin):
    autocomplete_fields = (
        'user',
    )
    inlines = (
        ColaboratorInline,
    )
    list_display = ('name', 'user', )
    search_fields = ('name', )


class EventModelAdmin(admin.ModelAdmin):
    autocomplete_fields = (
        'share_with',
    )
    model = Event
    list_filter = ('company', )


class InvoiceAdmin(admin.ModelAdmin):
    autocomplete_fields = (
        'company',
    )
    inlines = (PaymentInline, )
    list_display = ('__str__', 'company', 'total')
    list_filter = ('company', )
    search_fields = ('id', )


class InviteAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'email', 'user')
    list_filter = ('company', )
    search_fields = ('name', 'email')


class LinkModelAdmin(admin.ModelAdmin):
    list_display = ('destination', 'message', 'user')
    list_filter = ('company', )
    model = Link


class MessageAdmin(admin.ModelAdmin):
    inlines = (
        LinkInline,
    )
    list_display = (
        'from_', 'to', 'company', 'date_creation', 'direction'
    )
    list_filter = ('company', 'direction')
    model = Message

    def has_add_permission(self, request):
        return False


class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'company', 'date_creation', 'content',
    )
    list_filter = (
        'company',
    )
    model = Notification

    def has_add_permission(self, request):
        return False


class RoleAdmin(admin.ModelAdmin):
    filter_horizontal = ('permissions',)
    list_display = ('name', 'company')
    list_filter = ('company', )
    search_fields = ('name', )


class UserAdmin(UserAdmin):
    autocomplete_fields = (
        'company',
    )
    fieldsets = (
        (
            None, {
                'fields': ('username', 'password')
            },
        ),
        (
            _("Personal info"), {
                'fields': (
                    'first_name', 'last_name', 'email', 'company', 'timezone',
                    'language', 'photo',
                )
            },
        ),
        (
            _("Permissions"), {
                'fields': (
                    'is_active', 'is_staff', 'is_superuser',
                    'groups', 'user_permissions'
                )
            },
        ),
        (
            _("Important dates"), {
                'fields': (
                    'last_login', 'date_joined'
                )
            },
        ),
    )
    inlines = (ColaboratorInline, )
    list_filter = (
        'is_staff', 'is_superuser', 'is_active', 'company'
    )


admin.site.register(Company, CompanyAdmin)
admin.site.register(Colaborator, ColaboratorAdmin)
admin.site.register(Event, EventModelAdmin)
admin.site.register(Invite, InviteAdmin)
admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(Link, LinkModelAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(Role, RoleAdmin)
admin.site.register(User, UserAdmin)
