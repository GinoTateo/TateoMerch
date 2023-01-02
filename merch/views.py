
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.template.context_processors import request
from django.urls import resolve
from django.utils import timezone
from django.views import View
from django.views.generic import DetailView, ListView

from .forms import StoreForm, MerchForm, WeeklyDataForm, StoreForm2, ItemForm
from .models import Merch, WeeklyData, Order, Item, OrderItem
from django.template import loader
from django.contrib import messages


@login_required(login_url='login')
def index(request):
    latest_list = Merch.objects.order_by('-date')[:25]
    template = loader.get_template('index.html')
    context = {
        'latest_list': latest_list,
    }
    return HttpResponse(template.render(context, request))

class ProductView(DetailView):
    model = Item
    template_name = "order_page.html"

@login_required(login_url='login')
def detail(request, merch_id):
    merch = get_object_or_404(Merch, pk=merch_id)
    return render(request, 'detail.html', {'merch': merch})


def home(request):
    latest_list = WeeklyData.objects.order_by('-date')[:5]
    template = loader.get_template('home.html')
    context = {
        'latest_list': latest_list,
    }
    return HttpResponse(template.render(context, request))


def loginrequest(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            print("username")
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect("home")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    form = AuthenticationForm()
    return render(request=request, template_name="login.html", context={"login_form": form})

def logout_view(request):
    logout(request)
    return render(request, 'home.html')

def merchuser(request, merchuser):
    user = get_object_or_404(User, username=merchuser)
    profile = User.objects.get(username=user)
    url_name = resolve(request.path).url_name

    context = {
        'profile': profile,
        'url_name': url_name,
    }

    return render(request, 'merchuser.html', context)


@login_required(login_url='login')
def account(request):
    current_user = request.user
    user = get_object_or_404(User, username=current_user)
    profile = User.objects.get(username=user)
    url_name = resolve(request.path).url_name

    context = {
        'profile': profile,
        'url_name': url_name,
    }

    return render(request, 'merchuser.html', context)


@login_required(login_url='login')
def add(request):
    return render(request, 'addHome.html')


@login_required(login_url='login')
def addStore(request):
    if request.method == 'POST':
        form = StoreForm2(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/add')

    else:
        form = StoreForm2()

    return render(request,
                  'add.html',
                  {'form': form})


@login_required(login_url='login')
def addMerch(request):
    if request.method == 'POST':
        form = MerchForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/add')

    else:
        form = MerchForm()

    return render(request,
                  'add.html',
                  {'form': form})


@login_required(login_url='login')
def addWD(request):
    if request.method == 'POST':
        form = WeeklyDataForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/add')

    else:
        form = WeeklyDataForm()

    return render(request,
                  'add.html',
                  {'form': form})

@login_required(login_url='login')
def addItem(request):
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/add')

    else:
        form = ItemForm()

    return render(request,
                  'add.html',
                  {'form': form})

@login_required
def OrderSummaryView(request):
        # current_user = request.user
        # user = get_object_or_404(User, username=current_user)
        user = User.objects.get(username=request.user)
        order = Order.objects.filter(user=user)
        context = {
            'object' : order
        }

        return render(request, 'order_summary.html', context)


# class OrderSummaryView(LoginRequiredMixin, View):
#     def get(self, *args, **kwargs):
#
#         try:
#             user = get_object_or_404(User, username=self.kwargs.get('username'))
#             order = Order.objects.get(user, ordered=False)
#             context = {
#                 'object' : order
#             }
#             return render(self.request, 'order_summary.html', context)
#         except ObjectDoesNotExist:
#             messages.error(self.request, "You do not have an order")
#             return redirect("order_summary.html")

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