from django.db import migrations

def create_initial_phobias(apps, schema_editor):
    Phobias = apps.get_model('app_general', 'Phobias')
    initial_phobias = [
        {"name_TH": "กลัวแมว",      "name_ENG": "Ailurophobia",     "color": "#381f6b",  "image1": "static/app_general/images/pb0101.jpg", "image2": "static/app_general/images/pb0102.jpg"},
        {"name_TH": "กลัวแมงมุม",     "name_ENG": "Arachnophobia",    "color": "#1f2854", "image1": "static/app_general/images/pb0201.png", "image2": "static/app_general/images/pb0202.png"},
        {"name_TH": "กลัวตัวตลก",     "name_ENG": "Coulrophobia",     "color": "#6c1e5d", "image1": "static/app_general/images/pb0301.jpg", "image2": "static/app_general/images/pb0302.jpg"},
        {"name_TH": "กลัวสุนัข",       "name_ENG": "Cynophobia",       "color": "#22421f", "image1": "static/app_general/images/pb0401.jpg", "image2": "static/app_general/images/pb0402.png"},
        {"name_TH": "กลัวเลือด",      "name_ENG": "Hemophobia",       "color": "#544921", "image1": "static/app_general/images/pb0501.jpg", "image2": "static/app_general/images/pb0502.jpg"},
        {"name_TH": "กลัวแมลงสาบ",   "name_ENG": "Katsaridaphobia",  "color": "#381f6b", "image1": "static/app_general/images/pb0601.jpg", "image2": "static/app_general/images/pb0602.jpg"},
        {"name_TH": "กลัวงู",         "name_ENG": "Ophidiophobia",    "color": "#1f2854", "image1": "static/app_general/images/pb0701.jpg", "image2": "static/app_general/images/pb0702.jpg"},
        {"name_TH": "กลัวนก",        "name_ENG": "Ornithophobia",    "color": "#6c1e5d", "image1": "static/app_general/images/pb0801.jpg", "image2": "static/app_general/images/pb0802.png"},
        {"name_TH": "กลัวกบ เขียด",   "name_ENG": "Ranidaphobia",     "color": "#22421f", "image1": "static/app_general/images/pb0901.jpg", "image2": "static/app_general/images/pb0902.jpg"},
        {"name_TH": "กลัวรู",         "name_ENG": "Trypophobia",      "color": "#544921", "image1": "static/app_general/images/pb1001.png", "image2": "static/app_general/images/pb1002.png"},
    ]
    for phobia in initial_phobias:
        Phobias.objects.create(name_TH=phobia["name_TH"], name_ENG=phobia["name_ENG"], color=phobia["color"], image1=phobia["image1"], image2=phobia["image2"])

class Migration(migrations.Migration):

    dependencies = [
        ('app_general', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_initial_phobias),
    ]