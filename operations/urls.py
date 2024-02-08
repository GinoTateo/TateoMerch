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

    # Order
    path('warehouse/<int:warehouse_id>/orderform', login_required(orderForm.as_view()), name='warehouse-orderform'),
    path('warehouse/<int:warehouse_id>/inventory', views.WarehouseDateItemView, name='warehouse-inventory'),
    path('warehouse/<int:warehouse_id>/inventory/physical', views.WarehouseDateForm, name='warehouse-physical-inventory'),
    path('warehouse/orders', views.orders_view, name='orderview'),
    path('warehouse/order/<str:order_id>/', views.order_detail_view, name='detail_view'),

    path('order-summary', views.OrderSummaryView, name='order-summary'),
    path('order-summary/<int:order_id>', views.OrderSummaryViewWithID, name='order-summary'),
    path('data/<int:item_id>', views.ItemData, name='item-data'),

    path('dashboard/', views.WarehouseDashboard, name='warehouse-dash'),
    path('warehouse/<int:warehouse_id>', views.WarehouseDetail, name='warehouse-detail'),
    path('warehouse/<int:warehouse_id>/warehousemanager', views.WarehouseManagerDetail, name='warehouse-detail'),


    path('warehouse-dates', views.WarehouseDateItemView, name='warehouse-dates'),
    path('warehouse-dates/input', views.WarehouseDateForm, name='warehouse-dates-form'),
    path('warehouse-dates/<int:item_id>/<int:inventory_id>/skip', views.WarehouseDateFormSkip, name='warehouse-dates-form-skip'),
    path('warehouse-dates/<int:item_id>', views.WarehouseDateItemForm, name='warehouse-date-form'),
    path('warehouse-dates/<int:item_id>/<int:inventory_id>/input', views.WarehouseDateItemInput, name='warehouse-date-input'),

    #Print pallet pages
    path('warehouse/<int:route_id>/print/pallet/', views.PalletPages, name='print-pallet-pages'),
    path('warehouse/<int:warehouse_id>/print/', views.PrintPalletPages, name='print-pallet-pages'),

    #Order_Status
    path('warehouse/order-status-update/<int:order_id>/update', views.WarehouseManagerOrderStatusUpdate, name='whmosu'),
    path('warehouse/order-status-view/', views.WarehouseManagerOrderStatusView, name='whmosv'),
    path('warehouse/order-status-view/<int:order_id>/', views.WarehouseManagerOrderStatusDetail, name='whmosv'),
    path('warehouse/order/<str:order_id>/pdf/', views.generate_order_pdf, name='generate_order_pdf'),
]
