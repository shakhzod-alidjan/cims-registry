from celery import shared_task
from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail
import requests
import logging

logger = logging.getLogger(__name__)

DAYS_WARNING = 30  # notify when ≤ 30 days left


def send_telegram(message: str, chat_id: str = None) -> bool:
    token = settings.TELEGRAM_BOT_TOKEN
    cid = chat_id or settings.TELEGRAM_CHAT_ID
    if not token or not cid:
        logger.warning('Telegram не настроен — пропускаем уведомление')
        return False
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    try:
        resp = requests.post(url, json={'chat_id': cid, 'text': message, 'parse_mode': 'HTML'}, timeout=10)
        return resp.ok
    except Exception as e:
        logger.error(f'Telegram send error: {e}')
        return False


def _notify(subject: str, body: str, emails: list[str], telegram_msg: str = None):
    """Отправить email + Telegram уведомление."""
    # Email
    if emails:
        try:
            send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, emails, fail_silently=False)
        except Exception as e:
            logger.error(f'Email send error: {e}')
    # Telegram
    if telegram_msg:
        send_telegram(telegram_msg)


@shared_task(bind=True, queue='notifications')
def check_expiring_licenses(self):
    """Проверяет лицензии у которых ≤ 30 дней до истечения."""
    from apps.licenses.models import License
    today = timezone.now().date()
    expiring = License.objects.filter(
        expiry_date__isnull=False,
        expiry_date__lte=today + timezone.timedelta(days=DAYS_WARNING),
        expiry_date__gte=today,
    ).select_related('app', 'site', 'app__vendor')

    if not expiring.exists():
        return 'No expiring licenses'

    lines = []
    for lic in expiring:
        days = (lic.expiry_date - today).days
        lines.append(
            f'  • {lic.app.name} [{lic.get_license_type_display()}] — '
            f'объект {lic.site.name} — истекает через {days} дн. ({lic.expiry_date})'
        )

    subject = f'⚠️ IT Registry: {expiring.count()} лицензий истекают в ближайшие {DAYS_WARNING} дней'
    body = f'Требуют продления:\n\n' + '\n'.join(lines) + f'\n\nОткрыть: {settings.SITE_URL}/licenses/'
    tg_msg = (
        f'⚠️ <b>IT Registry — Лицензии</b>\n'
        f'Истекают в ближайшие {DAYS_WARNING} дней:\n\n'
        + '\n'.join(lines)
        + f'\n\n<a href="{settings.SITE_URL}/licenses/">Открыть реестр</a>'
    )

    emails = [settings.ADMIN_EMAIL] if settings.ADMIN_EMAIL else []
    _notify(subject, body, emails, tg_msg)
    return f'Notified: {expiring.count()} licenses'


@shared_task(bind=True, queue='notifications')
def check_expiring_domains(self):
    """Проверяет домены у которых ≤ 30 дней до истечения."""
    from apps.dns.models import Domain
    today = timezone.now().date()
    expiring = Domain.objects.filter(
        expiry_date__isnull=False,
        expiry_date__lte=today + timezone.timedelta(days=DAYS_WARNING),
        expiry_date__gte=today,
    ).select_related('site', 'registrar')

    if not expiring.exists():
        return 'No expiring domains'

    lines = []
    for d in expiring:
        days = (d.expiry_date - today).days
        lines.append(f'  • {d.name} [{d.site.name}] — {days} дн. ({d.expiry_date})')

    subject = f'⚠️ IT Registry: {expiring.count()} доменов истекают в ближайшие {DAYS_WARNING} дней'
    body    = 'Требуют продления:\n\n' + '\n'.join(lines) + f'\n\n{settings.SITE_URL}/dns/'
    tg_msg  = (
        f'🌐 <b>IT Registry — Домены</b>\n'
        f'Истекают в ближайшие {DAYS_WARNING} дней:\n\n'
        + '\n'.join(lines)
    )

    emails = [settings.ADMIN_EMAIL] if settings.ADMIN_EMAIL else []
    _notify(subject, body, emails, tg_msg)
    return f'Notified: {expiring.count()} domains'


