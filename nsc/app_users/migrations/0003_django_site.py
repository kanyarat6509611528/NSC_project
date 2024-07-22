from django.db import migrations

def create_or_update_site(apps, schema_editor):
    Site = apps.get_model('sites', 'Site')
    site, created = Site.objects.get_or_create(id=1, defaults={
        'name': 'AI PICK Phobia System',
        'domain': '127.0.0.1:8000' 
    })
    if not created:
        site.name = 'AI PICK Phobia System'
        site.domain = '127.0.0.1:8000'  
        site.save()

class Migration(migrations.Migration):

    dependencies = [
        ('app_users', '0001_initial'),
        ('app_users', '0002_create_initial_data')  
    ]

    operations = [
        migrations.RunPython(create_or_update_site),
    ]