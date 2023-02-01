from django.contrib.auth.decorators import login_required
from django.urls import path

#from operations.views import add_to_cart, remove_from_cart, reduce_quantity_item, ProductView, orderForm
from operations import views
from operations.views import orderForm, ProductView, add_to_cart, add_item_order

app_name = "ops"

urlpatterns = [
    # Cart
    path('add-to-cart', add_item_order, name='add-to-cart'),
    path('add-to-cart/<int:pk>/<int:quantity>/', add_to_cart, name='add-to-cart-item-quantity'),
    # path('remove-from-cart/<pk>/', remove_from_cart, name='remove-from-cart'),
    # path('reduce-quantity-item/<pk>/', reduce_quantity_item, name='reduce-quantity-item'),
    path('product/<pk>/', ProductView.as_view(), name='product'),
    path('orderform', login_required(orderForm.as_view()), name='order-form'),

    path('order-summary', views.OrderSummaryView, name='order-summary'),
    path('data/<int:item_id>', views.ItemData, name='item-data'),

]