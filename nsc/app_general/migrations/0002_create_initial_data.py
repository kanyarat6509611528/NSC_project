from django.db import migrations

def create_initial_phobias(apps, schema_editor):
    Phobias = apps.get_model('app_general', 'Phobias')
    initial_phobias = [
        {"name_TH": "กลัวแมว",      "name_ENG": "Ailurophobia",     "color": "#381f6b"},
        {"name_TH": "กลัวแมงมุม",     "name_ENG": "Arachnophobia",    "color": "#1f2854"},
        {"name_TH": "กลัวตัวตลก",     "name_ENG": "Coulrophobia",     "color": "#6c1e5d"},
        {"name_TH": "กลัวสุนัข",       "name_ENG": "Cynophobia",       "color": "#22421f"},
        {"name_TH": "กลัวเลือด",      "name_ENG": "Hemophobia",       "color": "#544921"},
        {"name_TH": "กลัวแมลงสาบ",   "name_ENG": "Katsaridaphobia",  "color": "#381f6b"},
        {"name_TH": "กลัวงู",         "name_ENG": "Ophidiophobia",    "color": "#1f2854"},
        {"name_TH": "กลัวนก",        "name_ENG": "Ornithophobia",    "color": "#6c1e5d"},
        {"name_TH": "กลัวกบ เขียด",   "name_ENG": "Ranidaphobia",     "color": "#22421f"},
        {"name_TH": "กลัวรู",         "name_ENG": "Trypophobia",      "color": "#544921"},
    ]
    for phobia in initial_phobias:
        Phobias.objects.create(name_TH=phobia["name_TH"], name_ENG=phobia["name_ENG"], color=phobia["color"])

class Migration(migrations.Migration):

    dependencies = [
        ('app_general', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_initial_phobias),
    ]