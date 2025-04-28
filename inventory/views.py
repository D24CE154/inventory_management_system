# inventory/views.py
import json
from datetime import timedelta
from django.utils.timezone import now
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, F, Value, Q
from django.db.models.functions import Coalesce
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from decimal import Decimal

from employees.models import AuditLog, Employee
from .forms import ProductForm, ProductItemForm, CategoryForm, BrandForm, CATEGORY_SPEC_FIELDS
from .models import ProductCategory, Brand, Product, ProductItem


def is_active_inventory_manager(user):
    if user.is_authenticated and (
            user.employee.role == 'Admin' or user.employee.role == 'Inventory Manager') and user.employee.is_active:
        return True
    return False


@login_required(login_url='login')
def inventoryManagerDashboard(request):
    # Authorization check
    if not is_active_inventory_manager(request.user):
        messages.error(request, 'You are not authorized to view this page.')
        return redirect('login') # Or an appropriate error/dashboard page

    # --- Key Metrics ---
    # Total distinct products
    product_count = Product.objects.count()

    # Low Stock Items (Example: quantity > 0 and < 5, assuming no reorder_level)
    # Adjust the threshold (5) as needed or use a reorder_level field if available
    low_stock_threshold = 5
    low_stock_count = ProductItem.objects.filter(
        is_sold=False,
        quantity__gt=0,
        quantity__lt=low_stock_threshold
    ).values('product').distinct().count() # Count distinct products with low stock items

    # Out of Stock Items (quantity = 0)
    out_of_stock_count = ProductItem.objects.filter(
        is_sold=False,
        quantity=0
    ).values('product').distinct().count() # Count distinct products with out-of-stock items

    # Inventory Value (Sum of cost_price * quantity for non-sold items)
    inventory_value = ProductItem.objects.filter(is_sold=False).aggregate(
        total_value=Coalesce(Sum(F('cost_price') * F('quantity')), Decimal('0.00'))
    )['total_value']

    # --- Chart Data ---
    # Stock Levels by Category (Sum quantity for non-sold items per category)
    stock_by_category_query = ProductCategory.objects.annotate(
        stock=Coalesce(Sum('product__items__quantity', filter=Q(product__items__is_sold=False)), 0)
    ).values('name', 'stock').order_by('-stock')

    stock_by_category_data = list(stock_by_category_query)

    # Product Turnover Rate (Placeholder - Requires Sales Data Integration)
    # This part needs significant logic based on how sales are tracked and linked to inventory.
    # For now, we provide a default structure for the initial load.
    # The actual data fetching for different periods will be handled via AJAX.
    turnover_data = {
        '30days': {
            'labels': ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
            'fast_moving': [0] * 4, # Placeholder
            'slow_moving': [0] * 4  # Placeholder
        }
        # Add '90days' and 'year' placeholders if needed for initial load,
        # otherwise they will be fetched via AJAX.
    }

    # --- Table Data ---
    # Low Stock Products (Top 5, matching the low_stock_count logic)
    low_stock_products = Product.objects.annotate(
        current_stock=Coalesce(Sum('items__quantity', filter=Q(items__is_sold=False)), 0)
    ).filter(
        current_stock__gt=0,
        current_stock__lt=low_stock_threshold
        # Add filter for reorder_level if available: F('current_stock') <= F('reorder_level')
    ).order_by('current_stock')[:5]
    # Add reorder_level to each product if the field exists
    # for p in low_stock_products: p.reorder_level = p.reorder_level # Assuming field exists

    # Recent Purchase Orders (Top 5 - Requires PurchaseOrder model)
    recent_purchase_orders = []
    # try:
    #     # Replace 'PurchaseOrder' with your actual model name and app
    #     # Ensure 'supplier', 'order_date', 'status' fields exist
    #     recent_purchase_orders = PurchaseOrder.objects.select_related('supplier').order_by('-order_date')[:5]
    # except NameError: # Handle case where PurchaseOrder model isn't imported/doesn't exist
    #     print("PurchaseOrder model not found or not imported. Skipping recent purchase orders.")
    #     pass # Keep the list empty

    context = {
        'logged_in_employee': request.user.employee,
        'product_count': product_count,
        'low_stock_count': low_stock_count,
        'out_of_stock_count': out_of_stock_count,
        'inventory_value': inventory_value,
        'stock_by_category': json.dumps(stock_by_category_data),
        'turnover_data': json.dumps(turnover_data), # Initial data for turnover
        'low_stock_products': low_stock_products,
        'recent_purchase_orders': recent_purchase_orders,
    }
    return render(request, 'InventoryManagerDashboard.html', context)


