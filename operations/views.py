from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views.generic import DetailView, ListView
from rest_framework.filters import BaseFilterBackend

from account.models import Account
# from operations.filters import ItemFilter
from operations.filters import ItemFilter
from operations.forms import WarehouseForm
from operations.models import Item, Order, OrderItem, Warehouse, Inventory


class ProductView(DetailView):
    model = Item
    template_name = "order_page.html"


@login_required
def OrderSummaryView(request):
    # current_user = request.user
    # user = get_object_or_404(User, username=current_user)
    user = Account.objects.get(username=request.user)
    order = Order.objects.filter(user=user)
    context = {
        'object': order
    }

    return render(request, 'order_summary.html', context)


@login_required
def add_to_cart(request, pk, quantity):
    item = get_object_or_404(Item, pk=pk)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs[0]

        if order.items.filter(item__pk=item.pk).exists():
            order_item.quantity += quantity
            order_item.save()
            messages.info(request, "Added quantity Item")
            return redirect("order-form")
        else:
            order.items.add(order_item)
            order_item.quantity += quantity - 1
            order_item.save()
            messages.info(request, "Item added to your cart")
            return redirect("order-form")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        order_item.quantity += quantity - 1
        order_item.save()
        messages.info(request, "Item added to your cart")
        return redirect("order-form")


@login_required
def add_item_order(request, *args, **kwargs):
    user_id = request.user.id

    user = Account.objects.get(id=user_id)
    payload = {}

    item_id = request.POST.get("item_id")
    quantity_str = request.POST.get("quantity")
    try:
        quantity = int(quantity_str)
    except ValueError:
        quantity = quantity_str

    item = Item.objects.get(pk=item_id)
    if item:
        order_item, created = OrderItem.objects.get_or_create(
            item=item,
            user=request.user,
            ordered=False
        )
        order = Order.objects.filter(user=request.user, ordered=False)
        if order.exists():
            order = order[0]

            if order.items.filter(item__pk=item.pk).exists():
                order_item.quantity += quantity
                order_item.save()
                payload['response'] = "Item added to your cart"
            else:
                order.items.add(order_item)
                order_item.quantity += quantity - 1
                order_item.save()
                payload['response'] = "Item added to your cart"
        else:
            ordered_date = timezone.now()
            order = Order.objects.create(user=request.user, ordered_date=ordered_date)
            order.item.add(item)
            order_item.quantity += quantity - 1
            order_item.save()
            payload['response'] = "Item added to your cart"
    else:
        payload['response'] = "Could not find request"
    return redirect("ops:order-form")


@login_required
def remove_from_cart(request, pk):
    item = get_object_or_404(Item, pk=pk)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__pk=item.pk).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order_item.delete()
            messages.info(request, "Item \"" + order_item.item.item_name + "\" remove from order")
            return redirect("order-summary")
        else:
            messages.info(request, "This Item is not in your order")
            return redirect("product", pk=pk)
    else:
        # add message doesnt have order
        messages.info(request, "You do not have an Order")
        return redirect("product", pk=pk)


@login_required
def reduce_quantity_item(request, pk):
    item = get_object_or_404(Item, pk=pk)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__pk=item.pk).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order_item.delete()
            messages.info(request, "Item quantity was updated")
            return redirect("order-summary")
        else:
            messages.info(request, "This Item not in your cart")
            return redirect("order-summary")
    else:
        # add message doesnt have order
        messages.info(request, "You do not have an Order")
        return redirect("order-summary")


class orderForm(ListView):
    model = Item
    template_name = "order_form2.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = ItemFilter(self.request.GET, queryset=self.get_queryset())
        return context


@login_required
def ItemData(request, item_id):
    item = Item.objects.get(id=item_id)

    return render(request, "item_data.html", {'item': item})


def WarehouseDateItemView(request, warehouse_id):
    warehouse = Warehouse.objects.get(id=warehouse_id)
    inventory = Inventory.objects.filter(warehouse=warehouse).latest('date')
    inv_items = inventory.items.all()
    items = Item.objects.filter(Q(item_type='G') | Q(item_type='W'))

    return render(request, "warehouse_dates.html", {'items': inv_items})


@login_required
def WarehouseDateItemForm(request, item_id):
    item = Item.objects.get(id=item_id)
    items = Item.objects.filter(Q(item_type='G') | Q(item_type='W'))
    last_item = items.last()
    form = WarehouseForm()
    if item.pk is last_item.pk:
        return render(request, "warehouse_dates.html", {'items': items})
    return render(request, "item_date_form.html", {'item': item, 'form': form})


@login_required
def WarehouseDateItemInput(request, item_id):
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = WarehouseForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            date = form.cleaned_data['Date']

            item = Item.objects.get(id=item_id)
            item.item_date = date
            item.save()

            items = Item.objects.filter(Q(item_type='G') | Q(item_type='W'))
            last_item = items.last()
            item = Item.objects.get(id=item_id + 1)
            if item.pk is last_item.pk:
                return render(request, "warehouse_dates.html", {'items': items})
            return render(request, "item_date_form.html", {'form': form, 'item': item})

    # if a GET (or any other method) we'll create a blank form
    else:
        form = WarehouseForm()

    return render(request, 'item_date_form.html', {'form': form})


@login_required
def WarehouseDateForm(request, warehouse_id):
    items = Item.objects.all()

    warehouse = Warehouse.objects.get(id=warehouse_id)
    inventory = Inventory.objects.filter(warehouse=warehouse).latest('date')
    inv_items = inventory.items.all()

    for item in inv_items:
        item.item_date = None
        item.save()

    item = items.objects.first()
    form = WarehouseForm()

    return render(request, 'item_date_form.html', {'form': form, 'item': item})


@login_required
def WarehouseDateFormSkip(request, item_id):
    item = Item.objects.get(id=item_id + 1)
    form = WarehouseForm()

    items = Item.objects.filter(Q(item_type='G') | Q(item_type='W'))
    last_item = items.last()

    if item.pk is last_item.pk:
        return render(request, "warehouse_dates.html", {'items': items})

    return render(request, "item_date_form.html", {'form': form, 'item': item})


@login_required
def WarehouseDashboard(request):
    warehouses = Warehouse.objects.all()

    return render(request, 'warehouse_dashboard.html', {'warehouses': warehouses})


@login_required
def WarehouseDetail(request, warehouse_id):
    warehouse = Warehouse.objects.get(id=warehouse_id)

    return render(request, 'warehouse_detail.html', {'warehouse': warehouse})
