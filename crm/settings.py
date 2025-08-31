INSTALLED_APPS = [
    # ... default Django apps
    "django_crontab",
    "graphene_django",
    "crm",  # your app
]
CRONJOBS = [
    ('0 */12 * * *', 'crm.cron.update_low_stock'),
]
