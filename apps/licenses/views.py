from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import BusinessApp, License, Vendor
from apps.core.models import Site
from apps.core.views import _get_usd_rate
from decimal import Decimal


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
    usd_rate = _get_usd_rate()

    apps = BusinessApp.objects.filter(
        licenses__isnull=False,
        **({'licenses__' + k: v for k, v in sf.items()})
    ).distinct().select_related('vendor').prefetch_related('sites')

    if filter_tag == 'expired':
        from django.utils import timezone
        apps = apps.filter(
            licenses__expiry_date__lt=timezone.now().date(),
            **({'licenses__' + k: v for k, v in sf.items()})
        ).distinct()
    elif filter_tag == 'noventiq':
        apps = apps.filter(vendor__name__icontains='noventiq')
    elif filter_tag == '1c':
        apps = apps.filter(vendor__name__icontains='1с') | apps.filter(name__icontains='1с')
    elif filter_tag == 'mining':
        apps = apps.filter(category='mining')

    grouped = []
    total_cost_usd = Decimal('0')
    total_cost_uzs = Decimal('0')
    active_count = 0
    expired_count = 0

    for app in apps.order_by('name'):
        lics = app.licenses.filter(**sf).order_by('license_type')
        if not lics.exists():
            continue

        app_cost_usd = Decimal('0')
        worst_days = None
        worst_expiry = None
        worst_status = 'active'

        for lic in lics:
            # Cost in USD
            price_usd = lic.get_price_usd(usd_rate)
            if price_usd and lic.quantity_total:
                app_cost_usd += price_usd * lic.quantity_total

            # Status
            if lic.status == 'expired':
                expired_count += 1
                worst_status = 'expired'
            elif lic.status in ('expiring_soon', 'expiring') and worst_status != 'expired':
                worst_status = lic.status
            elif lic.status == 'active' and worst_status == 'active':
                active_count += 1

            # Worst expiry
            d = lic.days_until_expiry
            if d is not None and (worst_days is None or d < worst_days):
                worst_days = d
                worst_expiry = lic.expiry_date

        total_cost_usd += app_cost_usd
        total_cost_uzs += app_cost_usd * usd_rate

        grouped.append({
            'app':           app,
            'licenses':      lics,
            'total_cost_usd': app_cost_usd,
            'total_cost_uzs': app_cost_usd * usd_rate,
            'worst_days':    worst_days,
            'worst_expiry':  worst_expiry,
            'worst_status':  worst_status,
        })

    ctx = {
        'grouped':        grouped,
        'total_apps':     len(grouped),
        'total_records':  sum(item['licenses'].count() for item in grouped),
        'total_cost_usd': total_cost_usd,
        'total_cost_uzs': total_cost_uzs,
        'active_count':   active_count,
        'expired_count':  expired_count,
        'filter_tag':     filter_tag,
        'usd_rate':       usd_rate,
    }
    return render(request, 'licenses/list.html', ctx)


@login_required
def license_detail(request, pk):
    lic = get_object_or_404(License, pk=pk)
    if not request.user.is_admin:
        if lic.site not in request.user.get_accessible_sites():
            messages.error(request, 'Нет доступа')
            return redirect('license_list')
    usd_rate = _get_usd_rate()
    rows = [
        ('Приложение',         lic.app.name),
        ('Объект',             lic.site.name),
        ('Тип лицензии',       lic.get_license_type_display()),
        ('Вендор',             str(lic.app.vendor) if lic.app.vendor else '—'),
        ('Куплено (шт.)',      lic.quantity_total or '—'),
        ('Используется (шт.)', lic.quantity_used or '—'),
        ('Свободно (шт.)',     lic.quantity_free if lic.quantity_free is not None else '—'),
        ('Цена за ед.',        f'{lic.price_per_unit:,.2f} {lic.currency}' if lic.price_per_unit else '—'),
        ('Итого',              f'{lic.total_cost:,.2f} {lic.currency}' if lic.total_cost else '—'),
        ('Итого (USD)',        f'${lic.get_price_usd(usd_rate) * lic.quantity_total:,.0f}' if lic.get_price_usd(usd_rate) and lic.quantity_total else '—'),
        ('№ договора',         lic.contract_number or '—'),
        ('Дата покупки',       lic.purchase_date or '—'),
        ('Дата истечения',     lic.expiry_date or 'Бессрочно'),
        ('Дней до истечения',  f'{lic.days_until_expiry} дн.' if lic.days_until_expiry is not None else '—'),
        ('Примечания',         lic.notes or '—'),
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
    from apps.notifications.tasks import export_licenses_to_excel
    site = getattr(request, 'current_site', None)
    export_licenses_to_excel.delay(
        site_id=site.id if site else None,
        user_email=request.user.email,
    )
    messages.success(request, 'Экспорт запущен — файл придёт на email')
    return redirect('license_list')
