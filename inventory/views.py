# inventory/views.py
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.files.storage import default_storage
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from .models import ProductCategory, Brand, Product, ProductItem
from .forms import ProductForm, ProductItemForm, CategoryForm, BrandForm, CATEGORY_SPEC_FIELDS
import json

def is_active_inventory_manager(user):
    if user.is_authenticated and (user.employee.role == 'Admin' or user.employee.role == 'Inventory Manager') and user.employee.is_active:
        return True
    return False

@login_required(login_url='login')
def inventoryManagerDashboard(request):
    context = {
        'logged_in_employee': request.user.employee
    }
    return render(request, 'inventoryManagerDashboard.html', context)

@login_required
def category_list(request):
    categories = ProductCategory.objects.all()
    return render(request, 'category_list.html', {'categories': categories,'logged_in_employee': request.user.employee})

@login_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created successfully.')
            return redirect('category_list')
    else:
        form = CategoryForm()
    return render(request, 'category_form.html', {'form': form,'logged_in_employee': request.user.employee})

@login_required
def category_update(request, pk):
    category = get_object_or_404(ProductCategory, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully.')
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'category_form.html', {'form': form,'logged_in_employee': request.user.employee})

@login_required
def category_delete(request, pk):
    category = get_object_or_404(ProductCategory, pk=pk)
    if Product.objects.filter(category=category).exists():
        messages.error(request, 'Cannot delete category as it has associated products.')
        return redirect('category_list')
    category.delete()
    messages.success(request, 'Category deleted successfully.')
    return redirect('category_list')

@login_required
def brand_delete(request, pk):
    brand = get_object_or_404(Brand, pk=pk)
    brand.delete()
    messages.success(request, 'Brand deleted successfully.')
    return redirect('brand_list')

@login_required
def brand_create(request):
    if request.method == 'POST':
        form = BrandForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Brand created successfully.')
            return redirect('brand_list')
    else:
        form = BrandForm()
    return render(request, 'brand_form.html', {'form': form,'logged_in_employee': request.user.employee})

@login_required
def brand_update(request, pk):
    brand = get_object_or_404(Brand, pk=pk)
    if request.method == 'POST':
        form = BrandForm(request.POST, instance=brand)
        if form.is_valid():
            form.save()
            messages.success(request, 'Brand updated successfully.')
            return redirect('brand_list')
    else:
        form = BrandForm(instance=brand)
    return render(request, 'brand_form.html', {'form': form,'logged_in_employee': request.user.employee})

# inventory/views.py
@login_required
def brand_list(request):
    brands = Brand.objects.all()
    return render(request, 'brand_list.html', {'brands': brands, 'logged_in_employee': request.user.employee})

def product_list(request):
    products = Product.objects.all()
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
            messages.success(request, 'Product created successfully.')
            # Redirect to stock_add view for the newly created product
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
    messages.success(request, 'Product deleted successfully.')
    return redirect('product_list')

@login_required
def product_stock(request, pk):
    product = get_object_or_404(Product, pk=pk)
    stock_items = ProductItem.objects.filter(product=product)
    return render(request, 'product_stock.html', {'product': product, 'stock_items': stock_items,'logged_in_employee': request.user.employee})

@login_required
def stock_add(request, product_pk):
    product = get_object_or_404(Product, pk=product_pk)
    category = product.category.name  # Get the category name

    if request.method == 'POST':
        form = ProductItemForm(request.POST, request.FILES, category=category)
        if form.is_valid():
            stock_item = form.save(commit=False)
            stock_item.product = product
            if category != "Accessories":
                stock_item.quantity = 1  # Ensure quantity is 1 for serialized products
            stock_item.save()
            messages.success(request, 'Stock item added successfully.')
            return redirect('product_stock', pk=product.pk)
    else:
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
            messages.success(request, 'Stock item updated successfully.')
            return redirect('product_stock', pk=stock_item.product.pk)
    else:
        form = ProductItemForm(instance=stock_item, category=category)

    return render(request, 'stock_item_form.html', {
        'form': form,
        'product': stock_item.product,
        'logged_in_employee': request.user.employee
    })
@login_required
def stock_delete(request, pk):
    stock_item = get_object_or_404(ProductItem, pk=pk)
    stock_item.delete()
    messages.success(request, 'Stock item deleted successfully.')
    return redirect('product_stock', pk=stock_item.product.pk)

def get_brands(request):
    category_id = request.GET.get('category_id')
    if category_id:
        brands = Brand.objects.filter(categories__id=category_id).values('id', 'name')
        return JsonResponse(list(brands), safe=False)
    return JsonResponse([], safe=False)