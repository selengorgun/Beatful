from django.db import models


class Event(models.Model):
    title = models.CharField(max_length=500)
    description = models.CharField(max_length=500)
    body = models.TextField()
    date = models.CharField(max_length=500)
    site = models.CharField(max_length=500)

# Create your models here.
