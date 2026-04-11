from django.contrib import admin


# Celery task results are managed via django-celery-results
# and Celery Beat schedules via django-celery-beat.
# Both are auto-registered in Django Admin when those apps are in INSTALLED_APPS.
# This file intentionally left minimal.
