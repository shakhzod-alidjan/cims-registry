from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Vendor, BusinessApp, License


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display  = ('name', 'contact_name', 'contact_email', 'contact_phone', 'country')
    search_fields = ('name', 'contact_name', 'contact_email')
    list_filter   = ('country',)


class LicenseInline(admin.TabularInline):
    model  = License
    extra  = 1
    fields = ('site', 'license_type', 'quantity_total', 'quantity_used',
              'price_per_unit', 'expiry_date', 'contract_file')
    show_change_link = True


@admin.register(BusinessApp)
class BusinessAppAdmin(admin.ModelAdmin):
    list_display  = ('name', 'vendor', 'category', 'sites_list', 'is_active')
    list_filter   = ('category', 'is_active', 'vendor')
    search_fields = ('name',)
    filter_horizontal = ('sites',)
    inlines = [LicenseInline]

    def sites_list(self, obj):
        return ', '.join(s.name for s in obj.sites.all())
    sites_list.short_description = 'Объекты'


@admin.register(License)
class LicenseAdmin(admin.ModelAdmin):
    list_display  = ('app', 'site', 'license_type', 'quantity_total', 'quantity_used',
                     'price_per_unit', 'total_cost_display', 'expiry_date', 'status_badge')
    list_filter   = ('site', 'license_type', 'app__category', 'app__vendor')
    search_fields = ('app__name', 'contract_number')
    date_hierarchy = 'expiry_date'
    readonly_fields = ('quantity_free', 'total_cost', 'days_until_expiry', 'status')

    fieldsets = (
        ('Основное', {'fields': ('app', 'site', 'license_type', 'license_type_custom')}),
        ('Количество', {'fields': ('quantity_total', 'quantity_used', 'quantity_free')}),
        ('Финансы', {'fields': ('price_per_unit', 'total_cost', 'contract_number')}),
        ('Даты', {'fields': ('purchase_date', 'expiry_date', 'days_until_expiry', 'status')}),
        ('Документы', {'fields': ('contract_file',)}),
        ('Примечания', {'fields': ('notes',)}),
    )

    def total_cost_display(self, obj):
        tc = obj.total_cost
        return f'${tc:,.0f}' if tc else '—'
    total_cost_display.short_description = 'Итого'

    def status_badge(self, obj):
        colors = {
            'expired':      ('#BF2600', 'Истекла'),
            'expiring_soon':('#974F0C', '⚠ Скоро'),
            'expiring':     ('#974F0C', 'Внимание'),
            'active':       ('#006644', 'Активна'),
        }
        color, label = colors.get(obj.status, ('#666', obj.status))
        return format_html('<span style="color:{};font-weight:600">{}</span>', color, label)
    status_badge.short_description = 'Статус'
