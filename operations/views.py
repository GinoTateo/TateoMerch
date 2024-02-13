from bson import ObjectId
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views.generic import DetailView, ListView
from pymongo import MongoClient
from reportlab.lib.pagesizes import letter
from rest_framework.filters import BaseFilterBackend

import rsr.models
from account.models import Account
# from operations.filters import ItemFilter
from operations.filters import ItemFilter
from operations.forms import WarehouseForm, palletForm
from operations.models import Item, Order, OrderItem, Warehouse, Inventory, InventoryItem, OutOfStockItem

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from bson import ObjectId
from django.http import HttpResponse

from . import email_parse_util


# Assuming this function is correctly getting MongoDB client and fetching data
def get_mongodb_client():
    # Return a MongoClient instance connected to your database
    pass


class ProductView(DetailView):
    model = Item
    template_name = "order_page.html"


@login_required
def OrderSummaryView(request):
    # current_user = request.user
    # user = get_object_or_404(User, username=current_user)
    user = Account.objects.get(username=request.user)
    order = Order.objects.filter(user=user)
    context = {
        'object': order
    }

    return render(request, 'order_summary.html', context)


@login_required
def OrderSummaryViewWithID(request, order_id):
    # current_user = request.user
    # user = get_object_or_404(User, username=current_user)
    order = Order.objects.filter(id=order_id)
    context = {
        'object': order
    }

    return render(request, 'order_summary.html', context)


@login_required
def add_to_cart(request, pk, quantity):
    item = get_object_or_404(Item, pk=pk)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
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
def add_item_order(request, *args, **kwargs):
    user_id = request.user.id

    user = Account.objects.get(id=user_id)
    payload = {}

    item_id = request.POST.get("item_id")
    quantity_str = request.POST.get("quantity")
    try:
        quantity = int(quantity_str)
    except ValueError:
        quantity = quantity_str

    item = Item.objects.get(pk=item_id)
    if item:
        order_item, created = OrderItem.objects.get_or_create(
            item=item,
            user=request.user,
            ordered=False
        )
        order = Order.objects.filter(user=request.user, ordered=False)
        if order.exists():
            order = order[0]

            if order.items.filter(item__pk=item.pk).exists():
                order_item.quantity += quantity
                order_item.save()
                payload['response'] = "Item added to your cart"
            else:
                order.items.add(order_item)
                order_item.quantity += quantity - 1
                order_item.save()
                payload['response'] = "Item added to your cart"
        else:
            ordered_date = timezone.now()
            order = Order.objects.create(user=request.user, ordered_date=ordered_date)
            order.item.add(item)
            order_item.quantity += quantity - 1
            order_item.save()
            payload['response'] = "Item added to your cart"
    else:
        payload['response'] = "Could not find request"
    return redirect("ops:order-form")


@login_required
def remove_from_cart(request, pk):
    item = get_object_or_404(Item, pk=pk)
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
            messages.info(request, "Item \"" + order_item.item.item_name + "\" remove from order")
            return redirect("order-summary")
        else:
            messages.info(request, "This Item is not in your order")
            return redirect("product", pk=pk)
    else:
        # add message doesnt have order
        messages.info(request, "You do not have an Order")
        return redirect("product", pk=pk)


@login_required
def reduce_quantity_item(request, pk):
    item = get_object_or_404(Item, pk=pk)
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
        # add message doesnt have order
        messages.info(request, "You do not have an Order")
        return redirect("order-summary")


class orderForm(ListView):
    model = Item
    template_name = "order_form2.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = ItemFilter(self.request.GET, queryset=self.get_queryset())
        return context


@login_required
def ItemData(request, item_id):
    item = Item.objects.get(id=item_id)

    return render(request, "item_data.html", {'item': item})


def WarehouseDateItemView(request, warehouse_id):
    warehouse = Warehouse.objects.get(id=warehouse_id)
    inventory = Inventory.objects.filter(warehouse=warehouse).latest('date')
    inv_items = inventory.items.all()
    items = Item.objects.filter(Q(item_type='G') | Q(item_type='W'))

    return render(request, "warehouse_dates.html", {'items': inv_items, 'warehouse': warehouse})


@login_required
def WarehouseDateItemForm(request, item_id):
    item = Item.objects.get(id=item_id)
    items = Item.objects.filter(Q(item_type='G') | Q(item_type='W'))
    last_item = items.last()
    form = WarehouseForm()
    if item.pk is last_item.pk:
        return render(request, "warehouse_dates.html", {'items': items})
    return render(request, "item_date_form.html", {'item': item, 'form': form})