@shared_task(bind=True, queue='notifications')
def check_expiring_isp_contracts(self):
    """Проверяет договоры ISP у которых ≤ 30 дней до истечения."""
    from apps.internet.models import ISPContract
    today = timezone.now().date()
    expiring = ISPContract.objects.filter(
        end_date__isnull=False,
        end_date__lte=today + timezone.timedelta(days=DAYS_WARNING),
        end_date__gte=today,
    ).select_related('site', 'operator')

    if not expiring.exists():
        return 'No expiring ISP contracts'

    lines = []
    for c in expiring:
        days = (c.end_date - today).days
        lines.append(f'  • {c.service_name} / {c.operator} [{c.site.name}] — {days} дн. ({c.end_date})')

    subject = f'⚠️ IT Registry: {expiring.count()} договоров ISP истекают'
    body    = 'Требуют продления:\n\n' + '\n'.join(lines) + f'\n\n{settings.SITE_URL}/internet/'
    tg_msg  = f'📡 <b>IT Registry — Интернет</b>\nИстекают:\n\n' + '\n'.join(lines)

    emails = [settings.ADMIN_EMAIL] if settings.ADMIN_EMAIL else []
    _notify(subject, body, emails, tg_msg)
    return f'Notified: {expiring.count()} ISP contracts'


@shared_task(bind=True, queue='notifications')
def send_weekly_summary(self):
    """Еженедельный сводный отчёт каждый понедельник."""
    from apps.licenses.models import License
    from apps.dns.models import Domain
    from apps.internet.models import ISPContract
    today = timezone.now().date()
    deadline = today + timezone.timedelta(days=90)

    exp_lic = License.objects.filter(expiry_date__isnull=False, expiry_date__lte=deadline).count()
    exp_dom = Domain.objects.filter(expiry_date__isnull=False, expiry_date__lte=deadline).count()
    exp_isp = ISPContract.objects.filter(end_date__isnull=False, end_date__lte=deadline).count()

    subject = f'📊 IT Registry — Еженедельный отчёт ({today})'
    body = (
        f'Сводка на {today}:\n\n'
        f'Лицензии истекают ≤90 дней:   {exp_lic}\n'
        f'Домены истекают ≤90 дней:      {exp_dom}\n'
        f'Договоры ISP истекают ≤90 дней:{exp_isp}\n\n'
        f'Открыть: {settings.SITE_URL}'
    )
    tg_msg = (
        f'📊 <b>IT Registry — Еженедельный отчёт</b>\n'
        f'📅 {today}\n\n'
        f'⚠️ Лицензий истекает: <b>{exp_lic}</b>\n'
        f'🌐 Доменов истекает: <b>{exp_dom}</b>\n'
        f'📡 Договоров ISP: <b>{exp_isp}</b>\n\n'
        f'<a href="{settings.SITE_URL}">Открыть IT Registry</a>'
    )

    emails = [settings.ADMIN_EMAIL] if settings.ADMIN_EMAIL else []
    _notify(subject, body, emails, tg_msg)
    return 'Weekly summary sent'


@shared_task(bind=True, queue='exports')
def export_licenses_to_excel(self, site_id=None, user_email=None):
    """Асинхронный экспорт лицензий в Excel."""
    import io
    import openpyxl
    from apps.licenses.models import License

    qs = License.objects.select_related('app', 'site', 'app__vendor')
    if site_id:
        qs = qs.filter(site_id=site_id)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Лицензии'
    headers = ['Приложение', 'Объект', 'Тип', 'Вендор', 'Куплено', 'Используется',
               'Цена (USD)', 'Итого (USD)', 'Дата истечения', 'Статус', 'Примечания']
    ws.append(headers)

    for lic in qs:
        ws.append([
            lic.app.name,
            lic.site.name,
            lic.get_license_type_display(),
            str(lic.app.vendor) if lic.app.vendor else '',
            lic.quantity_total,
            lic.quantity_used,
            float(lic.price_per_unit) if lic.price_per_unit else None,
            float(lic.total_cost) if lic.total_cost else None,
            str(lic.expiry_date) if lic.expiry_date else '',
            lic.status,
            lic.notes,
        ])

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)

    if user_email:
        from django.core.mail import EmailMessage
        msg = EmailMessage(
            subject='IT Registry — Экспорт лицензий',
            body='Файл экспорта лицензий во вложении.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user_email],
        )
        msg.attach('licenses_export.xlsx',
                   buf.read(),
                   'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        msg.send()

    return f'Export done: {qs.count()} rows'
