# pos/views.py
import json
from datetime import timedelta
from decimal import Decimal
from io import BytesIO

import razorpay
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.core.mail import EmailMessage
from django.db import transaction
from django.db.models import Sum, Avg
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import get_template
from django.utils.timezone import now
from xhtml2pdf import pisa

from employees.views import is_active_employee
from .forms import CustomerForm
from .models import Sale, SaleItem, Customer, Product, ProductCategory, ProductItem


@login_required  # Ensure login is required
def salesExecutiveDashboard(request):
    # Check if the user is an active employee and authorized
    if not hasattr(request.user, 'employee') or not is_active_employee(request.user):
        messages.error(request, 'You are not authorized to view this page.')
        # Redirect to a generic error page or login page
        return redirect('login')  # Or an appropriate error view name

    today = now().date()
    yesterday = today - timedelta(days=1)

    # --- Today's Sales Count & Change ---
    today_sales_count = Sale.objects.filter(sale_date__date=today).count()
    yesterday_sales_count = Sale.objects.filter(sale_date__date=yesterday).count()
    today_sales_change = 0
    if yesterday_sales_count > 0:
        # Calculate percentage change
        today_sales_change = round(((today_sales_count - yesterday_sales_count) / yesterday_sales_count) * 100)

    # --- Today's Revenue & Change ---
    today_revenue = Sale.objects.filter(sale_date__date=today).aggregate(total=Sum('total_amount'))['total'] or Decimal(
        '0.00')
    yesterday_revenue = Sale.objects.filter(sale_date__date=yesterday).aggregate(total=Sum('total_amount'))[
                            'total'] or Decimal('0.00')
    today_revenue_change = 0
    if yesterday_revenue > 0:
        today_revenue_change = round(((today_revenue - yesterday_revenue) / yesterday_revenue) * 100)

    # --- Monthly Target Progress ---
    month_start = today.replace(day=1)
    # Consider making the target dynamic (e.g., from settings or employee model)
    monthly_target = Decimal('150000.00')
    monthly_sales = Sale.objects.filter(sale_date__date__gte=month_start, sale_date__date__lte=today).aggregate(
        total=Sum('total_amount'))['total'] or Decimal('0.00')
    monthly_target_percentage = 0
    if monthly_target > 0:
        # Calculate percentage achieved
        monthly_target_percentage = round((monthly_sales / monthly_target) * 100)

    # --- Average Order Value & Change ---
    avg_order_value = Sale.objects.filter(sale_date__date=today).aggregate(avg=Avg('total_amount'))['avg'] or Decimal(
        '0.00')
    # Calculate last month's average
    last_month_end = month_start - timedelta(days=1)
    last_month_start = last_month_end.replace(day=1)
    last_month_avg = \
    Sale.objects.filter(sale_date__date__gte=last_month_start, sale_date__date__lte=last_month_end).aggregate(
        avg=Avg('total_amount'))['avg'] or Decimal('0.00')
    avg_change = 0
    if last_month_avg > 0:
        avg_change = round(((avg_order_value - last_month_avg) / last_month_avg) * 100)

    # --- Recent Sales ---
    # Use select_related for efficiency
    recent_sales = Sale.objects.select_related('customer_id').order_by('-sale_date')[:5]

    # --- Sales Performance Chart Data (Last 7 Days) ---
    sales_performance_labels = []
    sales_performance_values = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        daily_total = Sale.objects.filter(sale_date__date=day).aggregate(total=Sum('total_amount'))['total'] or 0
        sales_performance_labels.append(day.strftime('%a'))  # Short day name (e.g., Mon)
        sales_performance_values.append(float(daily_total))  # Ensure float for JSON

    sales_data = {
        'daily': {
            'labels': sales_performance_labels,
            'values': sales_performance_values,
        }
        # Add weekly/monthly data fetching logic here if needed
    }

    # --- Top Products Chart Data (Today) ---
    # Corrected field lookup: product_id__name
    top_products_today_query = (SaleItem.objects.filter(sale_id__sale_date__date=today)
                                .values('product_id__name')  # Use 'name' from Product model
                                .annotate(units=Sum('quantity'))
                                .order_by('-units')[:5])

    top_products_data = {
        'today': {
            # Corrected key: product_id__name
            'labels': [item['product_id__name'] for item in top_products_today_query],
            'values': [item['units'] for item in top_products_today_query]
        }
        # Add week/month data fetching logic here if needed
    }

    context = {
        'today_sales_count': today_sales_count,
        'today_sales_change': today_sales_change,
        'today_revenue': today_revenue,
        'today_revenue_change': today_revenue_change,
        'monthly_target': monthly_target,
        'monthly_target_percentage': monthly_target_percentage,
        'monthly_sales': monthly_sales,
        'avg_order_value': avg_order_value,
        'avg_change': avg_change,
        'recent_sales': recent_sales,
        'sales_data': json.dumps(sales_data),
        'top_products_today': json.dumps(top_products_data),
        # Pass the employee object correctly for the template include
        'logged_in_employee': request.user.employee,
    }

    return render(request, 'SalesDashboard.html', context=context)


