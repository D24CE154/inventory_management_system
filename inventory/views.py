from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from django.db.models import Sum, Count, F, DecimalField, ExpressionWrapper, Q
import json
from .forms import CategoryForm
from datetime import datetime,timedelta
from employees.models import Employee,AuditLog
from pos.models import Sale, SaleItem, Customer
from inventory.models import Product, ProductItems,ProductCategory,NonSerializedProducts


def is_active_inventory_manager(user):
    if user.is_authenticated and (user.employee.role == 'Admin' or user.employee.role == 'Inventory Manager') and user.employee.is_active:
        return True
    return False
def inventoryManagerDashboard(request):
    if not is_active_inventory_manager(request.user):
        messages.error(request, "You don't have permission to access this page.")
        return redirect("error_403_view")

    product_count = Product.objects.count()
    low_Stock_count = Product.objects.filter(stock__lte=5).count()
    out_of_Stock_count = Product.objects.filter(stock__gt=0).count()

    inventory_value = ProductItems.objects.filter(status='Available').aggregate(value = Sum('price'))['value'] or 0

    low_stock_products = Product.objects.filter(stock__lte=5).order_by('stock')[:10]
    out_of_stock_products = Product.objects.filter(stock=0).order_by('stock')[:10]

    low_stock_data = []
    for product in low_stock_products:
        low_stock_data.append({
            'id': product.product_id,
            'name': product.product_name,
            'curren_stock' : product.stock,
            'reorder_level': 5,
        })

    categories = ProductCategory.objects.all()
    stock_by_category = []
    for category in categories:
        products = Product.objects.filter(category=category)
        total_stock = products.aggregate(Sum('stock'))['total'] or 0
        stock_by_category.append({
            'category_id': category.category_id,
            "category_name" : category.category_name,
            'stock' : total_stock
        })

    today = datetime.now()
    turnover_data = {
        '30days':{
            'labels': [(today - timedelta(days=i * 7)).strftime('%b.%d') for i in range(4,0,-1)],
            'fast_moving': [14,16,19,21],
            'slow_moving': [4,5,3,2]
        }
    }

    context = {
        'product_count': product_count,
        'low_Stock_count' : low_Stock_count,
        'out_of_Stock_count' : out_of_Stock_count,
        'inventory_value' : inventory_value,
        'low_stock_products' : low_stock_products,
        'stock-by-category' : json.dumps(stock_by_category),
        'turnover-data' : json.dumps(turnover_data),
        'employee' : Employee.objects.get(employee_id=request.user.employee.employee_id)
    }

    return render(request,'InventoryManagerDashboard.html',context)

@login_required(login_url='login')
def category_list(request):
    categories = ProductCategory.objects.annotate(
        product_count=Count('product', distinct=True),
        stock_value=Sum('product__productitems__price', distinct=True,
                        filter=Q(product__productitems__status='Available'))
    ).order_by('category_name')

    context = {
        'categories': categories,
        'logged_in_employee': request.user.employee
    }
    return render(request, 'category_list.html', context)

@login_required(login_url='login')
def add_category(request):
    if not (request.user.employee.role == 'Admin' or request.user.employee.role == 'Inventory Manager'):
        messages.error(request, "You don't have permission to access this page.")
        return redirect("error_403_view")

    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, f"Category {category.category_name} added successfully.")
            return redirect("category_list")
    else:
        form = CategoryForm()

    context = {
        'form': form,
        'logged_in_employee': request.user.employee
    }
    return render(request, 'add_category.html', context)

@login_required(login_url='login')
def edit_category(request, category_id):
    if not is_active_inventory_manager(request.user):
        messages.error(request, "You don't have permission to access this page.")
        return redirect("error_403_view")

    category = get_object_or_404(ProductCategory, category_id=category_id)

    if request.method == 'POST':
        editCategoryForm = CategoryForm(request.POST, instance=category)
        if editCategoryForm.is_valid():
            category = editCategoryForm.save()
            messages.success(request, f"Category {category.category_name} updated successfully.")
            return redirect("category_list")
    else:
        editCategoryForm = CategoryForm(instance=category)

    context = {
        'form': editCategoryForm,
        'logged_in_employee': request.user.employee,
        'category': category
    }
    return render(request, 'edit_category.html', context)

@login_required(login_url='login')
def delete_category(request,category_id):

    if not is_active_inventory_manager(request.user):
        messages.error(request, "You don't have permission to access this page.")
        return redirect("error_403_view")

    category = get_object_or_404(ProductCategory, category_id = category_id)

    if Product.objects.filter(category_id=category_id).exists():
        messages.error(request, f"Cannot delete '{category.category_name}' as it has associated products.")
        return redirect('category_list')

    category_name = category.category_name
    category.delete()
    messages.success(request,f"Category {category_name} deleted successfully.")
    return redirect('category_list')
