from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from .models import BusinessApp, License, Vendor
from apps.core.models import Site
import json


def _site_filter(request):
    site = getattr(request, 'current_site', None)
    if site:
        return {'site': site}
    accessible = [s.id for s in request.user.get_accessible_sites()]
    return {'site_id__in': accessible}


@login_required
def license_list(request):
    sf = _site_filter(request)
    filter_tag = request.GET.get('f', '')

    apps = BusinessApp.objects.filter(
        licenses__isnull=False, **({'licenses__' + k: v for k, v in sf.items()})
    ).distinct().select_related('vendor').prefetch_related('sites')

    # Apply tag filter
    if filter_tag == 'expired':
        from django.utils import timezone
        apps = apps.filter(licenses__expiry_date__lt=timezone.now().date(), **({'licenses__' + k: v for k, v in sf.items()})).distinct()
    elif filter_tag in ('noventiq', '1c', 'mining'):
        tag_map = {'noventiq': 'Noventiq', '1c': '1С', 'mining': 'mining'}
        apps = apps.filter(vendor__name__icontains=tag_map[filter_tag]) if filter_tag != 'mining' else apps.filter(category='mining')

    grouped = []
    total_cost = 0
    active_count = 0
    expired_count = 0

    for app in apps.order_by('name'):
        lics = app.licenses.filter(**sf).order_by('license_type')
        if not lics.exists():
            continue

        # Compute summary values in Python (no Django template math)
        app_total = sum((l.total_cost or 0) for l in lics)
        first_price = next((l.price_per_unit for l in lics if l.price_per_unit), None)
        worst_days = None
        worst_expiry = None
        worst_status = 'active'

        for lic in lics:
            d = lic.days_until_expiry
            if d is not None:
                if worst_days is None or d < worst_days:
                    worst_days = d
                    worst_expiry = lic.expiry_date
            if lic.status == 'expired':
                expired_count += 1
                worst_status = 'expired'
            elif lic.status in ('expiring_soon', 'expiring') and worst_status != 'expired':
                worst_status = lic.status
            elif lic.status == 'active' and worst_status == 'active':
                active_count += 1

        total_cost += app_total

        grouped.append({
            'app': app,
            'licenses': lics,
            'first_lic': lics.first(),
            'total_cost': app_total,
            'total_display': f'${app_total:,.0f}' if app_total else '—',
            'price_display': f'${first_price:,.0f}' if first_price else '—',
            'worst_days': worst_days,
            'worst_expiry': worst_expiry,
            'worst_status': worst_status,
        })

    total_records = sum(item['licenses'].count() for item in grouped)

    ctx = {
        'grouped': grouped,
        'total_apps': len(grouped),
        'total_records': total_records,
        'total_cost': total_cost,
        'active_count': active_count,
        'expired_count': expired_count,
        'filter_tag': filter_tag,
    }
    return render(request, 'licenses/list.html', ctx)


@login_required
def license_detail(request, pk):
    lic = get_object_or_404(License, pk=pk)
    if not request.user.is_admin:
        if lic.site not in request.user.get_accessible_sites():
            messages.error(request, 'Нет доступа')
            return redirect('license_list')

    rows = [
        ('Приложение',          lic.app.name),
        ('Объект',              lic.site.name),
        ('Тип лицензии',        lic.get_license_type_display()),
        ('Вендор',              str(lic.app.vendor) if lic.app.vendor else '—'),
        ('Куплено (шт.)',       lic.quantity_total or '—'),
        ('Используется (шт.)',  lic.quantity_used or '—'),
        ('Свободно (шт.)',      lic.quantity_free if lic.quantity_free is not None else '—'),
        ('Цена за ед. (USD)',   f'${lic.price_per_unit:,.0f}' if lic.price_per_unit else '—'),
        ('Итого (USD)',         f'${lic.total_cost:,.0f}' if lic.total_cost else '—'),
        ('№ договора',          lic.contract_number or '—'),
        ('Дата покупки',        lic.purchase_date or '—'),
        ('Дата истечения',      lic.expiry_date or 'Бессрочно'),
        ('Дней до истечения',   f'{lic.days_until_expiry} дн.' if lic.days_until_expiry is not None else '—'),
        ('Примечания',          lic.notes or '—'),
    ]
    return render(request, 'licenses/detail.html', {'license': lic, 'rows': rows})


@login_required
def license_add(request):
    if not request.user.is_editor:
        messages.error(request, 'Нет прав для добавления')
        return redirect('license_list')

    if request.method == 'POST':
        from .forms import LicenseForm
        form = LicenseForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            lic = form.save()
            messages.success(request, f'Лицензия «{lic.app.name}» добавлена')
            return redirect('license_list')
    else:
        from .forms import LicenseForm
        form = LicenseForm(user=request.user)

    return render(request, 'licenses/form.html', {'form': form, 'title': 'Добавить лицензию'})


@login_required
def license_edit(request, pk):
    lic = get_object_or_404(License, pk=pk)
    if not request.user.is_editor:
        messages.error(request, 'Нет прав')
        return redirect('license_list')

    if request.method == 'POST':
        from .forms import LicenseForm
        form = LicenseForm(request.POST, request.FILES, instance=lic, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Лицензия обновлена')
            return redirect('license_list')
    else:
        from .forms import LicenseForm
        form = LicenseForm(instance=lic, user=request.user)

    return render(request, 'licenses/form.html', {'form': form, 'title': 'Редактировать лицензию', 'license': lic})


@login_required
@require_POST
def license_delete(request, pk):
    if not request.user.is_admin:
        return JsonResponse({'error': 'Нет прав'}, status=403)
    lic = get_object_or_404(License, pk=pk)
    lic.delete()
    messages.success(request, 'Лицензия удалена')
    return redirect('license_list')


@login_required
def export_excel(request):
    """Запустить асинхронный экспорт через Celery."""
    from apps.notifications.tasks import export_licenses_to_excel
    site = getattr(request, 'current_site', None)
    export_licenses_to_excel.delay(
        site_id=site.id if site else None,
        user_email=request.user.email,
    )
    messages.success(request, 'Экспорт запущен — файл придёт на email')
    return redirect('license_list')
