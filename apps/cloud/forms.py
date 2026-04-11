from django import forms
from .models import CloudServer
from apps.core.models import Site


class CloudServerForm(forms.ModelForm):
    class Meta:
        model  = CloudServer
        fields = ('site', 'provider', 'server_type', 'name', 'cpu', 'ram_gb',
                  'disk_gb', 'disk_type', 'os', 'ip_address', 'purpose',
                  'status', 'cost_usd', 'billing_period', 'next_payment', 'notes')
        widgets = {
            'next_payment': forms.DateInput(attrs={'type': 'date'}),
            'notes':        forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user and not user.is_admin:
            self.fields['site'].queryset = user.get_accessible_sites()
        else:
            self.fields['site'].queryset = Site.objects.filter(is_active=True)
        for f in self.fields.values():
            if not isinstance(f.widget, (forms.CheckboxInput,)):
                f.widget.attrs.setdefault('class', 'form-control')