@login_required
def WarehouseDateItemInput(request, item_id, inventory_id):
    inventory = Inventory.objects.get(id=inventory_id)
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = WarehouseForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            date = form.cleaned_data['Date']
            amount = form.cleaned_data['Amount']

            item = Item.objects.get(id=item_id)

            add_item, created = InventoryItem.objects.get_or_create(
                item=item,
                total_quantity=amount,
                item_date=date,
            )

            inventory.items.add(add_item)
            inventory.save()

            items = Item.objects.filter(Q(item_type='G') | Q(item_type='W'))
            last_item = items.last()
            item = Item.objects.get(id=item_id + 1)
            if item.pk is last_item.pk:
                return render(request, "warehouse_dates.html", {'items': items})
            return render(request, "item_date_form.html", {'form': form, 'item': item, 'inventory': inventory})

    # if a GET (or any other method) we'll create a blank form
    else:
        form = WarehouseForm()

    return render(request, 'item_date_form.html', {'form': form, 'inventory': inventory})


@login_required
def WarehouseDateForm(request, warehouse_id):
    items = Item.objects.all()

    warehouse = Warehouse.objects.get(id=warehouse_id)
    inventory = Inventory.objects.filter(warehouse=warehouse).latest('date')
    inv_items = inventory.items.all()

    for item in inv_items:
        item.item_date = None
        item.save()

    item = items.first()
    form = WarehouseForm()

    return render(request, 'item_date_form.html', {'form': form, 'item': item, 'inventory': inventory})


@login_required
def WarehouseDateFormSkip(request, item_id, inventory_id):
    inventory = Inventory.objects.get(id=inventory_id)
    item = Item.objects.get(id=item_id + 1)
    form = WarehouseForm()

    items = Item.objects.filter(Q(item_type='G') | Q(item_type='W'))
    last_item = items.last()

    if item.pk is last_item.pk:
        return render(request, "warehouse_dates.html", {'items': items, 'inventory': inventory})

    return render(request, "item_date_form.html", {'form': form, 'item': item, 'inventory': inventory})


def WarehouseDashboard(request):
    warehouses = Warehouse.objects.all()

    return render(request, 'warehouse_dashboard.html', {'warehouses': warehouses})


def WarehouseDetail(request, warehouse_id):
    warehouse = Warehouse.objects.get(id=warehouse_id)
    routes = warehouse.routes.all()

    return render(request, 'warehouse_detail.html', {'warehouse': warehouse, 'routes': routes})


import io
from django.http import FileResponse
from reportlab.pdfgen import canvas


def PalletPages(request, route_id):
    if request.method == 'POST':
        RT = rsr.models.Route.objects.get(id=route_id)
        RTnum = RT.number

        if request.method == 'POST':
            # Instanciate the form with posted data

            pages = int(request.POST.get('pallets'))
            # Create a file-like buffer to receive PDF data.
            buffer = io.BytesIO()

            # Create the PDF object, using the buffer as its "file."
            p = canvas.Canvas(buffer)
            p.setTitle(f"RT{RTnum}_pallet_pages")
            # Draw things on the PDF. Here's where the PDF generation happens.
            # See the ReportLab documentation for the full list of functionality.
            for page in range(pages):
                p.setFont("Helvetica", 100)
                p.drawString(150, 750, "RT " + RTnum.__str__(), )
                p.drawString(150, 150, f'{page + 1} of {pages}')
                p.showPage()
            # Close the PDF object cleanly, and we're done.

            p.save()

            # FileResponse sets the Content-Disposition header so that browsers
            # present the option to save the file.
            buffer.seek(0)
            return FileResponse(buffer, as_attachment=True, filename=f'RT{RTnum}_pallet_pages.pdf')
        else:  # The form is invalid return a json response
            return JsonResponse({"Error": "Form is invalid"}, status=400)
    else:
        return render(request, 'warehouse_print.html')
    # return render(request, 'pallet-pages.html', {'RTnum': RTnum, 'pages': pages})


def PrintPalletPages(request, warehouse_id):
    warehouse = Warehouse.objects.get(id=warehouse_id)
    routes = warehouse.routes.all()
    return render(request, 'warehouse_print.html', {'warehouse': warehouse, 'routes': routes})


