from django.contrib import admin
from django.utils.html import format_html
from .models import ISPOperator, ISPContract


@admin.register(ISPOperator)
class ISPOperatorAdmin(admin.ModelAdmin):
    list_display  = ('name', 'contact_name', 'contact_email', 'contact_phone')
    search_fields = ('name',)


@admin.register(ISPContract)
class ISPContractAdmin(admin.ModelAdmin):
    list_display  = ('service_name', 'operator', 'site', 'service_type',
                     'speed', 'cost_uzs', 'end_date', 'status_badge')
    list_filter   = ('site', 'operator', 'service_type')
    search_fields = ('service_name', 'contract_number', 'ip_address')
    date_hierarchy = 'end_date'

    fieldsets = (
        ('Основное', {'fields': ('site', 'operator', 'service_type', 'service_name', 'tariff', 'location')}),
        ('Технические', {'fields': ('speed', 'ip_address')}),
        ('Договор', {'fields': ('contract_number', 'contract_file', 'start_date', 'end_date', 'auto_renewal')}),
        ('Оплата', {'fields': ('cost_uzs', 'cost_usd', 'payment_method', 'next_payment')}),
        ('Примечания', {'fields': ('notes',)}),
    )

    def status_badge(self, obj):
        s = obj.status
        if s == 'expired':
            return format_html('<span style="color:#BF2600;font-weight:600">Истёк</span>')
        if s == 'expiring_soon':
            return format_html('<span style="color:#974F0C;font-weight:600">⚠ Скоро</span>')
        return format_html('<span style="color:#006644;font-weight:600">Активен</span>')
    status_badge.short_description = 'Статус'
