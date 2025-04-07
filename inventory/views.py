# inventory/views.py

from django.forms import formset_factory
from django import forms
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Sum, Count, Q
from django.db import transaction
from django.http import JsonResponse
from .forms import CategoryForm, ProductForm, BrandForm, ProductItemsForm, CATEGORY_SPEC_FIELDS
from .models import Product, ProductItems, ProductCategory, Brand

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

@login_required(login_url='login')
def category_list(request):
    categories = ProductCategory.objects.annotate(
        product_count=Count('product')
    )
    context = {
        'categories': categories,
        'logged_in_employee': request.user.employee
    }
    return render(request, 'category_list.html', context)

@login_required(login_url='login')
def category_products(request, category_id):
    category = get_object_or_404(ProductCategory, category_id=category_id)
    products = Product.objects.filter(category_id=category).annotate(
        available_count=Count('productitems', filter=Q(productitems__status='Available')),
        total_value=Sum('productitems__price', filter=Q(productitems__status='Available'))
    )
    context = {
        'category': category,
        'products': products,
        'logged_in_employee': request.user.employee
    }
    return render(request, 'category_products.html', context)

@login_required(login_url='login')
def add_category(request):
    if not (request.user.employee.role == 'Admin' or request.user.employee.role == 'Inventory Manager'):
        messages.error(request, "You don't have permission to access this page.")
        return redirect("error_403_view")

    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Category added successfully.")
            return redirect('category_list')
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

    category = get_object_or_404(ProductCategory, pk=category_id)

    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Category updated successfully.")
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)

    context = {
        'form': form,
        'logged_in_employee': request.user.employee
    }
    return render(request, 'edit_category.html', context)

@login_required(login_url='login')
def delete_category(request, category_id):
    if not is_active_inventory_manager(request.user):
        messages.error(request, "You don't have permission to access this page.")
        return redirect("error_403_view")

    category = get_object_or_404(ProductCategory, category_id=category_id)

    if Product.objects.filter(category_id=category_id).exists():
        messages.error(request, "Cannot delete category with associated products.")
        return redirect('category_list')

    category_name = category.category_name
    category.delete()
    messages.success(request, f"Category {category_name} deleted successfully.")
    return redirect('category_list')

@login_required(login_url='login')
def brand_list(request):
    brands = Brand.objects.all()
    context = {
        'brands': brands,
        'logged_in_employee': request.user.employee
    }
    return render(request, 'brand_list.html', context)

@login_required(login_url='login')
def add_brand(request):
    if request.method == 'POST':
        form = BrandForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Brand added successfully.")
            return redirect('brand_list')
    else:
        form = BrandForm()
    context = {
        'form': form,
        'logged_in_employee': request.user.employee
    }
    return render(request, 'add_brand.html', context)

@login_required(login_url='login')
def edit_brand(request, brand_id):
    brand = get_object_or_404(Brand, brand_id=brand_id)
    if request.method == 'POST':
        form = BrandForm(request.POST, instance=brand)
        if form.is_valid():
            form.save()
            messages.success(request, "Brand updated successfully.")
            return redirect('brand_list')
    else:
        form = BrandForm(instance=brand)
    context = {
        'form': form,
        'logged_in_employee': request.user.employee
    }
    return render(request, 'edit_brand.html', context)

@login_required(login_url='login')
def delete_brand(request, brand_id):
    brand = get_object_or_404(Brand, brand_id=brand_id)
    brand.delete()
    messages.success(request, "Brand deleted successfully.")
    return redirect('brand_list')

@login_required(login_url='login')
def add_product(request):
    if request.method == 'POST':
        product_form = ProductForm(request.POST)
        if product_form.is_valid():
            product = product_form.save()
            # Remove the is_serialized check or use stock instead
            if product_form.cleaned_data['stock'] > 0:
                return redirect('add_product_items', product_id=product.product_id, stock=product_form.cleaned_data['stock'])
            messages.success(request, "Product added successfully.")
            return redirect('product_list')
    else:
        product_form = ProductForm()
    return render(request, 'add_product.html', {'product_form': product_form, 'logged_in_employee': request.user.employee})
