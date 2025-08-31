#!/bin/bash

# Path to Django project root (adjust if needed)
PROJECT_DIR="$(dirname "$(dirname "$(realpath "$0")")")"
MANAGE_PY="$PROJECT_DIR/manage.py"

# Log file
LOG_FILE="/tmp/customer_cleanup_log.txt"

# Run Django shell command to delete inactive customers
DELETED_COUNT=$(python3 $MANAGE_PY shell -c "
from django.utils import timezone
from datetime import timedelta
from crm.models import Customer

cutoff_date = timezone.now() - timedelta(days=365)
inactive_customers = Customer.objects.filter(orders__isnull=True, created_at__lt=cutoff_date)
count = inactive_customers.count()
inactive_customers.delete()
print(count)
")

# Append result to log with timestamp
echo \"\$(date '+%Y-%m-%d %H:%M:%S') - Deleted customers: $DELETED_COUNT\" >> $LOG_FILE
