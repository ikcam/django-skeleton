from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import Colaborator, Profile


class ColaboratorAdmin(admin.ModelAdmin):
    list_display = ('profile', 'company', 'date_joined', 'is_active', )
    list_filter = ('company', )


admin.site.register(Colaborator, ColaboratorAdmin)


class ProfileInline(admin.StackedInline):
    model = Profile


class UserAdmin(UserAdmin):
    inlines = [
        ProfileInline,
    ]


admin.site.unregister(User)


admin.site.register(User, UserAdmin)
