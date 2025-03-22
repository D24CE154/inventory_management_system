# pos/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Avg, F, ExpressionWrapper, DecimalField
from django.utils.timezone import now
import json
from datetime import datetime, timedelta
from employees.models import Employee
from employees.views import is_active_employee
from pos.models import Sale, SaleItem, Customer
from inventory.models import Product



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




