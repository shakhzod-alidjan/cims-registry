from django.db import models
from django.contrib.auth.models import AbstractUser


class Site(models.Model):
    """Объект/площадка компании: HQ, MMG, AGG, CityMakon, K-Tungsten..."""
    name        = models.CharField('Название', max_length=100, unique=True)
    code        = models.SlugField('Код', max_length=20, unique=True)
    color       = models.CharField('Цвет (hex)', max_length=7, default='#0052CC')
    description = models.TextField('Описание', blank=True)
    is_active   = models.BooleanField('Активен', default=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Объект'
        verbose_name_plural = 'Объекты'
        ordering = ['name']

    def __str__(self):
        return self.name


class User(AbstractUser):
    ROLE_ADMIN  = 'admin'
    ROLE_EDITOR = 'editor'
    ROLE_VIEWER = 'viewer'
    ROLE_CHOICES = [
        (ROLE_ADMIN,  'Администратор'),
        (ROLE_EDITOR, 'Редактор'),
        (ROLE_VIEWER, 'Просмотр'),
    ]

    role            = models.CharField('Роль', max_length=20, choices=ROLE_CHOICES, default=ROLE_VIEWER)
    sites           = models.ManyToManyField(Site, through='UserSiteRole', blank=True, verbose_name='Объекты')
    telegram_chat_id = models.CharField('Telegram Chat ID', max_length=50, blank=True)
    notify_email    = models.BooleanField('Email уведомления', default=True)
    notify_telegram = models.BooleanField('Telegram уведомления', default=False)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.get_full_name() or self.username} ({self.get_role_display()})'

    @property
    def is_admin(self):
        return self.role == self.ROLE_ADMIN or self.is_superuser

    @property
    def is_editor(self):
        return self.role in (self.ROLE_ADMIN, self.ROLE_EDITOR) or self.is_superuser

    def get_accessible_sites(self):
        if self.is_admin:
            return Site.objects.filter(is_active=True)
        return self.sites.filter(is_active=True)


class UserSiteRole(models.Model):
    """Привязка пользователя к конкретному объекту с ролью"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    role = models.CharField('Роль на объекте', max_length=20,
                            choices=User.ROLE_CHOICES, default=User.ROLE_VIEWER)

    class Meta:
        unique_together = ('user', 'site')
        verbose_name = 'Роль на объекте'
        verbose_name_plural = 'Роли на объектах'

    def __str__(self):
        return f'{self.user} → {self.site} [{self.role}]'