@login_required(login_url='login')
def edit_product(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        product_form = ProductForm(request.POST, instance=product)
        if product_form.is_valid():
            product_form.save()
            messages.success(request, "Product updated successfully.")
            return redirect('product_list')
    else:
        product_form = ProductForm(instance=product)
    return render(request, 'edit_product.html', {'product_form': product_form,'logged_in_employee': request.user.employee})

@login_required(login_url='login')
def delete_product(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    product_name = product.product_name
    product.delete()
    messages.success(request, f"Product '{product_name}' deleted successfully.")
    return redirect('product_list')

@login_required(login_url='login')
def add_product_items(request, product_id, stock):
    product = get_object_or_404(Product, pk=product_id)
    category = product.category_id

    # Get specification fields for this category
    spec_fields = CATEGORY_SPEC_FIELDS.get(category.category_name, [])

    ProductItemsFormSet = formset_factory(ProductItemsForm, extra=stock)

    if request.method == 'POST':
        if 'cancel' in request.POST:
            product.delete()
            messages.info(request, "Product creation was canceled.")
            return redirect('product_list')

        formset = ProductItemsFormSet(request.POST, request.FILES)

        # Add specification fields to each form
        for form in formset:
            for field in spec_fields:
                form.fields[field] = forms.CharField(
                    required=False,
                    widget=forms.TextInput(attrs={'class': 'form-control'})
                )

        if formset.is_valid():
            with transaction.atomic():
                for form in formset:
                    product_item = form.save(commit=False)
                    product_item.product = product

                    # Handle image renaming to serial number
                    if form.cleaned_data.get('image'):
                        image = form.cleaned_data.get('image')
                        if image.size > 2 * 1024 * 1024:  # 2MB limit
                            messages.error(request, "Image size must be less than 2MB")
                            continue

                        # Get file extension
                        ext = image.name.split('.')[-1]
                        # Rename file to serial number
                        image.name = f"{form.cleaned_data['serial_number']}.{ext}"

                    # Save specifications
                    specifications = {}
                    for field in spec_fields:
                        if field in form.cleaned_data and form.cleaned_data[field]:
                            specifications[field] = form.cleaned_data[field]

                    product_item.specifications = specifications
                    product_item.save()

                messages.success(request, "Product items added successfully.")
                return redirect('product_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        formset = ProductItemsFormSet()

        # Add specification fields to each form
        for form in formset:
            for field in spec_fields:
                form.fields[field] = forms.CharField(
                    required=False,
                    widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': field.capitalize()})
                )

    return render(request, 'add_product_items.html', {
        'formset': formset,
        'product_name': product.product_name,
        'logged_in_employee': request.user.employee
    })

@login_required(login_url='login')
def edit_product_item(request, item_id):
    product_item = get_object_or_404(ProductItems, pk=item_id)
    if request.method == 'POST':
        form = ProductItemsForm(request.POST, request.FILES, instance=product_item)
        if form.is_valid():
            form.save()
            messages.success(request, "Product item updated successfully.")
            return redirect('product_items_list', product_id=product_item.product.product_id)
    else:
        form = ProductItemsForm(instance=product_item, category=product_item.product.category_id)
    return render(request, 'edit_product_item.html', {'form': form,'logged_in_employee': request.user.employee})

@login_required(login_url='login')
def delete_product_item(request, item_id):
    product_item = get_object_or_404(ProductItems, pk=item_id)
    product = product_item.product

    # Check if this is the last product item
    item_count = ProductItems.objects.filter(product=product).count()
    if item_count <= 1:
        messages.error(request, "Cannot delete the last product item. A product must have at least one item.")
        return redirect('product_items_list', product_id=product.product_id)

    # Delete product item directly
    product_name = product_item.serial_number
    product_item.delete()

    messages.success(request, f"Product item '{product_name}' deleted successfully.")
    return redirect('product_items_list', product_id=product.product_id)

@login_required(login_url='login')
def product_list(request):
    product_list = Product.objects.all()
    paginator = Paginator(product_list, 10)
    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    return render(request, 'product_list.html', {'products': products,'logged_in_employee': request.user.employee})

@login_required(login_url='login')
def product_items_list(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    product_items_list = ProductItems.objects.filter(product=product)
    paginator = Paginator(product_items_list, 10)
    page = request.GET.get('page')
    try:
        product_items = paginator.page(page)
    except PageNotAnInteger:
        product_items = paginator.page(1)
    except EmptyPage:
        product_items = paginator.page(paginator.num_pages)

    return render(request, 'product_items_list.html', {'product': product, 'product_items': product_items,'logged_in_employee': request.user.employee})

@login_required(login_url='login')
def get_brands_by_category(request, category_id):
    brands = Brand.objects.filter(categories__pk=category_id).distinct()
    # Fix the property names to match what JavaScript expects
    brand_list = [{'id': brand.brand_id, 'name': brand.brand_name} for brand in brands]
    return JsonResponse(brand_list, safe=False)