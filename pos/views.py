from django.shortcuts import render , redirect

# Create your views here.
def salesExecutiveDashboard(request):
    return render (request, 'SalesDashboard.html')

