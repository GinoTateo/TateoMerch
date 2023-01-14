from django.contrib.auth.decorators import login_required
from django.urls import path, include
from django.conf.urls.static import static
from MerchManagerV1 import settings
from django.views.static import serve
from . import views
from .views import OrderSummaryView, add_to_cart, remove_from_cart, reduce_quantity_item, ProductView, orderForm

urlpatterns = [
    # Base
    path('', views.index, name='index'),
    path('home', views.home, name='home'),

    # Account level
    path('account', views.account, name='account'),
    path('login', views.loginrequest, name='login'),
    path('register', views.loginrequest, name='login'),
    path('logout', views.logout_view, name='logout'),

    # Add
    path('add', views.add, name='add toolbar'),
    path('add/store', views.addStore, name='create merch'),
    path('add/merch', views.addMerch, name='create merch'),
    path('add/EOW', views.addWD, name='create merch'),
    path('add/Item', views.addItem, name='create merch'),

    # Merch
    path('<int:merch_id>/', views.detail, name='detail'),
    path('<merchuser>/', views.merchuser, name='merch-user'),
    path('weekly', views.weekly, name='weekly-data'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('create-merch/<storeid>', views.create_merch, name='create-merch'),
    #path('data', views.merchuser, name='merch-user'), /<storeid>

    # Route
    path('route-review', views.RouteReview, name='route-review'),
    path('order-summary', views.OrderSummaryView, name='order-summary'),
    path('/data/<int:user_id>/<int:store_id>', views.StoreData, name='order-summary-data'),

    # Reports
    path('send', views.send_email, name='send-email'),

    # Cart
    path('add-to-cart/<pk>/', add_to_cart, name='add-to-cart'),
    path('add-to-cart/<pk>/<int:quantity>/', add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<pk>/', remove_from_cart, name='remove-from-cart'),
    path('reduce-quantity-item/<pk>/', reduce_quantity_item, name='reduce-quantity-item'),
    path('product/<pk>/', ProductView.as_view(), name='product'),
    path('orderform', login_required(orderForm.as_view()), name='order-form'),
]

if settings.DEBUG:  # new
    static(settings.STATIC_URL,document_root=settings.MEDIA_ROOT)