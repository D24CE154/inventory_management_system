from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render , redirect
from .models import Supplier, PurchaseOrder
from django.shortcuts import get_object_or_404
from .forms import SupplierForm
from django.contrib import messages
from django.db.models import Q
def supplierDashboard(request):
    suppliers = Supplier.objects.all()
    context = {
        'suppliers': suppliers,
        'logged_in_employee': request.user.employee
    }
    return render (request, 'suppliers.html',context)

@login_required(login_url='login')
def add_supplier(request):

    if request.method == "POST":
        supplierForm = SupplierForm(request.POST)
        if supplierForm.is_valid():
            supplierForm.save()
            messages.success(request,'Supplier added successfully')
            return redirect('suppliers')
        else:
            messages.error(request, "Invalid form data. Please check the form and try again.")
    else:
        supplierForm = SupplierForm()
    context = {
        'supplierForm': supplierForm,
        'logged_in_employee': request.user.employee
    }
    return render(request, 'add_supplier.html', context)

@login_required(login_url='login')
def edit_supplier(request, supplier_id):
    supplier = Supplier.objects.get(supplier_id=supplier_id)
    if request.method == "POST":
        supplierForm = SupplierForm(request.POST, instance=supplier)
        if supplierForm.is_valid():
            supplierForm.save()
            messages.success(request,'Supplier edited successfully')
            return redirect('suppliers')
        else:
            messages.error(request, "Invalid form data. Please check the form and try again.")
    else:
        supplierForm = SupplierForm(instance=supplier)
    context = {
        'supplierForm': supplierForm,
        'logged_in_employee': request.user.employee
    }
    return render(request, 'edit_supplier.html', context)

@login_required(login_url='login')
def delete_supplier(request,supplier_id):

    supplier = Supplier.objects.get(supplier_id=supplier_id)

    if request.method == "POST":
        supplier_name = supplier.supplier_name
        supplier.delete()
        messages.success(request, f"Supplier '{supplier_name}' deleted.")
        return redirect('suppliers')

    return redirect('suppliers')

@login_required(login_url='login')
def search_supplier(request):

    query = request.GET.get('q','')

    if query:
        suppliers = Supplier.objects.filter(
        Q(supplier_name__icontains=query) |
        Q(supplier_phone__icontains=query) |
        Q(supplier_mail__icontains=query) |
        Q(contact_person__icontains=query)
        )
    else:
        suppliers = Supplier.objects.all()
    result = []
    for supplier in suppliers:
        result.append({
            'id':supplier.supplier_id,
            'name':supplier.supplier_name,
            'contact':supplier.contact_person,
            'phone':supplier.supplier_phone,
            'mail':supplier.supplier_mail,
            'address':supplier.supplier_address,
            'created':supplier.created_at.strftime('%b %d,%Y')
        })

    return JsonResponse({'suppliers': result})

@login_required(login_url='login')
def view_supplier(request, supplier_id):
    supplier = get_object_or_404(Supplier, supplier_id=supplier_id)
    purchase_orders = PurchaseOrder.objects.filter(supplier_id=supplier).order_by('-received_date')

    context = {
        'supplier': supplier,
        'purchase_orders': purchase_orders,
        'logged_in_employee': request.user.employee
    }
    return render(request, 'view_supplier.html', context)