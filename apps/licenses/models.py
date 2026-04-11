from django.db import models
from apps.core.models import Site

CURRENCY_CHOICES = [('USD','USD'),('UZS','UZS'),('EUR','EUR'),('RUB','RUB')]

class Vendor(models.Model):
    name          = models.CharField('Вендор', max_length=200)
    contact_name  = models.CharField('Контакт', max_length=200, blank=True)
    contact_email = models.EmailField('Email', blank=True)
    contact_phone = models.CharField('Телефон', max_length=50, blank=True)
    telegram      = models.CharField('Telegram', max_length=100, blank=True)
    country       = models.CharField('Страна', max_length=100, blank=True)
    support_terms = models.CharField('Условия поддержки', max_length=200, blank=True)
    notes         = models.TextField('Примечания', blank=True)

    class Meta:
        verbose_name = 'Вендор'
        verbose_name_plural = 'Вендоры'
        ordering = ['name']

    def __str__(self):
        return self.name


class BusinessApp(models.Model):
    CATEGORY_CHOICES = [
        ('erp','ERP / Бухгалтерия'),('hr','HR / Зарплата'),('bi','BI / Аналитика'),
        ('mining','Горное ПО'),('cad','САПР'),('office','Офисный пакет'),
        ('security','Безопасность'),('legal','Правовая база'),('other','Другое'),
    ]
    name        = models.CharField('Название БП', max_length=200)
    vendor      = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, blank=True,
                                    verbose_name='Вендор', related_name='apps')
    category    = models.CharField('Категория', max_length=20, choices=CATEGORY_CHOICES, default='other')
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
    TYPE_CHOICES = [
        ('named','Именная'),('concurrent','Конкурентная'),
        ('subscription','Подписка'),('corporate','Корпоративная'),('oem','OEM'),
    ]

    app              = models.ForeignKey(BusinessApp, on_delete=models.CASCADE,
                                         verbose_name='Приложение', related_name='licenses')
    site             = models.ForeignKey(Site, on_delete=models.CASCADE,
                                         verbose_name='Объект', related_name='licenses')
    license_type     = models.CharField('Тип лицензии', max_length=20, choices=TYPE_CHOICES)
    license_type_custom = models.CharField('Тип (свой)', max_length=100, blank=True)
    quantity_total   = models.PositiveIntegerField('Куплено (шт.)', null=True, blank=True)
    quantity_used    = models.PositiveIntegerField('Используется (шт.)', null=True, blank=True)

    # Мультивалютность
    price_per_unit   = models.DecimalField('Цена за ед.', max_digits=14, decimal_places=2,
                                            null=True, blank=True)
    currency         = models.CharField('Валюта', max_length=3, choices=CURRENCY_CHOICES, default='USD')

    contract_number  = models.CharField('№ договора', max_length=100, blank=True)
    purchase_date    = models.DateField('Дата покупки', null=True, blank=True)
    expiry_date      = models.DateField('Дата истечения', null=True, blank=True)
    contract_file    = models.FileField('Файл договора', upload_to='contracts/licenses/', blank=True)
    notes            = models.TextField('Примечания', blank=True)
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Лицензия'
        verbose_name_plural = 'Лицензии'
        ordering = ['app__name']

    def __str__(self):
        return f'{self.app.name} [{self.site.name}]'

    def get_price_usd(self, usd_rate=12800):
        """Вернуть цену за единицу в USD."""
        if not self.price_per_unit:
            return None
        from decimal import Decimal
        rate = Decimal(str(usd_rate))
        if self.currency == 'USD':
            return self.price_per_unit
        elif self.currency == 'UZS':
            return self.price_per_unit / rate
        elif self.currency == 'EUR':
            return self.price_per_unit * Decimal('1.08')
        elif self.currency == 'RUB':
            return self.price_per_unit / Decimal('90')
        return self.price_per_unit

    @property
    def total_cost(self):
        if self.price_per_unit and self.quantity_total:
            return self.price_per_unit * self.quantity_total
        return None

    @property
    def quantity_free(self):
        if self.quantity_total is not None and self.quantity_used is not None:
            return self.quantity_total - self.quantity_used
        return None

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
