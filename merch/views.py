import datetime

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect, BadHeaderError
from django.shortcuts import get_object_or_404, render, redirect
from django.template.context_processors import request
from django.template.loader import render_to_string
from django.urls import resolve
from django.utils import timezone
from django.utils.html import strip_tags
from django.views import View
from django.views.generic import ListView, DetailView
from django.core.mail import send_mail

from .forms import StoreForm, MerchForm, WeeklyDataForm, StoreForm2, ItemForm, MerchForm2
from .models import Merch, WeeklyData, Order, Item, OrderItem, Store, Display
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

@login_required
def weekly(request):
    latest_list = WeeklyData.objects.order_by('-date')[:5]
    template = loader.get_template('weekly.html')
    context = {
        'latest_list': latest_list,
    }
    return HttpResponse(template.render(context, request))

def home(request):
    return render(request, 'home.html')

@login_required(login_url='login')
def dashboard(request):
    #user = get_object_or_404(User, username=merchuser)
    latest_list = WeeklyData.objects.order_by('-date')[:5]
    template = loader.get_template('merch-dashboard.html')
    user = User.objects.get(username=request.user)
    if (request.user.is_superuser):
        rtmd = Store.objects.all()
    else:
        rtmd = Store.objects.filter(RSRrt=user.username)

    context = {
        'weekly': latest_list,
        'stores': rtmd,
        'requests': rtmd,
    }
    return HttpResponse(template.render(context, request))

def loginrequest(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect("route-review")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    form = AuthenticationForm()
    return render(request=request, template_name="login.html", context={"login_form": form})

def logout_view(request):
    logout(request)
    return render(request, 'home.html')

@login_required(login_url='login')
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

@login_required
def RouteReview(request):
        user = User.objects.get(username=request.user)
        if (request.user.is_superuser):
            rtmd = Store.objects.all()
        else:
            rtmd = Store.objects.filter(RSRrt=user.username)

        context = {
            'list' : rtmd
        }

        return render(request, 'route-review.html', context)

@login_required
def StoreData(request, user_id, store_id):
        user = User.objects.get(username=request.user)
        if (request.user.is_superuser):
            rtmd = Store.objects.all()
        else:
            rtmd = Store.objects.filter(RSRrt=user.username)
            #storedisplay = Store.displays.objects.filter(RSRrt=user.username)

        routeData = get_object_or_404(rtmd, pk=store_id)
        md = Merch.objects.filter(store=routeData).order_by('-date')[:5]
        #displays = Merch.objects.filter(store=routeData)
        return render(request, 'route-review-data.html', {'store': routeData,
                                                          'merch': md,
                                                          #'display': displays
                                                        })

@login_required
def SpecificStoreMerch(request, user_id, store_id):
        user = User.objects.get(username=request.user)
        if (request.user.is_superuser):
            rtmd = Store.objects.all()
        else:
            rtmd = Store.objects.filter(RSRrt=user.username)
            #storedisplay = Store.displays.objects.filter(RSRrt=user.username)

        routeData = get_object_or_404(rtmd, pk=store_id)
        md = Merch.objects.filter(store=routeData).order_by('-date')
        #displays = Merch.objects.filter(store=routeData)
        return render(request, 'index.html', {'store': routeData,
                                                          'latest_list': md,
                                                          #'display': displays
                                                        })


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

@login_required
def send_email(request):
    today = datetime.datetime.now()
    # fivedays = datetime.timedelta(days=5)
    # dayrange = today - fivedays

    enddate = today - datetime.timedelta(days=5)

    latest_list = Merch.objects.filter(date__range=[enddate, today],store__RSRrt='731')
    # latest_list.filter(date__range=[today, fivedays])

    html_message = render_to_string('email_template.html', {'latest_list': latest_list})
    plain_message = strip_tags(html_message)

    subject = request.POST.get('subject', 'Merch ')
    message = request.POST.get('message', plain_message)
    from_email = request.POST.get('from_email', 'Tateomerch@gmail.com')
    if subject and message and from_email:
        try:
            send_mail(subject, message, from_email, ['TateoGino@gmail.com'])
        except BadHeaderError:
            return HttpResponse('Invalid header found.')
        return HttpResponseRedirect('home')
    else:
        return HttpResponse('Make sure all fields are entered and valid.')

@login_required
def create_merch(request, storeid):
    current_store = get_object_or_404(Store, pk=storeid)
    current_user = request.user

    if request.method == 'POST':
        form = MerchForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/merch/dashboard')
        else:
            print(form.errors)

    else:
        form = MerchForm(initial={"user":  current_user, "store": current_store})

    return render(request,
                  'create-merch.html',
                  {'form': form,
                   'store': current_store
                   })