from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _

from .models import (
    Company, Invite, Invoice, Payment, Role
)

from .models import Colaborator, User


class ColaboratorAdmin(admin.ModelAdmin):
    list_display = ('user', 'company', 'date_joined', 'is_active', )
    list_filter = ('company', )


admin.site.register(Colaborator, ColaboratorAdmin)


class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', )
    search_fields = ('name', )


admin.site.register(Company, CompanyAdmin)


class PaymentInline(admin.TabularInline):
    model = Payment


class InvoiceAdmin(admin.ModelAdmin):
    inlines = (PaymentInline, )
    list_display = ('id', 'company', 'total')
    list_filter = ('company', )
    search_fields = ('id', )


admin.site.register(Invoice, InvoiceAdmin)


class InviteAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'email', 'user')
    list_filter = ('company', )
    search_fields = ('name', 'email')


admin.site.register(Invite, InviteAdmin)


class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'company')
    list_filter = ('company', )
    search_fields = ('name', )


admin.site.register(Role, RoleAdmin)


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


admin.site.register(User, UserAdmin)
