from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from employees.models import Employee

@login_required
def salesExecutiveDashboard(request):
    email = request.session.get("email")
    full_name = request.session.get("full_name")
    photo = request.session.get("photo")

    if not email:
        print("\n❌ DEBUG: Email not found in session!")  # 🔥 Debugging
        return render(request, 'SalesDashboard.html', {'user': None})  # 🔹 Handle missing email

    try:
        user = Employee.objects.get(user__email=email)  # 🔹 Get employee based on email
        print(f"\n✅ DEBUG: Employee found -> {user.full_name}")
        print(f"✅ DEBUG: Employee photo -> {user.photo.url}")  # 🔥 Debugging
    except Employee.DoesNotExist:
        print("\n❌ DEBUG: Employee not found in database!")  # 🔥 Debugging
        user = None  # 🔹 Handle case where employee does not exist

    return render(request, 'SalesDashboard.html', {'user': user, 'full_name': full_name, 'photo': photo})
