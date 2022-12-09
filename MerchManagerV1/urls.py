"""MerchManagerV1 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.models import User
from django.urls import include, path

from MerchManagerV1 import settings
from merch import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('merch/', include('merch.urls')),
    path('api/', include('api.urls')),
    path('', views.home, name='index'),
    path('home', views.home, name='index'),
    path('account/', views.account, name='account'),
    path('login', views.loginrequest, name='login'),
    path('add/', views.add, name='index'),
    path('add/store', views.addStore, name='create merch'),
    path('add/merch', views.addMerch, name='create merch'),
    path('add/EOW', views.addWD, name='create merch'),
]

if settings.DEBUG:  # new
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)