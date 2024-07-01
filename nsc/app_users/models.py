from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
# class CustomUser(AbstractUser):
#     email = models.EmailField(unique=True)

# class UserPhobias(models.Model):
#     check_pb = models.BooleanField(default=False)
#     user = models.ForeignKey(AbstractUser, on_delete=models.CASCADE)
#     phobias = user = models.ForeignKey("app_general.phobias", on_delete=models.CASCADE)