# --- API View for Turnover Data (Needs to be added to urls.py) ---
@login_required
def get_turnover_data(request):
    if not is_active_inventory_manager(request.user):
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    period = request.GET.get('period', '30days') # Default to 30days

    # --- !!! Placeholder Logic for Turnover Calculation !!! ---
    # Replace this with actual calculation based on sales data and inventory levels
    # for the requested period ('30days', '90days', 'year').
    # This likely involves querying SaleItem, linking back to Product/ProductItem,
    # calculating COGS and average inventory value for the period.
    data = {}
    if period == '30days':
        data = {
            'labels': ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
            'fast_moving': [15, 18, 20, 22], # Example data
            'slow_moving': [5, 4, 6, 3]      # Example data
        }
    elif period == '90days':
        data = {
            'labels': ['Month 1', 'Month 2', 'Month 3'],
            'fast_moving': [50, 55, 60], # Example data
            'slow_moving': [15, 12, 18]   # Example data
        }
    elif period == 'year':
        data = {
            'labels': ['Q1', 'Q2', 'Q3', 'Q4'], # Example labels
            'fast_moving': [200, 220, 210, 230], # Example data
            'slow_moving': [50, 45, 55, 48]      # Example data
        }
    else:
        return JsonResponse({'error': 'Invalid period specified'}, status=400)

    return JsonResponse(data)


@login_required
def category_list(request):
    search_query = request.GET.get('search', '').strip()
    categories = ProductCategory.objects.all()
    if search_query:
        filtered = categories.filter(name__icontains=search_query)
        if not filtered.exists():
            messages.info(request, "No results found. Displaying all categories.")
        else:
            categories = filtered
    return render(request, 'category_list.html', {
        'categories': categories,
        'logged_in_employee': request.user.employee
    })

@login_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            AuditLog.objects.create(
                employee=request.user.employee,
                action=f'Created Category: {form.cleaned_data["name"]}')

            messages.success(request, 'Category created successfully.')
            return redirect('category_list')
    else:
        form = CategoryForm()
    return render(request, 'category_form.html', {'form': form, 'logged_in_employee': request.user.employee})


@login_required
def category_update(request, pk):
    category = get_object_or_404(ProductCategory, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()

            AuditLog.objects.create(
                employee=request.user.employee,
                action=f'Updated Category: {category.name}')

            messages.success(request, 'Category updated successfully.')
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'category_form.html', {'form': form, 'logged_in_employee': request.user.employee})


@login_required
def category_delete(request, pk):
    category = get_object_or_404(ProductCategory, pk=pk)
    if Product.objects.filter(category=category).exists():
        messages.error(request, 'Cannot delete category as it has associated products.')
        return redirect('category_list')
    category.delete()

    AuditLog.objects.create(
        employee=request.user.employee,
        action=f'Deleted Category: {category.name}'
    )

    messages.success(request, 'Category deleted successfully.')
    return redirect('category_list')


@login_required
def brand_delete(request, pk):
    brand = get_object_or_404(Brand, pk=pk)
    brand.delete()

    AuditLog.objects.create(
        employee=request.user.employee,
        action=f'Deleted Brand: {brand.name}'
    )

    messages.success(request, 'Brand deleted successfully.')
    return redirect('brand_list')


@login_required
def brand_create(request):
    if request.method == 'POST':
        form = BrandForm(request.POST)
        if form.is_valid():
            form.save()

            AuditLog.objects.create(
                employee=request.user.employee,
                action=f'Created Brand: {form.cleaned_data["name"]}'
            )

            messages.success(request, 'Brand created successfully.')
            return redirect('brand_list')
    else:
        form = BrandForm()
    return render(request, 'brand_form.html', {'form': form, 'logged_in_employee': request.user.employee})

