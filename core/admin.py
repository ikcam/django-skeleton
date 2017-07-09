from django.contrib import admin

from .models import (
    Company, Invite, Invoice, Payment
)


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
