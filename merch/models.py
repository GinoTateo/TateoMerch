from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect


class Merch(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    store = models.ForeignKey('Store', on_delete=models.CASCADE, default="Safeway")
    OOS = models.IntegerField(max_length=2, default=0)
    case_count = models.IntegerField(max_length=2, default=0)
    date = models.DateTimeField(auto_now_add=True)
    upload = models.ImageField(upload_to='media/images', default="N/A")
    def __str__(self):
        return f'{self.store} |  {self.date}'

class Store(models.Model):
    name = models.CharField(max_length=100)
    number = models.IntegerField(max_length=100)
    def __str__(self):
        return f'{self.name} {self.number}'

class WeeklyData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    TotalStores = models.IntegerField(max_length=100)
    TotalCases = models.IntegerField(max_length=100)
    def __str__(self):
        return f'{self.user} {self.date}'