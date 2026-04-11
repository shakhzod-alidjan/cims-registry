from apps.core.models import Site


def global_context(request):
    """Глобальный контекст для всех шаблонов."""
    ctx = {
        'current_site': None,
        'all_sites': [],
        'expiring_count': 0,
    }

    if not request.user.is_authenticated:
        return ctx

    ctx['all_sites'] = list(request.user.get_accessible_sites())
    ctx['current_site'] = getattr(request, 'current_site', None)

    # Badge count — истекают в течение 30 дней
    from django.utils import timezone
    from apps.licenses.models import License
    from apps.dns.models import Domain
    from apps.internet.models import ISPContract

    deadline = timezone.now().date() + timezone.timedelta(days=30)
    qs_filter = {}
    if ctx['current_site']:
        site_id = ctx['current_site'].id
        lic_count = License.objects.filter(
            site_id=site_id,
            expiry_date__isnull=False,
            expiry_date__lte=deadline,
        ).count()
        dom_count = Domain.objects.filter(
            site_id=site_id,
            expiry_date__isnull=False,
            expiry_date__lte=deadline,
        ).count()
        isp_count = ISPContract.objects.filter(
            site_id=site_id,
            end_date__isnull=False,
            end_date__lte=deadline,
        ).count()
    else:
        accessible_ids = [s.id for s in ctx['all_sites']]
        lic_count = License.objects.filter(
            site_id__in=accessible_ids,
            expiry_date__isnull=False,
            expiry_date__lte=deadline,
        ).count()
        dom_count = Domain.objects.filter(
            site_id__in=accessible_ids,
            expiry_date__isnull=False,
            expiry_date__lte=deadline,
        ).count()
        isp_count = ISPContract.objects.filter(
            site_id__in=accessible_ids,
            end_date__isnull=False,
            end_date__lte=deadline,
        ).count()

    ctx['expiring_count'] = lic_count + dom_count + isp_count
    return ctx
