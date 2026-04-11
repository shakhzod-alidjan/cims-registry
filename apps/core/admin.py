from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Site, UserSiteRole


class UserSiteRoleInline(admin.TabularInline):
    model = UserSiteRole
    extra = 1
    fields = ('site', 'role')


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = [UserSiteRoleInline]
    list_display  = ('username', 'get_full_name', 'email', 'role', 'is_active')
    list_filter   = ('role', 'is_active', 'sites')
    fieldsets     = BaseUserAdmin.fieldsets + (
        ('Роль и объекты', {'fields': ('role', 'telegram_chat_id', 'notify_email', 'notify_telegram')}),
    )


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display  = ('name', 'code', 'color', 'is_active')
    list_editable = ('is_active',)
    search_fields = ('name', 'code')
    prepopulated_fields = {'code': ('name',)}
