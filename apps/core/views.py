from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from apps.core.models import Site
from apps.licenses.models import License
from apps.internet.models import ISPContract
from apps.dns.models import Domain
from apps.cloud.models import CloudServer
from django.utils import timezone
from decimal import Decimal
import requests as http_requests


def _get_usd_rate():
    """Курс USD/UZS из ЦБ Узбекистана."""
    try:
        resp = http_requests.get(
            'https://cbu.uz/uz/arkhiv-kursov-valyut/json/USD/',
            timeout=3
        )
        return Decimal(str(resp.json()[0]['Rate']))
    except Exception:
        return Decimal('12800')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    error = None
    if request.method == 'POST':
        user = authenticate(
            request,
            username=request.POST.get('username'),
            password=request.POST.get('password'),
        )
        if user:
            login(request, user)
            return redirect(request.GET.get('next', 'dashboard'))
        error = 'Неверный логин или пароль'
    return render(request, 'core/login.html', {'error': error})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    site = request.current_site
    accessible_ids = [s.id for s in request.user.get_accessible_sites()]
    site_filter = {'site_id': site.id} if site else {'site_id__in': accessible_ids}

    today       = timezone.now().date()
    deadline_30 = today + timezone.timedelta(days=30)
    deadline_90 = today + timezone.timedelta(days=90)

    # Курс валют
    usd_rate = _get_usd_rate()

    # ── KPI counts ────────────────────────────────────────
    lic_total    = License.objects.filter(**site_filter).count()
    lic_expiring = License.objects.filter(
        **site_filter, expiry_date__lte=deadline_30, expiry_date__gte=today
    ).count()
    lic_expired  = License.objects.filter(**site_filter, expiry_date__lt=today).count()

    isp_total    = ISPContract.objects.filter(**site_filter).count()
    isp_expired  = ISPContract.objects.filter(**site_filter, end_date__lt=today).count()

    dom_total    = Domain.objects.filter(**site_filter).count()
    dom_expiring = Domain.objects.filter(
        **site_filter, expiry_date__lte=deadline_30, expiry_date__gte=today
    ).count()

    # ── IT Budget — всё конвертируем в USD ───────────────
    # Лицензии
    total_lic_usd = sum(
        (lic.get_price_usd(usd_rate) * lic.quantity_total
         for lic in License.objects.filter(**site_filter)
         if lic.price_per_unit and lic.quantity_total),
        Decimal('0')
    )

    # ISP (ежемесячно → годовой)
    total_isp_usd = sum(
        (c.get_cost_usd_monthly(usd_rate) * 12
         for c in ISPContract.objects.filter(**site_filter)),
        Decimal('0')
    )
    total_isp_uzs = total_isp_usd * usd_rate

    # Cloud (ежемесячно → годовой)
    total_cloud_usd = sum(
        (s.get_cost_usd_monthly(usd_rate) * 12
         for s in CloudServer.objects.filter(**site_filter)),
        Decimal('0')
    )

    # DNS (годовая стоимость)
    total_dns_usd = sum(
        (d.get_cost_usd(usd_rate)
         for d in Domain.objects.filter(**site_filter)),
        Decimal('0')
    )

    grand_total_usd = total_lic_usd + total_isp_usd + total_cloud_usd + total_dns_usd
    grand_total_uzs = grand_total_usd * usd_rate

    # ── Expiring soon ─────────────────────────────────────
    expiring_licenses = License.objects.filter(
        **site_filter,
        expiry_date__isnull=False,
        expiry_date__lte=deadline_90,
    ).select_related('app', 'site').order_by('expiry_date')[:10]

    expiring_domains = Domain.objects.filter(
        **site_filter,
        expiry_date__isnull=False,
        expiry_date__lte=deadline_90,
    ).select_related('site', 'registrar').order_by('expiry_date')[:5]

    ctx = {
        'lic_total':         lic_total,
        'lic_expiring':      lic_expiring,
        'lic_expired':       lic_expired,
        'isp_total':         isp_total,
        'isp_expired':       isp_expired,
        'dom_total':         dom_total,
        'dom_expiring':      dom_expiring,
        'total_lic_usd':     total_lic_usd,
        'total_lic_uzs':     total_lic_usd * usd_rate,
        'total_isp_usd':     total_isp_usd,
        'total_isp_uzs':     total_isp_uzs,
        'total_cloud_usd':   total_cloud_usd,
        'total_cloud_uzs':   total_cloud_usd * usd_rate,
        'total_dns_usd':     total_dns_usd,
        'total_dns_uzs':     total_dns_usd * usd_rate,
        'grand_total_usd':   grand_total_usd,
        'grand_total_uzs':   grand_total_uzs,
        'usd_rate':          usd_rate,
        'expiring_licenses': expiring_licenses,
        'expiring_domains':  expiring_domains,
        'today':             today,
    }
    return render(request, 'core/dashboard.html', ctx)


@login_required
@require_POST
def switch_site(request):
    site_id = request.POST.get('site_id')
    if site_id == 'all':
        request.session.pop('current_site_id', None)
        return JsonResponse({'ok': True, 'site': 'all', 'name': 'Все объекты'})

    accessible = request.user.get_accessible_sites()
    site = accessible.filter(id=site_id).first()
    if not site:
        return JsonResponse({'ok': False, 'error': 'Нет доступа'}, status=403)

    request.session['current_site_id'] = site.id
    return JsonResponse({'ok': True, 'site': site.id, 'name': site.name, 'color': site.color})
