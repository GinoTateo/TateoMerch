from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, reverse

CATEGORY = (
    ('PG', 'PW'),
    ('IG', 'IW'),
    ('SG', 'SW')
)

LABEL = (
    ('10.5', '18'),
    ('10', '12')
)

class Merch(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    store = models.ForeignKey('Store', on_delete=models.CASCADE, default="Safeway")
    OOS = models.IntegerField(max_length=2, default=0)
    case_count = models.IntegerField(max_length=2, default=0)
    date = models.DateTimeField(auto_now_add=True)
    upload = models.ImageField(upload_to='images', default="N/A")
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


class Item(models.Model):
    item_name = models.CharField(max_length=100)
    item_number = models.IntegerField(default=0)
    item_size = models.IntegerField(default=0)
    description = models.TextField()

    def __str__(self):
        return self.item_name

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