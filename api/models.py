from django.db import models

class Account(models.Model):
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    routeNum = models.IntegerField(max_length=100)
    region = models.IntegerField(max_length=100)
    def __str__(self):
        return self.name
