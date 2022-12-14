from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'account',views.AccountViewSet)
router.register(r'merch',views.MerchViewSet)
urlpatterns = [
    path('', include(router.urls), name='index'),
    path('api-auth', include('rest_framework.urls')),
    path('merch-api-auth', include('rest_framework.urls')),

]