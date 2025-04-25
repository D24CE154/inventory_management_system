# pos/views.py
import json
from datetime import timedelta
from employees.views import is_active_employee
from xhtml2pdf import pisa
from django.db.models import Sum, Avg
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.forms import formset_factory
from .models import Sale, SaleItem, Customer, ProductItem
from .forms import SaleForm, SaleItemForm,SaleItemFormSet
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils.timezone import now
from django.core.files.storage import FileSystemStorage
from django.utils import timezone
from inventory.models import Product, ProductItem, ProductCategory

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
def create_sale(request):
    if request.method == 'POST':
        sale_form = SaleForm(request.POST)
        formset = SaleItemFormSet(request.POST)

        if sale_form.is_valid() and formset.is_valid():
            customer_name = sale_form.cleaned_data['customer_name']
            phone = sale_form.cleaned_data['phone']
            email = sale_form.cleaned_data['email']
            address = sale_form.cleaned_data['address']
            payment_method = sale_form.cleaned_data['payment_method']

            customer, _ = Customer.objects.get_or_create(
                phone=phone,
                defaults={
                    'name': customer_name,
                    'email': email,
                    'address': address
                }
            )

            sale = Sale.objects.create(customer_id=customer, payment_method=payment_method)

            total_amount = 0

            for form in formset:
                product = form.cleaned_data['product_id']
                quantity = form.cleaned_data['quantity']
                category = form.cleaned_data['product_category']
                imei = form.cleaned_data.get('imei')

                # Determine price
                if category == 'Electronics' and imei:
                    price = imei.price
                    imei.status = 'Sold'
                    imei.save()
                elif category == 'Accessories':
                    non_serialized_item = ProductItem.objects.filter(
                        product=product,
                        product_type='NonSerialized'
                    ).first()
                    if non_serialized_item:
                        price = non_serialized_item.price
                    else:
                        messages.error(request, f"No price found for accessory product: {product}")
                        sale.delete()  # Cleanup
                        return redirect('create_sale')
                else:
                    price = 0  # fallback

                total_amount += price * quantity

                # Create sale item
                sale_item = form.save(commit=False)
                sale_item.sale_id = sale
                sale_item.imei = imei if category == 'Electronics' else None
                sale_item.price = price
                sale_item.save()

                # Update product stock
                product.stock -= quantity
                product.save()

            # Update total amount
            sale.total_amount = total_amount
            sale.save()

            messages.success(request, f"Sale created successfully. Total amount: ₹{total_amount}")
            return redirect('sale_detail', sale_id=sale.sale_id)

        else:
            messages.error(request, "Please correct the errors below.")

    else:
        sale_form = SaleForm()
        formset = SaleItemFormSet()

    return render(request, 'create_sale.html', {
        'sale_form': sale_form,
        'formset': formset
    })

@csrf_exempt
def razorpay_callback(request):
    if request.method == 'POST':
        sale_data = request.session.get('sale_data')
        if not sale_data:
            return HttpResponse("Session expired or invalid", status=400)

        sale_form_data = sale_data['sale_form']
        sale_form = SaleForm(sale_form_data)
        formset_data = sale_data['formset']
        formset = [SaleItemForm(data) for data in formset_data]

        customer, _ = Customer.objects.get_or_create(
            customer_phone=sale_form_data['phone'],
            defaults={
                'customer_name': sale_form_data['customer_name'],
                'customer_address': sale_form_data['address']
            }
        )

        sale = Sale(
            employee_id=request.user.employee,
            customer_id=customer,
            payment_method='UPI',
            total_amount=sale_data['formset'][0]['product_id'].selling_price  # Placeholder, use correct sum
        )

        return finalize_sale(request, sale, formset, customer)

    return HttpResponse("Invalid request", status=400)

def finalize_sale(request, sale, formset, customer):
    sale.save()
    for form in formset:
        sale_item = form.save(commit=False)
        sale_item.sale_id = sale
        sale_item.save()

        if sale_item.imei:
            product_item = get_object_or_404(ProductItem, pk=sale_item.imei.pk)
            product_item.status = 'Sold'
            product_item.save()
        else:
            product = get_object_or_404(Product, pk=sale_item.product_id.pk)
            product.stock -= sale_item.quantity
            product.save()

    context = {
        'sale': sale,
        'sale_items': SaleItem.objects.filter(sale_id=sale),
        'customer': customer,
        'total': sale.total_amount,
        'payment_method': sale.payment_method
    }
    html_string = render_to_string('invoice_template.html', context)
    pdf_file = f'media/invoices/invoice_{sale.pk}.pdf'
    with open(pdf_file, 'wb') as output:
        pisa_status = pisa.CreatePDF(html_string, dest=output)
    sale.invoice_file = pdf_file
    sale.save()

    messages.success(request, 'Sale created successfully!')
    return redirect('salesExecutiveDashboard')

