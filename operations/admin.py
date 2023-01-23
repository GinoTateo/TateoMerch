from datetime import datetime

from django.contrib import admin

# Register your models here.
from operations.models import Item, Order

class EntryAdmin(admin.ModelAdmin):
    # Overide of the save model
    def save_model(self, request, obj, form, change):
        obj.cart.total += obj.quantity * obj.product.cost
        obj.cart.count += obj.quantity
        obj.cart.updated = datetime.now()
        obj.cart.save()
        super().save_model(request, obj, form, change)


admin.site.register(Item)
admin.site.register(Order)