client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


@login_required
def create_sale(request):
    categories = ProductCategory.objects.all()
    if request.method == "POST":
        customer_data = {
            "customer_name": request.POST.get("customer_name"),
            "customer_address": request.POST.get("customer_address"),
            "customer_phone": request.POST.get("customer_phone"),
            "customer_email": request.POST.get("customer_email")
        }
        customer, _ = Customer.objects.get_or_create(customer_phone=customer_data["customer_phone"],
                                                     defaults=customer_data)
        sale = Sale.objects.create(
            employee_id=request.user.employee,
            customer_id=customer,
            total_amount=0,
            payment_method=request.POST.get("paymentMethod")
        )
        products = json.loads(request.POST.get("products", "[]"))
        total = 0
        with transaction.atomic():
            for item in products:
                product = Product.objects.get(pk=item["productId"])
                if "imei" in item:
                    product_item = ProductItem.objects.select_for_update().get(
                        serial_number=item["imei"], is_sold=False
                    )
                    selling_price = product_item.sale_price
                    quantity = 1
                    product_item.is_sold = True
                    product_item.save()
                    sale_item = SaleItem.objects.create(
                        sale_id=sale,
                        product_id=product,
                        imei=product_item,
                        quantity=quantity,
                        selling_price=selling_price
                    )
                else:
                    quantity = int(item["quantity"])
                    available_items = ProductItem.objects.select_for_update().filter(
                        product_id=product,
                        item_type=ProductItem.NON_SERIAL,
                        is_sold=False
                    )
                    # Assume check_stock already confirmed sufficient quantity.
                    available_total = available_items.aggregate(
                        total=Sum("quantity")
                    )["total"] or 0
                    if available_total < quantity:
                        messages.error(request, "Insufficient stock for product.")
                        return redirect("create_sale")
                    # Use sale_price from the first available item.
                    selling_price = available_items.first().sale_price
                    qty_needed = quantity
                    for available in available_items:
                        qty_to_sell = min(available.quantity, qty_needed)
                        available.quantity -= qty_to_sell
                        if available.quantity == 0:
                            available.is_sold = True
                        available.save()
                        qty_needed -= qty_to_sell
                        if qty_needed == 0:
                            break
                    sale_item = SaleItem.objects.create(
                        sale_id=sale,
                        product_id=product,
                        quantity=quantity,
                        selling_price=selling_price
                    )
                total += float(sale_item.selling_price) * sale_item.quantity
            sale.total_amount = total
            sale.save()
        request.session["sale_invoice_email"] = customer.customer_email
        return redirect("generate_invoice", sale_id=sale.sale_id)
    context = {"categories": categories, "logged_in_employee": request.user.employee}
    return render(request, "create_sale.html", context)


@login_required
def fetch_products_by_category(request, category_id):
    products = Product.objects.filter(category_id=category_id)
    product_data = []
    is_accessories = ProductCategory.objects.filter(id=category_id, name__iexact="Accessories").exists()

    for product in products:
        has_imei = not is_accessories
        stock_count = ProductItem.objects.filter(product_id=product.id).count()
        product_item = ProductItem.objects.filter(product_id=product.id).first()
        price = product_item.sale_price if product_item else 0
        product_data.append({
            "id": product.id,
            "name": product.name,
            "has_imei": has_imei,
            "stock": stock_count,
            "price": price,
        })

    return JsonResponse({"products": product_data})


@login_required
def add_customer(request):
    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save()
            # Ensure this block is indented correctly (e.g., 8 spaces)
            return JsonResponse({"status": "success",
                                 "customer": {"id": customer.customer_id, "customer_name": customer.customer_name}})
        else:
            # Ensure this block is indented correctly (e.g., 8 spaces)
            return JsonResponse({"status": "error", "message": "Invalid form data."})