@login_required
def WarehousePhysicalInventory(request, item_id):
    return render(request, 'item_date_form.html', {'form': form})


@login_required
def WarehouseManagerDetail(request, warehouse_id):
    warehouse = Warehouse.objects.get(id=warehouse_id)
    routes = warehouse.routes.all()
    user = request.user
    orders = Order.objects.all()

    return render(request, 'warehouse_manager_detail.html',
                  {'warehouse': warehouse, 'routes': routes, 'user': user, 'orders': orders})


def WarehouseManagerOrderStatusUpdate(request, order_id):
    order = Order.objects.get(id=order_id)

    if request.method == 'POST':
        # Access form input data
        order_status = request.POST.get('orderStatus')
        quantity = request.POST.get('quantity')
        order.status = order_status
        order.save()

    return WarehouseManagerOrderStatusDetail(request, order_id)


def WarehouseManagerOrderStatusView(request):
    orders = Order.objects.all()

    return render(request, 'OrderStatusView.html', {'orders': orders})


def WarehouseManagerOrderStatusDetail(request, order_id):
    order = Order.objects.get(id=order_id)

    return render(request, 'OrderStatusDetail.html', {'order': order})


from django.shortcuts import render

def orders_view(request):

    email = "GJTat901@gmail.com"
    password = "xnva kbzm flsa szzo"
    uri = "mongodb+srv://gjtat901:koxbi2-kijbas-qoQzad@cluster0.abxr6po.mongodb.net/?retryWrites=true&w=majority"
    client = MongoClient(uri)

    email_parse_util.check_and_parse_new_emails(email, password, client, 'mydatabase', 'orders')

    uri = "mongodb+srv://gjtat901:koxbi2-kijbas-qoQzad@cluster0.abxr6po.mongodb.net/?retryWrites=true&w=majority"
    client = MongoClient(uri)
    db = client['mydatabase']
    collection = db['orders']

    orders = list(collection.find())

    # Renaming '_id' field to 'order_id' for each order
    for order in orders:
        order['order_id'] = str(order['_id'])  # Convert ObjectId to string
        del order['_id']

    orders.reverse()

    # You can now pass these orders to your template or process them further
    return render(request, 'mongoOrdersInOrder.html', {'orders': orders})

from pymongo import MongoClient
from bson.objectid import ObjectId
from django.http import HttpResponse
from django.shortcuts import render

def complete_order(request, order_id):
    try:
        uri = "mongodb+srv://gjtat901:koxbi2-kijbas-qoQzad@cluster0.abxr6po.mongodb.net/?retryWrites=true&w=majority"
        client = MongoClient(uri)
        db = client['mydatabase']
        collection = db['orders']

        # Update the order's status to "Complete"
        result = collection.update_one(
            {'_id': ObjectId(order_id)},
            {'$set': {'status': "Complete"}}
        )

        # Check if the order was successfully updated
        if result.matched_count == 0:
            # No order was found with the provided ID
            print("No order found with the specified ID.")
            client.close()
            return HttpResponse("Order not found", status=404)

        # Retrieve the updated order for rendering
        order = collection.find_one({'_id': ObjectId(order_id)})
    except Exception as e:
        print(f"An error occurred: {e}")
        client.close()
        return HttpResponse("Error connecting to database", status=500)

    client.close()
    return render(request, 'order_detail.html', {'order': order})


def order_detail_view(request, order_id):
    # Directly create a MongoDB client instance
    try:
        uri = "mongodb+srv://gjtat901:koxbi2-kijbas-qoQzad@cluster0.abxr6po.mongodb.net/?retryWrites=true&w=majority"
        client = MongoClient(uri)
        db = client['mydatabase']
        collection = db['orders']
        order = collection.find_one({'_id': ObjectId(order_id)})
    except Exception as e:
        print(f"An error occurred: {e}")
        # Optionally, return an error response or handle the error as appropriate
        return HttpResponse("Error connecting to database", status=500)

    collection = db['orders']

    order = collection.find_one({'_id': ObjectId(order_id)})

    #Fetch OOS
    OOS_items = OutOfStockItem.objects.all().values_list('item_number', flat=True)
    OOS = list(OOS_items)

    # Reformat the orders array and check stock status
    if order and 'orders' in order:
        reformatted_orders = []
        for item in order['orders']:
            item_number = item.get('Item Number', '')
            in_stock = item_number not in OOS

            reformatted_item = {
                'ItemNumber': item_number,
                'ItemDescription': item.get('Item Description', ''),
                'Quantity': item.get('Quantity', ''),
                'InStock': in_stock
            }
            reformatted_orders.append(reformatted_item)
        order['orders'] = reformatted_orders

    client.close()
    return render(request, 'order_detail.html', {'order': order})


