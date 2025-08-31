INSTALLED_APPS = [
    # ... default Django apps
    "django_crontab",
    "graphene_django",
    "crm",  # your app
    "django_celery_beat",
]
CRONJOBS = [
    ('0 */12 * * *', 'crm.cron.update_low_stock'),
]

# Celery
CELERY_BROKER_URL = "redis://localhost:6379/0"
CELERY_RESULT_BACKEND = "redis://localhost:6379/0"
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'generate-crm-report': {
        'task': 'crm.tasks.generate_crm_report',
        'schedule': crontab(day_of_week='mon', hour=6, minute=0),  # every Monday at 6 AM
    },
}
