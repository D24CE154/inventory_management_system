from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from employees.models import Employee

@login_required(login_url="login")
def salesExecutiveDashboard(request):
    email = request.session.get("email")
    full_name = request.session.get("full_name")
    photo = request.session.get("photo")

    if not email:
        return render(request, 'SalesDashboard.html', {'user': None})
    try:
        user = Employee.objects.get(user__email=email)

    except Employee.DoesNotExist:
        user = None

    return render(request, 'SalesDashboard.html', {'user': user, 'full_name': full_name, 'photo': photo})
