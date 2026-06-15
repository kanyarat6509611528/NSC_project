from django.db import migrations
from django.contrib.auth import get_user_model

def create_admin_user(apps, schema_editor):
    User = get_user_model()
    admin_user = User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='123'
    )
    admin_user.save()

class Migration(migrations.Migration):

    dependencies = [
        ('app_users', '0001_initial'),  # Replace with your actual dependency
    ]

    operations = [
        migrations.RunPython(create_admin_user),
    ]