def generate_order_pdf(request, order_id):
    uri = "mongodb+srv://gjtat901:koxbi2-kijbas-qoQzad@cluster0.abxr6po.mongodb.net/?retryWrites=true&w=majority"
    client = MongoClient(uri)
    db = client['mydatabase']
    collection = db['orders']

    #Fetch OOS
    OOS_items = OutOfStockItem.objects.all().values_list('item_number', flat=True)
    OOS = list(OOS_items)

    ship_to_routes = [
        "RTC000003", "RTC000013", "RTC000018", "RTC000019", "RTC000089",
        "RTC000377", "RTC000379", "RTC000649", "RTC000700", "RTC000719"
    ]


    order = collection.find_one({'_id': ObjectId(order_id)})
    client.close()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="order_{order_id}.pdf"'

    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    # Initialize totals
    total_quantity = 0
    adjusted_total_quantity = 0

    # Calculate totals
    for item in order.get('orders', []):
        quantity = int(item.get('Quantity', 0))
        total_quantity += quantity
        if item.get('Item Number', '') not in OOS:
            adjusted_total_quantity += quantity

    # Header setup with bold font
    # Set font to Helvetica-Bold for headers
    p.drawString(30, height - 30, "Pick List")
    p.setFont("Helvetica-Bold", 12)
    route_number = order.get('route', 'N/A')
    route_type = "Ship-to" if route_number in ship_to_routes else "Pick-up"
    p.drawString(30, height - 50, f"Route Number: {route_number} ({route_type})")
    p.setFont("Helvetica", 12)

    formatted_date = order.get('date', 'N/A').strftime('%m/%d/%Y') if order.get('date') else 'N/A'
    p.drawString(30, height - 70, f"Date: {formatted_date}")
    p.drawString(30, height - 90, f"Total Quantity Ordered: {total_quantity}")
    p.drawString(30, height - 110, f"Adjusted Total: {adjusted_total_quantity} +/- ")
    p.rect(160, height - 112, 25, 15)  # Scan count box
    p.drawString(30, height - 130, "Scan Count:")
    p.rect(110, height - 132, 50, 15)  # Scan count box



    # Starting position adjustment for item list
    y_position = height - 160

    p.setFont("Helvetica-Bold", 12)
    # Column headers
    p.drawString(30, y_position, "Item Number")
    p.drawString(150, y_position, "Description")
    p.drawString(350, y_position, "Quantity")
    p.drawString(450, y_position, "")  # Adjustment quantity column
    p.drawString(530, y_position, "Stock Status")
    p.drawString(630, y_position, "Check")  # Checkboxes moved to the far right

    # Revert to normal font for item details
    p.setFont("Helvetica", 12)

    # Adjust y_position for first item row
    y_position -= 20

    for item in order.get('orders', []):

        # Draw a line to separate this item from the next
        p.line(30, y_position - 2, 580, y_position - 2)  # Adjust line length as needed

        item_number = item.get('Item Number', 'Unknown')
        description = item.get('Item Description', 'N/A')
        quantity = item.get('Quantity', 0)
        stock_status = "IS" if item_number not in OOS else "OOS"

        # Drawing item details (keep this part unchanged)
        p.drawString(30, y_position, str(item_number))
        p.drawString(150, y_position, description)
        p.drawString(350, y_position, str(quantity))

        # If the item is out of stock, cross out the quantity
        if stock_status == "OOS":
            # Calculate width of the quantity text for precise line drawing
            quantity_text_width = p.stringWidth(str(quantity), "Helvetica", 12)
            # Draw a line through the quantity text
            p.line(350, y_position + 4, 350 + quantity_text_width, y_position + 4)

        # Draw the placeholder box for adjustment quantity, stock status, and checkbox
        p.rect(450, y_position - 2, 30, 15)  # Placeholder box for adjustment quantity
        p.drawString(530, y_position, stock_status)  # Include stock status
        p.rect(630, y_position - 2, 12, 12, stroke=1, fill=0)  # Checkbox

        # Move to the next line
        y_position -= 20

        # Check if we need to start a new page
        if y_position < 50:
            p.showPage()
            y_position = height - 50

    p.showPage()
    p.save()
    return response
