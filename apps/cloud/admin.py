from django.contrib import admin
from django.utils.html import format_html
from .models import CloudProvider, CloudServer


@admin.register(CloudProvider)
class CloudProviderAdmin(admin.ModelAdmin):
    list_display  = ('name', 'contact_email', 'billing_url')
    search_fields = ('name',)


@admin.register(CloudServer)
class CloudServerAdmin(admin.ModelAdmin):
    list_display  = ('name', 'provider', 'site', 'server_type', 'spec_display',
                     'os', 'cost_usd', 'billing_period', 'next_payment', 'status_badge')
    list_filter   = ('site', 'provider', 'server_type', 'status', 'billing_period')
    search_fields = ('name', 'purpose', 'ip_address')

    fieldsets = (
        ('Основное', {'fields': ('site', 'provider', 'server_type', 'name', 'purpose', 'status')}),
        ('Характеристики', {'fields': ('cpu', 'ram_gb', 'disk_gb', 'disk_type', 'os', 'ip_address')}),
        ('Оплата', {'fields': ('cost_usd', 'billing_period', 'next_payment')}),
        ('Примечания', {'fields': ('notes',)}),
    )

    def spec_display(self, obj):
        return obj.spec or '—'
    spec_display.short_description = 'Характеристики'

    def status_badge(self, obj):
        if obj.status == 'active':
            return format_html('<span style="color:#006644;font-weight:600">Активен</span>')
        return format_html('<span style="color:#BF2600;font-weight:600">Остановлен</span>')
    status_badge.short_description = 'Статус'
