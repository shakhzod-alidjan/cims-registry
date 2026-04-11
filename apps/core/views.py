from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from apps.core.models import Site
from apps.licenses.models import License
from apps.internet.models import ISPContract
from apps.dns.models import Domain
from apps.cloud.models import CloudServer
from django.utils import timezone
from decimal import Decimal


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

    today = timezone.now().date()
    deadline_30  = today + timezone.timedelta(days=30)
    deadline_90  = today + timezone.timedelta(days=90)

    # KPI
    lic_total   = License.objects.filter(**site_filter).count()
    lic_expiring = License.objects.filter(**site_filter, expiry_date__lte=deadline_30,
                                          expiry_date__gte=today).count()
    lic_expired = License.objects.filter(**site_filter, expiry_date__lt=today).count()

    isp_total   = ISPContract.objects.filter(**site_filter).count()
    isp_expired = ISPContract.objects.filter(**site_filter, end_date__lt=today).count()

    dom_total   = Domain.objects.filter(**site_filter).count()
    dom_expiring = Domain.objects.filter(**site_filter, expiry_date__lte=deadline_30,
                                         expiry_date__gte=today).count()

    # IT budget estimate
    lic_cost = License.objects.filter(**site_filter).exclude(
        price_per_unit__isnull=True
    ).exclude(quantity_total__isnull=True)
    total_lic_usd = sum(
        (l.price_per_unit * l.quantity_total for l in lic_cost
         if l.price_per_unit and l.quantity_total),
        Decimal('0')
    )
    isp_monthly_uzs = ISPContract.objects.filter(**site_filter).exclude(cost_uzs__isnull=True)
    total_isp_uzs = sum((c.cost_uzs for c in isp_monthly_uzs if c.cost_uzs), Decimal('0'))
    total_isp_usd = total_isp_uzs / Decimal('12800') * 12  # annual

    cloud_monthly = CloudServer.objects.filter(**site_filter).exclude(cost_usd__isnull=True)
    total_cloud_usd = sum((s.cost_usd * 12 for s in cloud_monthly if s.cost_usd), Decimal('0'))

    # Expiring soon list
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
        'lic_total':    lic_total,
        'lic_expiring': lic_expiring,
        'lic_expired':  lic_expired,
        'isp_total':    isp_total,
        'isp_expired':  isp_expired,
        'dom_total':    dom_total,
        'dom_expiring': dom_expiring,
        'total_lic_usd':    total_lic_usd,
        'total_isp_usd':    total_isp_usd,
        'total_cloud_usd':  total_cloud_usd,
        'grand_total_usd':  total_lic_usd + total_isp_usd + total_cloud_usd,
        'expiring_licenses': expiring_licenses,
        'expiring_domains':  expiring_domains,
        'today': today,
    }
    return render(request, 'core/dashboard.html', ctx)


@login_required
@require_POST
def switch_site(request):
    """AJAX: переключить текущий объект."""
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
