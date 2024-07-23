# app_users/signals.py
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.db import connection

@receiver(post_migrate)
def update_django_site(sender, **kwargs):
    # ตรวจสอบให้แน่ใจว่า sender คือ 'sites' application
    if sender.name == 'django.contrib.sites':
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE django_site SET domain = '127.0.0.1:8000', name = 'AI PICK Phobia System' WHERE id = 1;"
            )