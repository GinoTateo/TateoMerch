from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, reverse
#from multiselectfield import MultiSelectField
from datetime import datetime, timedelta

import account.models
from operations.models import Item
from rsr.models import Store, Route


# class WeeklyData(models.Model):
#     user 				= models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user")
#     date = models.DateField()
#     #merch = models.ManyToManyField(Merch, blank=True)
#     TotalStores = models.IntegerField(max_length=100)
#     TotalCases = models.IntegerField(max_length=100)
#     complete = models.BooleanField(default=False)
#     def __str__(self):
#         return f'{self.user} {self.date}'

class Merch(models.Model):
    user 				= models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user")
    store				= models.OneToOneField(Store, on_delete=models.CASCADE, related_name="user")
    OOS                 = models.ManyToManyField(Item, blank=True, null=True, related_name='OOS')
    worked_cases        = models.ManyToManyField(Item, blank=True, null=True, related_name='worked_cases')
    date                = models.DateTimeField(auto_now_add=True)
    upload              = models.ImageField(upload_to='images', default="N/A", blank=True, null=True)

    def __str__(self):
        return f'{self.store} |  {self.date}'

    def get_num_OOS(self):
            return self.OOS.count()

    def get_num_cases_worked(self):
            return self.worked_cases.count()

class Request(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='receiver')
    store = models.OneToOneField(Store, on_delete=models.CASCADE, default='1')
    date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True, blank=True, null=False)

    def __str__(self):
        return f'{self.store.name} {self.date}'

    def accept(self):
        receiver_route_list = Route.objects.get(user=self.receiver)
        if receiver_route_list:
            receiver_route_list.add_store(self.store.id)
            self.is_active = False
            self.delete()

    def decline(self):
        self.is_active = False
        self.delete()

    def cancel(self):
        self.is_active = False

class Docket(models.Model):
    user 				= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="docket_user")
    store_list			= models.ManyToManyField(Store, related_name="docket_store")
    date                = models.DateField()
    completed           = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user} |  {self.date}'