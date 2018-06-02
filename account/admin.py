from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Colaborator, User


class ColaboratorAdmin(admin.ModelAdmin):
    list_display = ('user', 'company', 'date_joined', 'is_active', )
    list_filter = ('company', )


admin.site.register(Colaborator, ColaboratorAdmin)


admin.site.register(User, UserAdmin)
