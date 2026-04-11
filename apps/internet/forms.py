from django import forms
from .models import ISPContract
from apps.core.models import Site


class ISPContractForm(forms.ModelForm):
    class Meta:
        model  = ISPContract
        fields = ('site', 'operator', 'service_type', 'service_name', 'tariff',
                  'location', 'speed', 'ip_address', 'contract_number', 'contract_file',
                  'start_date', 'end_date', 'auto_renewal',
                  'cost_uzs', 'cost_usd', 'payment_method', 'next_payment', 'notes')
        widgets = {
            'start_date':   forms.DateInput(attrs={'type': 'date'}),
            'end_date':     forms.DateInput(attrs={'type': 'date'}),
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
            if not isinstance(f.widget, (forms.CheckboxInput, forms.FileInput)):
                f.widget.attrs.setdefault('class', 'form-control')
