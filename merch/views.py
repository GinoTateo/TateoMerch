from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import resolve

from .forms import StoreForm, MerchForm, WeeklyDataForm, StoreForm2
from .models import Merch, WeeklyData
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
                return redirect("index")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    form = AuthenticationForm()
    return render(request=request, template_name="login.html", context={"login_form": form})


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