@login_required
def fetch_product_by_imei(request):
    imei = request.GET.get("imei")
    if not imei:
        return JsonResponse({"success": False, "error": "IMEI parameter is missing."})

    try:
        # Fetch the specific unsold, serialized item by its serial number
        product_item = ProductItem.objects.select_related('product').get(
            serial_number=imei,
            item_type=ProductItem.SERIALIZED,
            is_sold=False
        )
        # Get the related product
        product = product_item.product

        return JsonResponse({
            "success": True,
            "product": {
                "id": product.id,
                "name": product.name,
                "imei": product_item.serial_number,  # Use the item's serial number
                "sale_price": float(product_item.sale_price)  # Use the item's sale price
            }
        })
    except ProductItem.DoesNotExist:
        # Handle case where no matching unsold, serialized item is found
        return JsonResponse({"success": False, "error": "Invalid IMEI or Product not found/already sold."})
    except Exception as e:
        return JsonResponse({"success": False, "error": "An unexpected error occurred while fetching product details."})


@login_required
def check_stock(request):
    product_id = request.GET.get("product_id")
    quantity_str = request.GET.get("quantity")

    # Basic validation for quantity
    if not quantity_str or not quantity_str.isdigit():
        return JsonResponse({"success": False, "error": "Invalid quantity provided."})

    quantity = int(quantity_str)
    if quantity <= 0:
        return JsonResponse({"success": False, "error": "Quantity must be greater than zero."})

    try:
        # Find all non-serialized, unsold items for this product ID
        available_items = ProductItem.objects.filter(
            product_id=product_id,
            item_type=ProductItem.NON_SERIAL,
            is_sold=False
        )

        # Calculate total available quantity by summing quantities
        total_stock = available_items.aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
        # print(f"Checking stock for Product ID: {product_id}, Requested: {quantity}, Available: {total_stock}") # Optional debug

        # Check if total stock is enough
        if total_stock >= quantity:
            # Get the price from the first available item (assuming price is consistent)
            first_item = available_items.first()
            if first_item:
                return JsonResponse({
                    "success": True,
                    "price": float(first_item.sale_price)
                })
            else:
                return JsonResponse({"success": False, "error": "Not enough stock available."})
        else:
            return JsonResponse({"success": False, "error": "Not enough stock available."})

    except Exception as e:
        # Catch other potential errors during query or processing
        print(f"Error in check_stock for product_id {product_id}: {e}")  # Log the specific error
        return JsonResponse({"success": False, "error": "An unexpected error occurred while checking stock."})


def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    # Ensure UTF-8 encoding for pisaDocument
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result, encoding='UTF-8')
    if not pdf.err:
        return result.getvalue()
    # Log error if PDF generation fails
    print(f"PDF generation error: {pdf.err}")
    return None


@login_required
def generate_invoice(request, sale_id):
    sale = get_object_or_404(Sale, pk=sale_id)
    sale_items = SaleItem.objects.select_related('product_id', 'imei').filter(sale_id=sale)
    discount = request.session.pop("sale_discount", 0)
    customer_email = request.session.pop("sale_invoice_email", None)

    context = {"sale": sale, "sale_items": sale_items, "discount": discount}

    pdf = render_to_pdf("invoice_template.html", context)
    if pdf:
        invoice_filename = f"Invoice_{sale.sale_id}.pdf"
        if not sale.invoice_file:
            sale.invoice_file.save(invoice_filename, ContentFile(pdf), save=True)

        if customer_email:
            try:
                subject = f"Your Invoice #{sale.sale_id} from IG Mobile"
                message = "Thank you for your purchase! Please find your invoice attached."
                email = EmailMessage(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [customer_email]
                )
                email.attach(invoice_filename, pdf, "application/pdf")
                email.send(fail_silently=False)
            except Exception as e:
                print(f"Failed to send invoice email to {customer_email} for sale {sale.sale_id}: {e}")
                messages.warning(request, f"Invoice generated, but failed to send email to {customer_email}.")

        response = HttpResponse(pdf, content_type="application/pdf")
        response["Content-Disposition"] = f'inline; filename="{invoice_filename}"'
        return response
    else:
        messages.error(request, "Failed to generate the invoice PDF.")
        return redirect("salesExecutiveDashboard")


@login_required
def sales_history(request):
    sales = Sale.objects.select_related('customer_id', 'employee_id').order_by('-sale_date')
    return render(request, 'sales_history.html', {
        'sales': sales,
        'employee': request.user.employee
    })


@login_required
def customer_list(request):
    customers = Customer.objects.all()
    return render(request, 'customers.html', {
        'customers': customers,
        'employee': request.user.employee,
    })
