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
from django.urls import include, path
from MerchManagerV1 import settings
from merch import views

urlpatterns = [

    # Base patterns
    path('admin/', admin.site.urls),
    path('merch/', include('merch.urls')),
    path('api/', include('api.urls')),

    path('', views.home, name='index'),

    #
    path('home', views.home, name='index'),
    path('account/', views.account, name='account'),
    path('login', views.loginrequest, name='login'),
    path('logout', views.logout_view, name='login'),
    path('register', views.loginrequest, name='register'),
    path('accounts/login/', views.loginrequest, name='login'),

    #
    path('add/', views.add, name='index'),
    path('add/store', views.addStore, name='create store'),
    path('add/merch', views.addMerch, name='create merch'),
    path('add/EOW', views.addWD, name='create EOW'),
    path('add/Item', views.addItem, name='create item'),

    #
    path('route-review', views.RouteReview, name='route-review'),
    path('merch/data/<int:user_id>/<int:store_id>', views.StoreData, name='order-summary-data'),

    # url(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    # url(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
]

if settings.DEBUG:  # new
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

