from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _

from rest_framework.authtoken.admin import TokenAdmin

from .models import (
    Colaborator, Company, Event, Invite, Link, Message, Notification, Role,
    User
)


# Mixin
class CompanyAdminMixin(admin.ModelAdmin):
    list_filter = ('company', )

    def has_add_permission(self, request):
        return False


# TabularInline

class ColaboratorInline(admin.TabularInline):
    autocomplete_fields = ('user', 'company', )
    extra = 0
    fields = ('user', 'company', 'is_active', )
    model = Colaborator


class LinkInline(admin.TabularInline):
    extra = 0
    model = Link


# ModelAdmin
admin.site.unregister(Group)


@admin.register(Colaborator)
class ColaboratorAdmin(admin.ModelAdmin):
    list_display = ('user', 'company', 'date_creation', 'is_active', )
    list_filter = ('company', )


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    autocomplete_fields = (
        'user',
    )
    inlines = (
        ColaboratorInline,
    )
    list_display = ('name', 'user', )
    search_fields = ('name', )


@admin.register(Event)
class EventAdmin(CompanyAdminMixin):
    autocomplete_fields = (
        'user', 'share_with',
    )
    list_display = (
        '__str__', 'company', 'user', 'date_start', 'date_finish'
    )


@admin.register(Invite)
class InviteAdmin(CompanyAdminMixin):
    list_display = (
        '__str__', 'company', 'date_creation', 'name', 'email'
    )
    search_fields = ('id', )


@admin.register(Link)
class LinkModelAdmin(CompanyAdminMixin):
    list_display = ('destination', 'message', 'user')


@admin.register(Message)
class MessageAdmin(CompanyAdminMixin):
    inlines = (
        LinkInline,
    )
    list_display = (
        'from_', 'to', 'company', 'date_creation', 'direction'
    )
    list_filter = ('company', 'direction')


@admin.register(Notification)
class NotificationAdmin(CompanyAdminMixin):
    list_display = (
        'user', 'company', 'date_creation', 'content',
    )


@admin.register(Role)
class RoleAdmin(CompanyAdminMixin):
    filter_horizontal = ('permissions',)
    list_display = ('name', 'company')
    search_fields = ('name', )


@admin.register(User)
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
                    'first_name', 'last_name', 'email', 'timezone', 'language',
                    'photo',
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


TokenAdmin.raw_id_fields = ('user',)