def salesExecutiveDashboard(request):
    if not is_active_employee(request.user):
        messages.error(request, 'You are not authorized to view this page.')
        return redirect('error_403_view')

    today = now().date()
    yesterday = today - timedelta(days=1)

    today_sales_count = Sale.objects.filter(sale_date__date=today).count()
    yesterday_sales_count = Sale.objects.filter(sale_date__date=yesterday).count()
    today_sales_change = 0

    if yesterday_sales_count > 0:
        today_sales_change = round(((yesterday_sales_count - today_sales_count)/yesterday_sales_count) * 100)

    today_revenue = Sale.objects.filter(sale_date__date=today).aggregate(total=Sum('total_amount'))['total'] or 0
    yesterday_revenue = Sale.objects.filter(sale_date__date=yesterday).aggregate(total=Sum('total_amount'))['total'] or 0

    today_revenue_change = 0
    if yesterday_revenue > 0:
        today_revenue_change = round(((today_revenue - yesterday_revenue)/yesterday_revenue) * 100)


    month_start = today.replace(day=1)
    monthly_target = 150000
    monthly_sales = Sale.objects.filter(sale_date__date__gte=month_start,
                                        sale_date__lte=today).aggregate(total=Sum('total_amount'))['total'] or 0

    if monthly_sales > 0:
        monthly_target_percentage = round(((monthly_target - monthly_sales)/monthly_target) * 100)
    else:
        monthly_target_percentage = 0

    avg_order_value = Sale.objects.filter(sale_date__date=today).aggregate(avg = Avg('total_amount'))['avg'] or 0
    last_month = today.replace(day=1) - timedelta(days=1)
    last_month_start = last_month.replace(day=1)
    last_month_avg = Sale.objects.filter(sale_date__date__gte=last_month_start,
                                         sale_date__date__lte=last_month).aggregate(avg=Avg('total_amount'))['avg'] or 0

    avg_change = 0
    if last_month_avg > 0:
        avg_change = round(((avg_order_value-last_month_avg)/last_month_avg) * 100)


    recent_sales = Sale.objects.select_related('customer_id').order_by('-sale_date')[:5]

    sales_data = {
        'daily':{
            'labels' : [(today - timedelta(days=i)).strftime('%a') for i in range(6,-1,-1)],
            'values' : [Sale.objects.filter(sale_date__date=(today - timedelta(days=i))).aggregate(total=Sum('total_amount'))['total'] or 0 for i in range(6,-1,-1)],
        }
    }

    top_products_today = (SaleItem.objects.filter(sale_id__sale_date__date=today)
                          .values('product_id__product_name')
                          .annotate(units=Sum('quantity'))
                          .order_by('-units')[:5])

    top_products_data = {
        'today': {
            'labels': [item['product_id__product_name'] for item in top_products_today],
            'values': [item['units'] for item in top_products_today]
        }
    }

    context = {
        'today_sales_count' : today_sales_count,
        'today_sales_change' : today_sales_change,
        'today_revenue' : today_revenue,
        'today_revenue_change' : today_revenue_change,
        'monthly_target' : monthly_target,
        'monthly_target_percentage' : monthly_target_percentage,
        'monthly_sales' : monthly_sales,
        'avg_order_value' : avg_order_value,
        'avg_change' : avg_change,
        'recent_sales' : recent_sales,
        'sales_data' : json.dumps(sales_data),
        'top_products_today' : json.dumps(top_products_data),
        'employee' : request.user.employee,
    }


    return render(request,'SalesDashboard.html',context=context)

# pos/views.py
from django.http import JsonResponse

@login_required
def product_search(request):
    if 'term' in request.GET:
        qs = Product.objects.filter(product_name__icontains=request.GET.get('term'))
        products = list(qs.values('id', 'product_name', 'stock'))
        return JsonResponse(products, safe=False)
    return JsonResponse([], safe=False)