from django.db import models

# Create your models here.
class Phobias(models.Model):
    name_TH = models.CharField(max_length=250)
    name_ENG = models.CharField(max_length=250)
    color = models.CharField(max_length=8)
    count = models.IntegerField(default=0)

class Add_pb(models.Model):
    STATUS = [
        ('unread', 'Unread'),
        ('read', 'Read'),
        ('banned', 'Banned')
    ]
    pb_data = models.CharField(max_length=500)
    pb_status = models.CharField(max_length=500, choices=STATUS, default='unread')
    pb_time = models.DateTimeField(auto_now_add=True)
