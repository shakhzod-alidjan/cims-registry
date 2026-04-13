from django.db import models
from apps.core.models import Site

CURRENCY_CHOICES = [('USD','USD'),('UZS','UZS'),('EUR','EUR'),('RUB','RUB')]


class ServiceType(models.Model):
    """Тип услуги связи — добавляется через Admin"""
    name     = models.CharField('Название', max_length=200, unique=True)
    ordering = models.PositiveSmallIntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Тип услуги'
        verbose_name_plural = 'Типы услуг'
        ordering = ['ordering', 'name']

    def __str__(self):
        return self.name


class ISPOperator(models.Model):
    name          = models.CharField('Оператор', max_length=200)
    contact_name  = models.CharField('Контакт', max_length=200, blank=True)
    contact_email = models.EmailField('Email', blank=True)
    contact_phone = models.CharField('Телефон', max_length=50, blank=True)
    country       = models.CharField('Страна', max_length=100, blank=True)

    class Meta:
        verbose_name = 'Оператор связи'
        verbose_name_plural = 'Операторы связи'
        ordering = ['name']

    def __str__(self):
        return self.name


class ISPContract(models.Model):
    site            = models.ForeignKey(Site, on_delete=models.CASCADE,
                                        verbose_name='Объект', related_name='isp_contracts')
    operator        = models.ForeignKey(ISPOperator, on_delete=models.SET_NULL, null=True,
                                        verbose_name='Оператор', related_name='contracts')
    service_type    = models.ForeignKey(ServiceType, on_delete=models.SET_NULL, null=True, blank=True,
                                        verbose_name='Тип услуги', related_name='contracts')
    service_name    = models.CharField('Название услуги', max_length=200)
    tariff          = models.CharField('Тариф / описание', max_length=200, blank=True)
    location        = models.CharField('Локация', max_length=200, blank=True)
    speed           = models.CharField('Скорость / объём', max_length=100, blank=True)
    ip_address      = models.GenericIPAddressField('IP адрес', null=True, blank=True)
    contract_number = models.CharField('№ договора', max_length=100, blank=True)
    contract_file   = models.FileField('Файл договора', upload_to='contracts/isp/', blank=True)
    start_date      = models.DateField('Дата начала', null=True, blank=True)
    end_date        = models.DateField('Дата окончания', null=True, blank=True)
    auto_renewal    = models.BooleanField('Авто-продление', default=False)

    cost            = models.DecimalField('Стоимость / мес', max_digits=14, decimal_places=2,
                                          null=True, blank=True)
    currency        = models.CharField('Валюта', max_length=3, choices=CURRENCY_CHOICES, default='UZS')
    cost_uzs        = models.DecimalField('Стоимость / мес (UZS)', max_digits=14, decimal_places=0,
                                          null=True, blank=True)
    cost_usd        = models.DecimalField('Стоимость / мес (USD)', max_digits=10, decimal_places=2,
                                          null=True, blank=True)

    payment_method  = models.CharField('Способ оплаты', max_length=100, blank=True)
    next_payment    = models.DateField('Дата след. оплаты', null=True, blank=True)
    notes           = models.TextField('Примечания', blank=True)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Договор ISP'
        verbose_name_plural = 'Договоры ISP'
        ordering = ['site__name', 'operator__name']

    def __str__(self):
        return f'{self.service_name} — {self.operator} [{self.site.name}]'

    def get_cost_usd_monthly(self, usd_rate=12800):
        from decimal import Decimal
        val = self.cost or self.cost_usd or self.cost_uzs or Decimal('0')
        if not val:
            return Decimal('0')
        rate = Decimal(str(usd_rate))
        if self.cost:
            cur = self.currency
        elif self.cost_usd:
            cur = 'USD'
        elif self.cost_uzs:
            cur = 'UZS'
        else:
            cur = 'UZS'
        if cur == 'USD':
            return val
        elif cur == 'UZS':
            return val / rate
        elif cur == 'EUR':
            return val * Decimal('1.08')
        return val

    @property
    def days_until_expiry(self):
        if not self.end_date:
            return None
        from django.utils import timezone
        return (self.end_date - timezone.now().date()).days

    @property
    def status(self):
        days = self.days_until_expiry
        if days is None:
            return 'active'
        if days <= 0:
            return 'expired'
        if days <= 30:
            return 'expiring_soon'
        return 'active'
