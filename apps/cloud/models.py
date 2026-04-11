from django.db import models
from apps.core.models import Site

CURRENCY_CHOICES = [('USD','USD'),('UZS','UZS'),('EUR','EUR'),('RUB','RUB')]

class CloudProvider(models.Model):
    name          = models.CharField('Провайдер', max_length=200)
    contact_email = models.EmailField('Email', blank=True)
    billing_url   = models.URLField('Биллинг URL', blank=True)
    notes         = models.TextField('Примечания', blank=True)

    class Meta:
        verbose_name = 'Cloud-провайдер'
        verbose_name_plural = 'Cloud-провайдеры'
        ordering = ['name']

    def __str__(self):
        return self.name


class CloudServer(models.Model):
    TYPE_CHOICES = [
        ('vps','VPS'),('dedicated','Dedicated'),('managed_db','Managed Database'),
        ('s3','Object Storage (S3)'),('function','Serverless / Function'),('other','Другое'),
    ]
    STATUS_CHOICES = [('active','Активен'),('stopped','Остановлен')]

    site           = models.ForeignKey(Site, on_delete=models.CASCADE,
                                       verbose_name='Объект', related_name='cloud_servers')
    provider       = models.ForeignKey(CloudProvider, on_delete=models.SET_NULL, null=True,
                                       verbose_name='Провайдер', related_name='servers')
    server_type    = models.CharField('Тип', max_length=20, choices=TYPE_CHOICES, default='vps')
    name           = models.CharField('Имя сервера', max_length=200)
    cpu            = models.CharField('CPU', max_length=50, blank=True)
    ram_gb         = models.PositiveSmallIntegerField('RAM (GB)', null=True, blank=True)
    disk_gb        = models.PositiveIntegerField('Диск (GB)', null=True, blank=True)
    disk_type      = models.CharField('Тип диска', max_length=10,
                                      choices=[('ssd','SSD'),('hdd','HDD'),('nvme','NVMe')], default='ssd')
    os             = models.CharField('ОС', max_length=100, blank=True)
    ip_address     = models.GenericIPAddressField('IP адрес', null=True, blank=True)
    purpose        = models.CharField('Назначение', max_length=300, blank=True)
    status         = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='active')

    # Мультивалютность
    cost           = models.DecimalField('Стоимость / мес', max_digits=14, decimal_places=2,
                                         null=True, blank=True)
    currency       = models.CharField('Валюта', max_length=3, choices=CURRENCY_CHOICES, default='USD')
    # legacy
    cost_usd       = models.DecimalField('Стоимость / мес (USD)', max_digits=10, decimal_places=2,
                                         null=True, blank=True)

    billing_period = models.CharField('Период оплаты', max_length=20,
                                      choices=[('monthly','Ежемесячно'),('yearly','Ежегодно')],
                                      default='monthly')
    next_payment   = models.DateField('Следующий платёж', null=True, blank=True)
    notes          = models.TextField('Примечания', blank=True)
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Cloud-сервер'
        verbose_name_plural = 'Cloud-серверы'
        ordering = ['provider__name', 'name']

    def __str__(self):
        return f'{self.name} ({self.provider}) [{self.site.name}]'

    def get_cost_usd_monthly(self, usd_rate=12800):
        from decimal import Decimal
        val = self.cost or self.cost_usd
        if not val:
            return Decimal('0')
        rate = Decimal(str(usd_rate))
        cur = self.currency if self.cost else 'USD'
        if cur == 'USD':
            return val
        elif cur == 'UZS':
            return val / rate
        elif cur == 'EUR':
            return val * Decimal('1.08')
        return val

    @property
    def spec(self):
        parts = []
        if self.cpu:   parts.append(self.cpu)
        if self.ram_gb: parts.append(f'{self.ram_gb} GB RAM')
        if self.disk_gb: parts.append(f'{self.disk_gb} GB {self.disk_type.upper()}')
        return ' / '.join(parts) if parts else '—'
