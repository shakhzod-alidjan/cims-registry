from django.db import models
from apps.core.models import Site


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
    TYPE_VPS        = 'vps'
    TYPE_DEDICATED  = 'dedicated'
    TYPE_MANAGED_DB = 'managed_db'
    TYPE_S3         = 's3'
    TYPE_FUNCTION   = 'function'
    TYPE_OTHER      = 'other'
    TYPE_CHOICES = [
        (TYPE_VPS,        'VPS'),
        (TYPE_DEDICATED,  'Dedicated'),
        (TYPE_MANAGED_DB, 'Managed Database'),
        (TYPE_S3,         'Object Storage (S3)'),
        (TYPE_FUNCTION,   'Serverless / Function'),
        (TYPE_OTHER,      'Другое'),
    ]

    STATUS_ACTIVE  = 'active'
    STATUS_STOPPED = 'stopped'
    STATUS_CHOICES = [
        (STATUS_ACTIVE,  'Активен'),
        (STATUS_STOPPED, 'Остановлен'),
    ]

    site            = models.ForeignKey(Site, on_delete=models.CASCADE,
                                        verbose_name='Объект', related_name='cloud_servers')
    provider        = models.ForeignKey(CloudProvider, on_delete=models.SET_NULL, null=True,
                                        verbose_name='Провайдер', related_name='servers')
    server_type     = models.CharField('Тип', max_length=20, choices=TYPE_CHOICES, default=TYPE_VPS)
    name            = models.CharField('Имя сервера', max_length=200)
    cpu             = models.CharField('CPU', max_length=50, blank=True)
    ram_gb          = models.PositiveSmallIntegerField('RAM (GB)', null=True, blank=True)
    disk_gb         = models.PositiveIntegerField('Диск (GB)', null=True, blank=True)
    disk_type       = models.CharField('Тип диска', max_length=10,
                                       choices=[('ssd','SSD'),('hdd','HDD'),('nvme','NVMe')],
                                       default='ssd')
    os              = models.CharField('ОС', max_length=100, blank=True)
    ip_address      = models.GenericIPAddressField('IP адрес', null=True, blank=True)
    purpose         = models.CharField('Назначение', max_length=300, blank=True)
    status          = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    cost_usd        = models.DecimalField('Стоимость / мес (USD)', max_digits=10, decimal_places=2,
                                          null=True, blank=True)
    billing_period  = models.CharField('Период оплаты', max_length=20,
                                       choices=[('monthly','Ежемесячно'),('yearly','Ежегодно')],
                                       default='monthly')
    next_payment    = models.DateField('Следующий платёж', null=True, blank=True)
    notes           = models.TextField('Примечания', blank=True)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Cloud-сервер'
        verbose_name_plural = 'Cloud-серверы'
        ordering = ['provider__name', 'name']

    def __str__(self):
        return f'{self.name} ({self.provider}) [{self.site.name}]'

    @property
    def spec(self):
        parts = []
        if self.cpu:
            parts.append(self.cpu)
        if self.ram_gb:
            parts.append(f'{self.ram_gb} GB RAM')
        if self.disk_gb:
            parts.append(f'{self.disk_gb} GB {self.disk_type.upper()}')
        return ' / '.join(parts) if parts else '—'

    @property
    def cost_yearly(self):
        if self.cost_usd:
            return self.cost_usd * 12 if self.billing_period == 'monthly' else self.cost_usd
        return None
