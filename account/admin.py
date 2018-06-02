from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _

from .models import Colaborator, User


class ColaboratorAdmin(admin.ModelAdmin):
    list_display = ('user', 'company', 'date_joined', 'is_active', )
    list_filter = ('company', )


admin.site.register(Colaborator, ColaboratorAdmin)


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
