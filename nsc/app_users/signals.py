from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.db import connection

@receiver(post_migrate)
def update_django_site(sender, **kwargs):
    # Ensure sender is the 'sites' application
    if sender.name == 'django.contrib.sites':
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) FROM `phobias_db`.`django_site` WHERE `id` = 1;"
            )
            result = cursor.fetchone()
            if result and result[0] > 0:
                # If there is already a record with id = 1, update it
                cursor.execute(
                    "UPDATE `phobias_db`.`django_site` SET `domain` = '127.0.0.1:8000', `name` = 'AI PICK Phobia System' WHERE (`id` = 1);"
                )
            else:
                # If no record with id = 1 exists, insert a new record
                cursor.execute(
                    "INSERT INTO `phobias_db`.`django_site` (`id`, `domain`, `name`) VALUES (1, '127.0.0.1:8000', 'AI PICK Phobia System');"
                )
