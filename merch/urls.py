from django.urls import path, include
from django.conf.urls.static import static
from MerchManagerV1 import settings
from django.views.static import serve
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('home', views.home, name='home'),
    path('about', views.index, name='about'),
    path('account', views.account, name='account'),
    path('login', views.loginrequest, name='login'),
    path('<int:merch_id>/', views.detail, name='detail'),
    path('add', views.add, name='add toolbar'),
    path('add/store', views.addStore, name='create merch'),
    path('add/merch', views.addMerch, name='create merch'),
    path('add/EOW', views.addWD, name='create merch'),
    path('<merchuser>/', views.merchuser, name='merch-user'),
]

if settings.DEBUG:  # new
    static(settings.STATIC_URL,document_root=settings.MEDIA_ROOT)