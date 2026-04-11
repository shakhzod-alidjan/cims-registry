from django.contrib import admin
from django.utils.html import format_html
from .models import Registrar, Domain, DomainPayment


@admin.register(Registrar)
class RegistrarAdmin(admin.ModelAdmin):
    list_display  = ('name', 'url', 'contact_email')
    search_fields = ('name',)


class DomainPaymentInline(admin.TabularInline):
    model  = DomainPayment
    extra  = 1
    fields = ('paid_date', 'amount', 'paid_by', 'notes')


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display   = ('name', 'site', 'registrar', 'expiry_date', 'cost_usd', 'status_badge')
    list_filter    = ('site', 'registrar')
    search_fields  = ('name',)
    date_hierarchy = 'expiry_date'
    inlines        = [DomainPaymentInline]

    fieldsets = (
        ('Основное', {'fields': ('site', 'registrar', 'name')}),
        ('Даты', {'fields': ('registration_date', 'expiry_date', 'auto_renewal')}),
        ('Финансы', {'fields': ('cost_usd',)}),
        ('Примечания', {'fields': ('notes',)}),
    )

    def status_badge(self, obj):
        s = obj.status
        if s == 'expired':
            return format_html('<span style="color:#BF2600;font-weight:600">Истёк</span>')
        if s == 'expiring_soon':
            return format_html('<span style="color:#974F0C;font-weight:600">⚠ {}</span>',
                               f'{obj.days_until_expiry} дн.')
        return format_html('<span style="color:#006644;font-weight:600">Активен</span>')
    status_badge.short_description = 'Статус'


@admin.register(DomainPayment)
class DomainPaymentAdmin(admin.ModelAdmin):
    list_display  = ('domain', 'paid_date', 'amount', 'paid_by')
    list_filter   = ('domain__site',)
    search_fields = ('domain__name', 'paid_by')
