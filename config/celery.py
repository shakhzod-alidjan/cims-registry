import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('it_registry')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# ── Periodic tasks schedule ──────────────────────────────────
app.conf.beat_schedule = {
    # Every day at 09:00 Tashkent time
    'check-expiring-licenses': {
        'task': 'apps.notifications.tasks.check_expiring_licenses',
        'schedule': crontab(hour=9, minute=0),
        'options': {'queue': 'notifications'},
    },
    # Every day at 09:05
    'check-expiring-domains': {
        'task': 'apps.notifications.tasks.check_expiring_domains',
        'schedule': crontab(hour=9, minute=5),
        'options': {'queue': 'notifications'},
    },
    # Every day at 09:10
    'check-expiring-isp-contracts': {
        'task': 'apps.notifications.tasks.check_expiring_isp_contracts',
        'schedule': crontab(hour=9, minute=10),
        'options': {'queue': 'notifications'},
    },
    # Every Monday at 08:00
    'weekly-summary-report': {
        'task': 'apps.notifications.tasks.send_weekly_summary',
        'schedule': crontab(hour=8, minute=0, day_of_week=1),
        'options': {'queue': 'notifications'},
    },
}
