import datetime
from django.utils.datetime_safe import datetime
from django.contrib import admin
from .models import Merch, Store, WeeklyData, Item, Order, OrderItem

class EntryAdmin(admin.ModelAdmin):
    # Overide of the save model
    def save_model(self, request, obj, form, change):
        obj.cart.total += obj.quantity * obj.product.cost
        obj.cart.count += obj.quantity
        obj.cart.updated = datetime.now()
        obj.cart.save()
        super().save_model(request, obj, form, change)

admin.site.register(Merch)
admin.site.register(Store)
admin.site.register(WeeklyData)
admin.site.register(Item)
admin.site.register(Order)
admin.site.register(OrderItem)