@login_required
def brand_update(request, pk):
    brand = get_object_or_404(Brand, pk=pk)
    if request.method == 'POST':
        form = BrandForm(request.POST, instance=brand)
        if form.is_valid():
            form.save()

            AuditLog.objects.create(
                employee=request.user.employee,
                action=f'Updated Brand: {brand.name}'
            )
            messages.success(request, 'Brand updated successfully.')
            return redirect('brand_list')
    else:
        form = BrandForm(instance=brand)
    return render(request, 'brand_form.html', {'form': form, 'logged_in_employee': request.user.employee})

@login_required
def brand_list(request):
    search_query = request.GET.get('search', '').strip()
    brands = Brand.objects.all()
    if search_query:
        filtered = brands.filter(name__icontains=search_query)
        if not filtered.exists():
            messages.info(request, "No results found. Displaying all brands.")
        else:
            brands = filtered
    return render(request, 'brand_list.html', {
        'brands': brands,
        'logged_in_employee': request.user.employee
    })

@login_required
def product_list(request):
    search_query = request.GET.get('search', '').strip()
    products = Product.objects.all()
    if search_query:
        filtered = products.filter(
            Q(name__icontains=search_query) |
            Q(category__name__icontains=search_query) |
            Q(brand__name__icontains=search_query)
        )
        if not filtered.exists():
            messages.info(request, "No results found. Displaying all products.")
        else:
            products = filtered
    for product in products:
        if product.category.name != "Accessories":
            computed_total = ProductItem.objects.filter(product=product, is_sold=False).count()
        else:
            computed_total = ProductItem.objects.filter(product=product).aggregate(total=Sum('quantity'))['total'] or 0
        product.__dict__['total_stock'] = computed_total
    return render(request, 'product_list.html', {
        'products': products,
        'logged_in_employee': request.user.employee
    })
@login_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.specifications = json.dumps(request.POST.get('specifications', {}))
            product.save()

            AuditLog.objects.create(
                employee=request.user.employee,
                action=f'Created Product: {product.name}'
            )

            messages.success(request, 'Product created successfully.')
            return redirect('stock_add', product_pk=product.pk)
    else:
        form = ProductForm()
    categories = ProductCategory.objects.all()
    brands = Brand.objects.all()
    return render(request, 'product_form.html', {
        'form': form,
        'categories': categories,
        'brands': brands,
        'logged_in_employee': request.user.employee
    })


@login_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            product = form.save(commit=False)
            product.specifications = json.dumps(request.POST.get('specifications', {}))
            product.save()

            AuditLog.objects.create(
                employee=request.user.employee,
                action=f'Updated Product: {product.name}'
            )

            messages.success(request, 'Product updated successfully.')
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    categories = ProductCategory.objects.all()
    brands = Brand.objects.all()
    return render(request, 'product_form.html', {
        'form': form,
        'categories': categories,
        'brands': brands,
        'logged_in_employee': request.user.employee
    })


@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.delete()

    AuditLog.objects.create(
        employee=request.user.employee,
        action=f'Deleted Product: {product.name}'
    )

    messages.success(request, 'Product deleted successfully.')
    return redirect('product_list')


@login_required
def product_stock(request, pk):
    product = get_object_or_404(Product, pk=pk)
    search_query = request.GET.get('search', '').strip()
    stock_items = ProductItem.objects.filter(product=product)
    if search_query:
        filtered = stock_items.filter(serial_number__icontains=search_query)
        if not filtered.exists():
            messages.info(request, "No results found. Displaying all stock items.")
        else:
            stock_items = filtered
    if request.method == 'POST' and 'excel_file' in request.FILES:
        # Existing Excel file upload logic remains unchanged.
        pass
    return render(request, 'product_stock.html', {
        'product': product,
        'stock_items': stock_items,
        'logged_in_employee': request.user.employee
    })

