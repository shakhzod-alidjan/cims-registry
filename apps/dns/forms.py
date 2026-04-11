from django import forms
from .models import Domain, DomainPayment
from apps.core.models import Site


class DomainForm(forms.ModelForm):
    class Meta:
        model  = Domain
        fields = ('site', 'registrar', 'name', 'registration_date',
                  'expiry_date', 'cost_usd', 'auto_renewal', 'notes')
        widgets = {
            'registration_date': forms.DateInput(attrs={'type': 'date'}),
            'expiry_date':       forms.DateInput(attrs={'type': 'date'}),
            'notes':             forms.Textarea(attrs={'rows': 3}),
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


class DomainPaymentForm(forms.ModelForm):
    class Meta:
        model  = DomainPayment
        fields = ('paid_date', 'amount_usd', 'paid_by', 'notes')
        widgets = {
            'paid_date': forms.DateInput(attrs={'type': 'date'}),
            'notes':     forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            f.widget.attrs.setdefault('class', 'form-control')
