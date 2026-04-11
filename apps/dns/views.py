from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import Domain, DomainPayment, Registrar
from collections import defaultdict


def _sf(request):
    site = getattr(request, 'current_site', None)
    if site:
        return {'site': site}
    return {'site_id__in': [s.id for s in request.user.get_accessible_sites()]}


@login_required
def dns_list(request):
    sf = _sf(request)
    domains = Domain.objects.filter(**sf).select_related(
        'site', 'registrar'
    ).prefetch_related('payments').order_by('site__name', 'name')

    # Annotate each domain with last payment info
    for d in domains:
        last = d.payments.order_by('-paid_date').first()
        d.last_payment_date = last.paid_date if last else None
        d.last_payment_by   = last.paid_by   if last else None

    # Group by site — build clean list for template
    site_map = defaultdict(list)
    for d in domains:
        site_map[d.site_id].append(d)

    site_groups = []
    total_cost = 0
    expiring = 0

    for site_id, site_domains in site_map.items():
        site = site_domains[0].site
        sg_cost = sum(d.cost_usd or 0 for d in site_domains)
        warn = sum(1 for d in site_domains if d.days_until_expiry is not None and d.days_until_expiry <= 30)
        # Get first registrar name for hint
        registrar_name = next((d.registrar.name for d in site_domains if d.registrar), None)
        total_cost += sg_cost
        expiring += warn
        site_groups.append({
            'site_id':       site_id,
            'site_name':     site.name,
            'domains':       site_domains,
            'total_cost':    sg_cost,
            'warn_count':    warn,
            'registrar_name': registrar_name,
        })

    ctx = {
        'site_groups': site_groups,
        'domains':     domains,
        'total':       domains.count(),
        'expiring':    expiring,
        'total_cost':  total_cost,
    }
    return render(request, 'dns/list.html', ctx)


@login_required
def domain_add(request):
    if not request.user.is_editor:
        messages.error(request, 'Нет прав')
        return redirect('dns_list')
    if request.method == 'POST':
        from .forms import DomainForm
        form = DomainForm(request.POST, user=request.user)
        if form.is_valid():
            obj = form.save()
            messages.success(request, f'Домен «{obj.name}» добавлен')
            return redirect('dns_list')
    else:
        from .forms import DomainForm
        form = DomainForm(user=request.user)
    return render(request, 'dns/form.html', {'form': form, 'title': 'Добавить домен'})


@login_required
def domain_edit(request, pk):
    obj = get_object_or_404(Domain, pk=pk)
    if not request.user.is_editor:
        messages.error(request, 'Нет прав')
        return redirect('dns_list')
    if request.method == 'POST':
        from .forms import DomainForm
        form = DomainForm(request.POST, instance=obj, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Домен обновлён')
            return redirect('dns_list')
    else:
        from .forms import DomainForm
        form = DomainForm(instance=obj, user=request.user)
    return render(request, 'dns/form.html', {'form': form, 'title': 'Редактировать домен', 'object': obj})


@login_required
@require_POST
def domain_delete(request, pk):
    if not request.user.is_admin:
        messages.error(request, 'Нет прав')
        return redirect('dns_list')
    get_object_or_404(Domain, pk=pk).delete()
    messages.success(request, 'Домен удалён')
    return redirect('dns_list')


@login_required
def domain_payment(request, pk):
    domain = get_object_or_404(Domain, pk=pk)
    if not request.user.is_editor:
        messages.error(request, 'Нет прав')
        return redirect('dns_list')
    if request.method == 'POST':
        from .forms import DomainPaymentForm
        form = DomainPaymentForm(request.POST)
        if form.is_valid():
            pay = form.save(commit=False)
            pay.domain = domain
            pay.save()
            messages.success(request, f'Платёж за «{domain.name}» записан')
            return redirect('dns_list')
    else:
        from .forms import DomainPaymentForm
        form = DomainPaymentForm()
    return render(request, 'dns/payment_form.html', {'form': form, 'domain': domain})
