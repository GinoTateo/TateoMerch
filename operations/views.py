from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views.generic import DetailView, ListView

from account.models import Account
from operations.models import Item, Order, OrderItem


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
            'object' : order
        }

        return render(request, 'order_summary.html', context)

@login_required
def add_to_cart(request, pk, quantity):
    item = get_object_or_404(Item, pk=pk )
    order_item, created = OrderItem.objects.get_or_create(
        item = item,
        user = request.user,
        ordered = False
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
def remove_from_cart(request, pk):
    item = get_object_or_404(Item, pk=pk )
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
            messages.info(request, "Item \""+order_item.item.item_name+"\" remove from order")
            return redirect("order-summary")
        else:
            messages.info(request, "This Item is not in your order")
            return redirect("product", pk=pk)
    else:
        #add message doesnt have order
        messages.info(request, "You do not have an Order")
        return redirect("product", pk = pk)


@login_required
def reduce_quantity_item(request, pk):
    item = get_object_or_404(Item, pk=pk )
    order_qs = Order.objects.filter(
        user = request.user,
        ordered = False
    )
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__pk=item.pk).exists() :
            order_item = OrderItem.objects.filter(
                item = item,
                user = request.user,
                ordered = False
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
        #add message doesnt have order
        messages.info(request, "You do not have an Order")
        return redirect("order-summary")

class orderForm(ListView):
    model = Item
    template_name = "order_form.html"

@login_required
def ItemData(request, item_id):
    item = Item.objects.get(id=item_id)

    return render(request, "item_data.html", {'item': item })
