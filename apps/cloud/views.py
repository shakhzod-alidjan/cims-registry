from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import CloudServer, CloudProvider
from collections import defaultdict


def _sf(request):
    site = getattr(request, 'current_site', None)
    if site:
        return {'site': site}
    return {'site_id__in': [s.id for s in request.user.get_accessible_sites()]}


@login_required
def cloud_list(request):
    sf = _sf(request)
    servers = CloudServer.objects.filter(**sf).select_related(
        'site', 'provider'
    ).order_by('provider__name', 'name')

    # Group by provider — clean list for template
    prov_map = defaultdict(list)
    for s in servers:
        prov_map[s.provider_id].append(s)

    prov_groups = []
    total_monthly = 0
    total_annual  = 0

    for prov_id, prov_servers in prov_map.items():
        prov = prov_servers[0].provider
        pg_monthly = sum(
            (s.cost_usd or 0) for s in prov_servers if s.billing_period == 'monthly'
        )
        pg_annual = sum(
            (s.cost_usd or 0) for s in prov_servers if s.billing_period == 'yearly'
        )
        pg_total_monthly = pg_monthly
        pg_total_annual  = pg_monthly * 12 + pg_annual
        total_monthly += pg_monthly
        total_annual  += pg_total_annual
        prov_groups.append({
            'prov_id':      prov_id or 0,
            'prov_name':    prov.name if prov else 'Без провайдера',
            'servers':      prov_servers,
            'total_monthly': pg_total_monthly,
            'total_annual':  pg_total_annual,
        })

    ctx = {
        'prov_groups':   prov_groups,
        'servers':       servers,
        'total':         servers.count(),
        'total_monthly': total_monthly,
        'total_annual':  total_annual,
    }
    return render(request, 'cloud/list.html', ctx)


@login_required
def server_add(request):
    if not request.user.is_editor:
        messages.error(request, 'Нет прав')
        return redirect('cloud_list')
    if request.method == 'POST':
        from .forms import CloudServerForm
        form = CloudServerForm(request.POST, user=request.user)
        if form.is_valid():
            obj = form.save()
            messages.success(request, f'Сервер «{obj.name}» добавлен')
            return redirect('cloud_list')
    else:
        from .forms import CloudServerForm
        form = CloudServerForm(user=request.user)
    return render(request, 'cloud/form.html', {'form': form, 'title': 'Добавить сервер'})


@login_required
def server_edit(request, pk):
    obj = get_object_or_404(CloudServer, pk=pk)
    if not request.user.is_editor:
        messages.error(request, 'Нет прав')
        return redirect('cloud_list')
    if request.method == 'POST':
        from .forms import CloudServerForm
        form = CloudServerForm(request.POST, instance=obj, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Сервер обновлён')
            return redirect('cloud_list')
    else:
        from .forms import CloudServerForm
        form = CloudServerForm(instance=obj, user=request.user)
    return render(request, 'cloud/form.html', {'form': form, 'title': 'Редактировать сервер', 'object': obj})


@login_required
@require_POST
def server_delete(request, pk):
    if not request.user.is_admin:
        messages.error(request, 'Нет прав')
        return redirect('cloud_list')
    get_object_or_404(CloudServer, pk=pk).delete()
    messages.success(request, 'Сервер удалён')
    return redirect('cloud_list')
