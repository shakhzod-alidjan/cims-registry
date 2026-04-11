from django import forms
from .models import License, BusinessApp
from apps.core.models import Site


class LicenseForm(forms.ModelForm):
    class Meta:
        model  = License
        fields = ('app', 'site', 'license_type', 'license_type_custom',
                  'quantity_total', 'quantity_used', 'price_per_unit',
                  'contract_number', 'purchase_date', 'expiry_date',
                  'contract_file', 'notes')
        widgets = {
            'purchase_date': forms.DateInput(attrs={'type': 'date'}),
            'expiry_date':   forms.DateInput(attrs={'type': 'date'}),
            'notes':         forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user and not user.is_admin:
            self.fields['site'].queryset = user.get_accessible_sites()
        else:
            self.fields['site'].queryset = Site.objects.filter(is_active=True)

        for field in self.fields.values():
            if not isinstance(field.widget, (forms.CheckboxInput, forms.FileInput)):
                field.widget.attrs.setdefault('class', 'form-control')
