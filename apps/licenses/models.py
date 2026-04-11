from django.db import models
from apps.core.models import Site


class Vendor(models.Model):
    name           = models.CharField('Вендор', max_length=200)
    contact_name   = models.CharField('Контактное лицо', max_length=200, blank=True)
    contact_email  = models.EmailField('Email', blank=True)
    contact_phone  = models.CharField('Телефон', max_length=50, blank=True)
    telegram       = models.CharField('Telegram', max_length=100, blank=True)
    country        = models.CharField('Страна', max_length=100, blank=True)
    support_terms  = models.CharField('Условия поддержки', max_length=200, blank=True)
    notes          = models.TextField('Примечания', blank=True)

    class Meta:
        verbose_name = 'Вендор'
        verbose_name_plural = 'Вендоры'
        ordering = ['name']

    def __str__(self):
        return self.name


class BusinessApp(models.Model):
    CATEGORY_ERP    = 'erp'
    CATEGORY_HR     = 'hr'
    CATEGORY_BI     = 'bi'
    CATEGORY_MINING = 'mining'
    CATEGORY_CAD    = 'cad'
    CATEGORY_OFFICE = 'office'
    CATEGORY_SEC    = 'security'
    CATEGORY_LEGAL  = 'legal'
    CATEGORY_OTHER  = 'other'
    CATEGORY_CHOICES = [
        (CATEGORY_ERP,    'ERP / Бухгалтерия'),
        (CATEGORY_HR,     'HR / Зарплата'),
        (CATEGORY_BI,     'BI / Аналитика'),
        (CATEGORY_MINING, 'Горное ПО'),
        (CATEGORY_CAD,    'САПР'),
        (CATEGORY_OFFICE, 'Офисный пакет'),
        (CATEGORY_SEC,    'Безопасность'),
        (CATEGORY_LEGAL,  'Правовая база'),
        (CATEGORY_OTHER,  'Другое'),
    ]

    name        = models.CharField('Название БП', max_length=200)
    vendor      = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, blank=True,
                                    verbose_name='Вендор', related_name='apps')
    category    = models.CharField('Категория', max_length=20, choices=CATEGORY_CHOICES, default=CATEGORY_OTHER)
    description = models.TextField('Описание', blank=True)
    sites       = models.ManyToManyField(Site, verbose_name='Объекты', blank=True)
    is_active   = models.BooleanField('Активно', default=True)

    class Meta:
        verbose_name = 'Бизнес-приложение'
        verbose_name_plural = 'Бизнес-приложения'
        ordering = ['name']

    def __str__(self):
        return self.name


class License(models.Model):
    TYPE_NAMED       = 'named'
    TYPE_CONCURRENT  = 'concurrent'
    TYPE_SUBSCRIPTION = 'subscription'
    TYPE_CORPORATE   = 'corporate'
    TYPE_OEM         = 'oem'
    TYPE_CHOICES = [
        (TYPE_NAMED,       'Именная'),
        (TYPE_CONCURRENT,  'Конкурентная'),
        (TYPE_SUBSCRIPTION,'Подписка'),
        (TYPE_CORPORATE,   'Корпоративная'),
        (TYPE_OEM,         'OEM'),
    ]

    STATUS_ACTIVE  = 'active'
    STATUS_EXPIRED = 'expired'
    STATUS_CHOICES = [
        (STATUS_ACTIVE,  'Активна'),
        (STATUS_EXPIRED, 'Истекла'),
    ]

    app             = models.ForeignKey(BusinessApp, on_delete=models.CASCADE,
                                        verbose_name='Приложение', related_name='licenses')
    site            = models.ForeignKey(Site, on_delete=models.CASCADE,
                                        verbose_name='Объект', related_name='licenses')
    license_type    = models.CharField('Тип лицензии', max_length=20, choices=TYPE_CHOICES)
    license_type_custom = models.CharField('Тип (свой)', max_length=100, blank=True)
    quantity_total  = models.PositiveIntegerField('Куплено (шт.)', null=True, blank=True)
    quantity_used   = models.PositiveIntegerField('Используется (шт.)', null=True, blank=True)
    price_per_unit  = models.DecimalField('Цена / лиц. (USD)', max_digits=12, decimal_places=2,
                                          null=True, blank=True)
    contract_number = models.CharField('№ договора', max_length=100, blank=True)
    purchase_date   = models.DateField('Дата покупки', null=True, blank=True)
    expiry_date     = models.DateField('Дата истечения', null=True, blank=True)
    contract_file   = models.FileField('Файл договора', upload_to='contracts/licenses/', blank=True)
    notes           = models.TextField('Примечания', blank=True)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Лицензия'
        verbose_name_plural = 'Лицензии'
        ordering = ['app__name', 'license_type']

    def __str__(self):
        return f'{self.app.name} — {self.get_license_type_display()} [{self.site.name}]'

    @property
    def quantity_free(self):
        if self.quantity_total is not None and self.quantity_used is not None:
            return self.quantity_total - self.quantity_used
        return None

    @property
    def total_cost(self):
        if self.price_per_unit and self.quantity_total:
            return self.price_per_unit * self.quantity_total
        return None

    @property
    def days_until_expiry(self):
        if not self.expiry_date:
            return None
        from django.utils import timezone
        delta = self.expiry_date - timezone.now().date()
        return delta.days

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
