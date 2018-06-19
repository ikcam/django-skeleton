from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _

from .models import (
    Colaborator, Company, Event, Invite, Invoice, Link, Message, Payment,
    Role, User
)


class ColaboratorAdmin(admin.ModelAdmin):
    list_display = ('user', 'company', 'date_joined', 'is_active', )
    list_filter = ('company', )


class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', )
    search_fields = ('name', )


class EventModelAdmin(admin.ModelAdmin):
    model = Event


class PaymentInline(admin.TabularInline):
    model = Payment


class InvoiceAdmin(admin.ModelAdmin):
    inlines = (PaymentInline, )
    list_display = ('id', 'company', 'total')
    list_filter = ('company', )
    search_fields = ('id', )


class InviteAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'email', 'user')
    list_filter = ('company', )
    search_fields = ('name', 'email')


class LinkModelAdmin(admin.ModelAdmin):
    model = Link


class MessageModelAdmin(admin.ModelAdmin):
    model = Message
    list_display = (
        'from_', 'to', 'company', 'date_creation', 'direction'
    )
    list_filter = ('company', 'direction')


class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'company')
    list_filter = ('company', )
    search_fields = ('name', )


class UserAdmin(UserAdmin):
    fieldsets = (
        (
            None, {
                'fields': ('username', 'password')
            },
        ),
        (
            _("Personal info"), {
                'fields': (
                    'first_name', 'last_name', 'email', 'timezone', 'language'
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


admin.site.register(Company, CompanyAdmin)
admin.site.register(Colaborator, ColaboratorAdmin)
admin.site.register(Event, EventModelAdmin)
admin.site.register(Invite, InviteAdmin)
admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(Link, LinkModelAdmin)
admin.site.register(Message, MessageModelAdmin)
admin.site.register(Role, RoleAdmin)
admin.site.register(User, UserAdmin)
