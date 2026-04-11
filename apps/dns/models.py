from django.db import models
from apps.core.models import Site


class Registrar(models.Model):
    name          = models.CharField('Регистратор', max_length=200)
    url           = models.URLField('Сайт', blank=True)
    contact_name  = models.CharField('Контакт', max_length=200, blank=True)
    contact_email = models.EmailField('Email', blank=True)

    class Meta:
        verbose_name = 'Регистратор'
        verbose_name_plural = 'Регистраторы'
        ordering = ['name']

    def __str__(self):
        return self.name


class Domain(models.Model):
    site            = models.ForeignKey(Site, on_delete=models.CASCADE,
                                        verbose_name='Объект', related_name='domains')
    registrar       = models.ForeignKey(Registrar, on_delete=models.SET_NULL, null=True,
                                        verbose_name='Регистратор', related_name='domains')
    name            = models.CharField('Домен', max_length=255, unique=True)
    registration_date = models.DateField('Дата регистрации', null=True, blank=True)
    expiry_date     = models.DateField('Дата истечения', null=True, blank=True)
    cost_usd        = models.DecimalField('Стоимость / год (USD)', max_digits=8, decimal_places=2,
                                          null=True, blank=True)
    auto_renewal    = models.BooleanField('Авто-продление', default=False)
    notes           = models.TextField('Примечания', blank=True)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Домен'
        verbose_name_plural = 'Домены'
        ordering = ['site__name', 'name']

    def __str__(self):
        return f'{self.name} [{self.site.name}]'

    @property
    def days_until_expiry(self):
        if not self.expiry_date:
            return None
        from django.utils import timezone
        return (self.expiry_date - timezone.now().date()).days

    @property
    def status(self):
        days = self.days_until_expiry
        if days is None:
            return 'active'
        if days <= 0:
            return 'expired'
        if days <= 30:
            return 'expiring_soon'
        if days <= 90:
            return 'expiring'
        return 'active'


class DomainPayment(models.Model):
    """История платежей за домен"""
    domain      = models.ForeignKey(Domain, on_delete=models.CASCADE,
                                    verbose_name='Домен', related_name='payments')
    paid_date   = models.DateField('Дата оплаты')
    amount_usd  = models.DecimalField('Сумма (USD)', max_digits=8, decimal_places=2)
    paid_by     = models.CharField('Кто оплатил', max_length=200, blank=True)
    notes       = models.TextField('Примечания', blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Платёж за домен'
        verbose_name_plural = 'Платежи за домены'
        ordering = ['-paid_date']

    def __str__(self):
        return f'{self.domain.name} — {self.paid_date} — ${self.amount_usd}'
