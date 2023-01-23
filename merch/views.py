import datetime
import json

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, BadHeaderError
from django.shortcuts import get_object_or_404, render, redirect
from django.template.loader import render_to_string
from django.urls import resolve
from django.utils.html import strip_tags
from django.core.mail import send_mail

from account.models import Account
from operations.models import Item
from rsr.models import Store
from .models import Merch, Request, Docket
from django.template import loader

@login_required(login_url='login')
def index(request):
    latest_list = Merch.objects.order_by('-date')[:25]
    template = loader.get_template('merch/index.html')
    context = {
        'latest_list': latest_list
    }
    return HttpResponse(template.render(context, request))

@login_required(login_url='login')
def docket(request, user_id):
    my_dockets = Docket.objects.order_by('-date')[:25]
    # dockets_list = my_dockets.order_by('-date')[:5]
    template = loader.get_template('merch/docket.html')
    context = {
        'list': my_dockets,
    }
    return HttpResponse(template.render(context, request))

@login_required(login_url='login')
def detail(request, merch_id):
    merch = get_object_or_404(Merch, pk=merch_id)
    return render(request, 'merch/detail.html', {'merch': merch})

# @login_required
# def weekly(request):
#     latest_list = WeeklyData.objects.order_by('-date')[:5]
#     template = loader.get_template('weekly_view.html')
#     context = {
#         'latest_list': latest_list,
#     }
#     return HttpResponse(template.render(context, request))


@login_required(login_url='login')
def dashboard(request):
    #user = get_object_or_404(Account, username=merchuser)
    latest_list = Merch.objects.order_by('-date')[:5]
    template = loader.get_template('merch/merchandiser_dashboard_view.html')
    user = Account.objects.get(username=request.user)
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

@login_required(login_url='login')
def merchuser(request, merchuser):
    user = get_object_or_404(Account, username=merchuser)
    profile = Account.objects.get(username=user)
    url_name = resolve(request.path).url_name
    context = {
        'profile': profile,
        'url_name': url_name,
    }
    return render(request, 'merch/merchandiser_view.html', context)


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
def SpecificStoreMerch(request, user_id, store_id):
        user = Account.objects.get(username=request.user)
        if (request.user.is_superuser):
            rtmd = Store.objects.all()
        else:
            rtmd = Store.objects.filter(RSRrt=user.username)
            #storedisplay = Store.displays.objects.filter(RSRrt=user.username)

        routeData = get_object_or_404(rtmd, pk=store_id)
        md = Merch.objects.filter(store=routeData).order_by('-date')
        #displays = Merch.objects.filter(store=routeData)
        return render(request, 'merch/index.html', {'store': routeData,
                                                          'latest_list': md,
                                                    #'display': displays
                                                    })


# class OrderSummaryView(LoginRequiredMixin, View):
#     def get(self, *args, **kwargs):
#
#         try:
#             user = get_object_or_404(Account, username=self.kwargs.get('username'))
#             order = Order.objects.get(user, ordered=False)
#             context = {
#                 'object' : order
#             }
#             return render(self.request, 'order_summary.html', context)
#         except ObjectDoesNotExist:
#             messages.error(self.request, "You do not have an order")
#             return redirect("order_summary.html")

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

@login_required
def merch_request(request, *args, **kwargs):
    context = {}
    user = request.user
    if user.is_authenticated:
        #user_id = kwargs.get("user_id")
        #rout = Request.objects.get(pk=user_id)
        if user:
            merch_request = Request.objects.filter(receiver=user, is_active=True)
            context['merch_requests'] = merch_request
        else:
            return HttpResponse("You cant view another users friend requests")
    else:
        redirect('Login')
    return render(request, "merch/request_view.html", context)

@login_required
def send_merch_request(request, receiver_id, store_id):

    payload = {}
    user_id = request.user.id
    if user_id:
        user = Account.objects.get(id=user_id)
        receiver = Account.objects.get(id=receiver_id)
        store = Store.objects.get(id=store_id)
        try:
            merch_request = Request.objects.filter(sender=user, receiver=receiver)
            try:
                for request in merch_request:
                    if request.is_active and request.store == store:
                        raise Exception("Already sent a request")

                merch_request = Request(sender=user, receiver=receiver, store=store)
                merch_request.save()
                payload['response'] = "Merch request sent."
            except Exception as e:
                payload['response'] = str(e)
        except Request.DoesNotExist:
            mrq = Request(sender=user, receiver=receiver, store=store)
            mrq.save()
            payload['response'] = "Merch request sent."

        if payload['response'] is None:
            payload['response'] = "Something went wrong."
    else:
        payload['response'] = "Unable to send request."

    return redirect('rsr:route-review')

@login_required
def cancel_merch_request(request, receiver_id, store_id):
    payload = {}
    user_id = request.user.id
    if user_id:
        user = Account.objects.get(id=user_id)
        receiver = Account.objects.get(id=receiver_id)
        store = Store.objects.get(id=store_id)
        merch_request = Request.objects.filter(sender=user, receiver=receiver)
        try:
            for request in merch_request:
                if request.is_active and request.store == store:
                    request.delete()
        except Exception as e:
            payload['response'] = str(e)
    else:
        payload['response'] = "Unable to send request."
    return redirect('rsr:route-review')

@login_required
def accept_merch_request(request, *args, **kwargs):
    user_id = request.user.id

    user = Account.objects.get(id=user_id)
    payload = {}

    merch_request_id = kwargs.get("request_id")
    if merch_request_id:
        merch_request = Request.objects.get(pk=merch_request_id)
        if merch_request.receiver == user:
            if merch_request:
                merch_request.accept()
                payload['response'] = "Merch request accepted."
            else:
                payload['response'] = "Could not find request."
        else:
            payload['response'] = "This is not your request!"
    else:
        payload['response'] = "Could not find request"
    return redirect('merch:view-merch-request')

@login_required
def StoreData(request, user_id, store_id):
        user = Account.objects.get(username=request.user)
        if (request.user.is_superuser):
            rtmd = Store.objects.all()
        else:
            rtmd = Store.objects.filter(RSRrt=user.username)
            #storedisplay = Store.displays.objects.filter(RSRrt=user.username)

        routeData = get_object_or_404(rtmd, pk=store_id)
        md = Merch.objects.filter(store=routeData).order_by('-date')[:5]
        #displays = Merch.objects.filter(store=routeData)
        return render(request, 'rsr/route-review-data.html', {'store': routeData,
                                                          'merch': md,
                                                              #'display': displays
                                                              })

@login_required
def decline_merch_request(request, *args, **kwargs):
    user_id = request.user.id

    user = Account.objects.get(id=user_id)
    payload = {}

    merch_request_id = kwargs.get("request_id")
    if merch_request_id:
        merch_request = Request.objects.get(pk=merch_request_id)
        if merch_request.receiver == user:
            if merch_request:
                merch_request.decline()
                payload['response'] = "Merch request accepted."
            else:
                payload['response'] = "Could not find request."
        else:
            payload['response'] = "This is not your request!"
    else:
        payload['response'] = "Could not find request"
    return redirect('merch:view-merch-request')

@login_required(login_url='login')
def item(request):
    template = loader.get_template('merch/product_view.html')
    items = Item.objects.all()

    context = {
        'items': items,
    }
    return HttpResponse(template.render(context, request))
