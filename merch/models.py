from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, reverse
#from multiselectfield import MultiSelectField
from datetime import datetime, timedelta


TYPE = (
    ('G', 'Ground'),
    ('W', 'Whole Bean'),
    ('K', 'K-Cup'),
)

RECEIVE_TYPE = (
    ('DEX', 'DEX'),
    ('SCAN', 'SCAN'),
    ('SIGN', 'SIGN'),
)

DISPLAY_TYPE = (
    ('Shipper', 'Shipper'),
    ('Wire rack', 'Wire rack'),
    ('Hanging rack', 'Hanging rack'),
    ('End cap', 'End cap'),
    ('Rolling rack', 'Rolling rack'),
)

DISPLAY_LOCATION = (
    ('BOH', 'Back of house'),
    ('FOH', 'Front of house'),
    ('Aisle', 'Aisle'),
    ('Bakery', 'Bakery'),
    ('Deli', 'Deli'),
    ('Pharmacy', 'Pharmacy'),
    ('Check-stand', 'Check-stand'),
)

BRAND = (
    ('P', 'Peets'),
    ('I', 'Intelligentsia'),
    ('S', 'Stumptown'),
)

SIZE = (
    ('18', '18oz'),
    ('10.5', '10.5oz'),
    ('10.5', '10.5oz'),
    ('10', 'K-10'),
    ('22', 'K-22'),
    ('32', 'K-32'),
    ('48', 'K-48'),
)

WEEKDAYS = (
    ('Monday', 'Monday'),
    ('Tuesday', 'Tuesday'),
    ('Wednesday', 'Wednesday'),
    ('Thursday', 'Thursday'),
    ('Friday', 'Friday'),
    ('Saturday', 'Saturday'),
    ('Sunday', 'Sunday'),
)

STORE = (
    ('Safeway', 'Safeway'),
    ('Target', 'Target'),
    ('Lucky', 'Lucky'),
    ('FoodMaxx', 'FoodMaxx'),
    ('SaveMart', 'SaveMart'),
    ('Lunardis', 'Lunardis'),
    ('Nob Hill', 'Nob Hill'),
    ('Wholefoods', 'Wholefoods'),
    ('BerkeleyBowl', 'BerkeleyBowl'),
)

class Item(models.Model):
    item_brand = models.CharField(choices=BRAND, max_length=25, default='P')
    item_type = models.CharField(choices=TYPE, max_length=25)
    item_size = models.CharField(choices=SIZE, max_length=25)
    item_name = models.CharField(max_length=100)
    item_number = models.IntegerField(default=0)

    def __str__(self):
        return self.item_name + ' ' + self.item_brand + self.item_type + self.item_size

    def get_absolute_url(self):
        return reverse("product", kwargs={
            "pk": self.pk

        })

    def get_add_to_cart_url(self):
        return reverse("add-to-cart", kwargs={
            "pk": self.pk
        })

    def get_remove_from_cart_url(self):
        return reverse("remove-from-cart", kwargs={
            "pk": self.pk
        })

class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.item.item_name}"

    def get_total_item_price(self):
        return self.quantity * self.item.item_size

    def get_final_quantity(self):
        if self.quantity:
            return self.quantity
        return self.quantity

class WeeklyData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    #merch = models.ManyToManyField(Merch, blank=True)
    TotalStores = models.IntegerField(max_length=100)
    TotalCases = models.IntegerField(max_length=100)
    complete = models.BooleanField(default=False)
    def __str__(self):
        return f'{self.user} {self.date}'

class Merch(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    store = models.ForeignKey('Store', on_delete=models.CASCADE, default="1")
    OOS = models.ManyToManyField(Item, blank=True, null=True, related_name='OOS')
    worked_cases = models.ManyToManyField(Item, blank=True, null=True, related_name='worked_cases')
    date = models.DateTimeField(auto_now_add=True)
    upload = models.ImageField(upload_to='images', default="N/A", blank=True, null=True)

    def __str__(self):
        return f'{self.store} |  {self.date}'

    def get_num_OOS(self):
            return self.OOS.count()

    def get_num_cases_worked(self):
            return self.worked_cases.count()


def default_start_time():
    now = datetime.now()
    start = now.replace(hour=22, minute=0, second=0, microsecond=0)
    return start if start > now else start + timedelta(days=1)

# class ServiceDay(models.Model):
#     day = models.CharField(default="Monday", choices=WEEKDAYS, max_length=25)
#     time = models.TimeField(default=default_start_time)
#     frequency = models.IntegerField(default=0, max_length=100, blank=True, null=True)
#     def __str__(self):
#         return f'{self.day} {self.time}'

class Display(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    active = models.BooleanField(default=False)
    location = models.CharField(default= "End cap", choices=DISPLAY_LOCATION, max_length=25)
    type = models.CharField(default="Shipper", choices=DISPLAY_TYPE, max_length=25)
    description = models.CharField(default="", max_length=140)

    def __str__(self):
        return f"{self.type} at {self.location}"

class Store(models.Model):
    name = models.CharField(default= "Safeway", choices=STORE, max_length=25)
    number = models.IntegerField(default= "", max_length=100, blank=True, null=True)
    City = models.CharField(default= "", max_length=25)
    #Service_days = models.ForeignKey('ServiceDay', on_delete=models.CASCADE, default="Monday")
    RSRrt = models.IntegerField(default="", max_length=100)
    Area = models.CharField(default= "", max_length=25)
    receiver_name = models.CharField(default="", max_length=25)
    receiver_open = models.TimeField(default=default_start_time)
    receiver_close = models.TimeField(default=default_start_time)
    receive_type = models.CharField(default="DEX", choices=RECEIVE_TYPE, max_length=25)
    weekly_average = models.IntegerField(default=0, max_length=100)
    Address = models.CharField(default= "", max_length=50)
    BS_Location = models.CharField(default= "", max_length=50)
    displays = models.ManyToManyField(Display)
    def __str__(self):
        return f'{self.name} {self.number}'

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    def get_total_quantity(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.quantity
        return total