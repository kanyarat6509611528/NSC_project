from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from app_general.models import Phobias  # Import Phobias model from app_general

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    first_name = None
    last_name = None
    phobias_set = models.ManyToManyField(
        Phobias,
        through="UserPhobias",
        related_name="user_set",
    )
    def __str__(self):
        return self.username

class UserPhobias(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="user_phobias",
    )
    phobia = models.ForeignKey(
        Phobias,
        on_delete=models.CASCADE,
        related_name="phobia_users",
    )

    class Meta:
        db_table = 'UserPhobias' 
        constraints = [
            models.UniqueConstraint(fields=("user", "phobia"), name="unique_user_phobias")
        ]

    def __str__(self):
        return f"{self.user.username} - {self.phobia.name}"
