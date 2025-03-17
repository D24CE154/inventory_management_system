from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def role_required(allowed_roles=None):
    """
    Decorator to check if the user has one of the allowed roles.
    Usage: @role_required(['Admin', 'Inventory Manager'])
    """
    if allowed_roles is None:
        allowed_roles = []

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Check if user is authenticated and has an employee profile
            try:
                if request.user.employee.role in allowed_roles:
                    return view_func(request, *args, **kwargs)
                else:
                    messages.error(request,"Permission denied.")
                    return redirect('error_403')
            except AttributeError:
                messages.error(request, "User profile not found.")
                return redirect('error_403')

        return _wrapped_view
    return decorator