@login_required
def stock_add(request, product_pk):
    product = get_object_or_404(Product, pk=product_pk)
    category = product.category.name  # Get the category name

    if request.method == 'POST':
        form = ProductItemForm(request.POST, request.FILES, category=category)
        if form.is_valid():
            stock_item = form.save(commit=False)
            stock_item.product = product

            # Explicitly set item_type based on category (belt-and-suspenders)
            if category == "Accessories":
                stock_item.item_type = ProductItem.NON_SERIAL
                # Ensure serial number is None for non-serialized
                stock_item.serial_number = None
            else:
                stock_item.item_type = ProductItem.SERIALIZED
                stock_item.quantity = 1

            specs_data = {}
            if category in CATEGORY_SPEC_FIELDS:
                for field_name in CATEGORY_SPEC_FIELDS[category]:
                    if field_name in form.cleaned_data:
                        specs_data[field_name] = form.cleaned_data[field_name]
            stock_item.specifications = specs_data

            stock_item.save()

            AuditLog.objects.create(
                employee=request.user.employee,
                action=f'Created stock: {stock_item.serial_number or stock_item.item_type} for product: {product.name} with specifications: {stock_item.specifications or "None"}'
            )

            messages.success(request, 'Stock item added successfully.')
            return redirect('product_stock', pk=product.pk)
        else:
            messages.error(request, 'Failed to add stock item. Please check the form.')

    else:  # GET request
        form = ProductItemForm(category=category)

    return render(request, 'stock_item_form.html', {
        'form': form,
        'product': product,
        'logged_in_employee': request.user.employee
    })


@login_required
def stock_edit(request, pk):
    stock_item = get_object_or_404(ProductItem, pk=pk)
    category = stock_item.product.category.name  # Get the category name

    if request.method == 'POST':
        form = ProductItemForm(request.POST, request.FILES, instance=stock_item, category=category)
        if form.is_valid():
            stock_item = form.save(commit=False)
            stock_item.save()

            AuditLog.objects.create(
                employee=request.user.employee,
                action=f"Updated stock: {stock_item.serial_number or stock_item.item_type} for product: {stock_item.product.name} with specifications: {stock_item.specifications or 'None'}"
            )

            messages.success(request, "Stock item updated successfully.")
            return redirect("product_stock", pk=stock_item.product.pk)
    else:
        form = ProductItemForm(instance=stock_item, category=category)

    return render(request, "stock_item_form.html", {
        "form": form,
        "product": stock_item.product,
        "logged_in_employee": request.user.employee
    })


def stock_delete(request, pk):
    stock_item = get_object_or_404(ProductItem, pk=pk)
    product_id = stock_item.product.pk
    serial_number = stock_item.serial_number
    item_type = stock_item.item_type
    specifications = stock_item.specifications

    stock_item.delete()

    AuditLog.objects.create(
        employee=request.user.employee,
        action=f'Deleted stock: {serial_number or item_type} for product ID {product_id} with specifications: {specifications or "None"}'
    )

    messages.success(request, 'Stock item deleted successfully.')
    return redirect('product_stock', pk=product_id)

@login_required
def download_excel_template(request, pk):
    product = get_object_or_404(Product, pk=pk)
    category_fields = CATEGORY_SPEC_FIELDS.get(product.category.name, [])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename={product.name}_template.xlsx'

    wb = openpyxl.Workbook()
    sheet = wb.active
    sheet.title = f'{product.name} Template'

    # Add headers
    headers = ['Cost Price', 'Sale Price'] + category_fields
    if product.category.name != "Accessories":  # Include IMEI only for serialized categories
        headers.insert(0, 'IMEI')
    else:  # Include Quantity for non-serial categories
        headers.append('Quantity')
    sheet.append(headers)

    # Example row
    example_row = [100.00, 150.00] + ['Example' for _ in category_fields]
    if product.category.name != "Accessories":
        example_row.insert(0, 'SN12345')
    else:
        example_row.append(10)  # Example quantity for non-serial products
    sheet.append(example_row)

    wb.save(response)
    return response

def get_brands_by_category(request):
    category_id = request.GET.get('category_id')
    if not category_id:
        return JsonResponse({'error': 'Category ID is required'}, status=400)

    brands = Brand.objects.filter(categories__id=category_id).values('id', 'name')
    return JsonResponse(list(brands), safe=False)
