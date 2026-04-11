from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import ISPContract, ISPOperator


def _sf(request):
    site = getattr(request, 'current_site', None)
    if site:
        return {'site': site}
    return {'site_id__in': [s.id for s in request.user.get_accessible_sites()]}


@login_required
def isp_list(request):
    sf = _sf(request)
    contracts = ISPContract.objects.filter(**sf).select_related('site', 'operator').order_by('operator__name', 'service_name')

    # Group by operator — build clean list for template
    op_map = defaultdict(list)
    for c in contracts:
        op_map[c.operator_id].append(c)

    operators_list = []
    total_monthly_uzs = 0
    expired_count = 0

    for op_id, op_contracts in op_map.items():
        op = op_contracts[0].operator
        op_total = sum(c.cost_uzs or 0 for c in op_contracts)
        has_expired = any(c.status == 'expired' for c in op_contracts)
        site_names = ', '.join(sorted(set(c.site.name for c in op_contracts)))
        total_monthly_uzs += op_total
        expired_count += sum(1 for c in op_contracts if c.status == 'expired')
        operators_list.append({
            'id': op_id or 0,
            'name': op.name if op else 'Без оператора',
            'contracts': op_contracts,
            'total_uzs': op_total,
            'has_expired': has_expired,
            'site_names': site_names,
        })

    # Also handle contracts without operator
    no_op = [c for c in contracts if c.operator_id is None]
    if no_op:
        operators_list.append({
            'id': 0,
            'name': 'Без оператора',
            'contracts': no_op,
            'total_uzs': sum(c.cost_uzs or 0 for c in no_op),
            'has_expired': any(c.status == 'expired' for c in no_op),
            'site_names': ', '.join(sorted(set(c.site.name for c in no_op))),
        })

    ctx = {
        'operators_list': operators_list,
        'all_contracts': contracts,
        'total': contracts.count(),
        'expired': expired_count,
        'total_monthly_uzs': total_monthly_uzs,
        'total_annual_uzs': total_monthly_uzs * 12,
    }
    return render(request, 'internet/list.html', ctx)


@login_required
def isp_add(request):
    if not request.user.is_editor:
        messages.error(request, 'Нет прав')
        return redirect('isp_list')
    if request.method == 'POST':
        from .forms import ISPContractForm
        form = ISPContractForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            obj = form.save()
            messages.success(request, f'Договор «{obj.service_name}» добавлен')
            return redirect('isp_list')
    else:
        from .forms import ISPContractForm
        form = ISPContractForm(user=request.user)
    return render(request, 'internet/form.html', {'form': form, 'title': 'Добавить договор'})


@login_required
def isp_edit(request, pk):
    obj = get_object_or_404(ISPContract, pk=pk)
    if not request.user.is_editor:
        messages.error(request, 'Нет прав')
        return redirect('isp_list')
    if request.method == 'POST':
        from .forms import ISPContractForm
        form = ISPContractForm(request.POST, request.FILES, instance=obj, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Договор обновлён')
            return redirect('isp_list')
    else:
        from .forms import ISPContractForm
        form = ISPContractForm(instance=obj, user=request.user)
    return render(request, 'internet/form.html', {'form': form, 'title': 'Редактировать договор', 'object': obj})


@login_required
@require_POST
def isp_delete(request, pk):
    if not request.user.is_admin:
        messages.error(request, 'Нет прав')
        return redirect('isp_list')
    get_object_or_404(ISPContract, pk=pk).delete()
    messages.success(request, 'Договор удалён')
    return redirect('isp_list')
