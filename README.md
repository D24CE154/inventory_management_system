# Inventory Management System

A Django-based inventory management system that integrates point of sale, inventory management, supplier management, and employee authentication.

[Project Structure](Project%20structure.txt)
inventory_management_system/   # Root Project Folder
│── inventory_management_system/  # Main Django Project
│   │── settings.py        # Project settings
│   │── urls.py            # Main URL routing
│   │── wsgi.py            # WSGI entry point
│   │── asgi.py            # ASGI entry point 
│   │── __init__.py        # Required for Python package
│
│── pos/                   # Point Of Sales Module (Django App)
│   │── models.py          # Database models for POS
│   │── views.py           # Business logic for POS
│   │── urls.py            # URL routes for POS
│   │── forms.py           # Django Forms 
│   │── templates/         # HTML Templates for POS 
│   │── static/            # Static files (CSS, JS) for POS
│   │── __init__.py        # Required for Python package
│
│── inventory/             # Inventory Management Module (Django App)
│   │── models.py          # Database models for Inventory
│   │── views.py           # Business logic for Inventory
│   │── urls.py            # URL routes for Inventory
│   │── forms.py           # Django Forms
│   │── templates/         # HTML Templates for Inventory
│   │── static/            # Static files (CSS, JS) for Inventory
│   │── __init__.py        # Required for Python package
│
│── supplier/              # Supplier Management Module (Django App)
│   │── models.py          # Database models for Supplier Management
│   │── views.py           # Business logic for Supplier Management
│   │── urls.py            # URL routes for Supplier Management
│   │── forms.py           # Django Forms
│   │── templates          # HTML Templates for Supplier Management
│   │── static/            # Static files (CSS, JS) for Supplier Management
│   │── __init__.py        # Required for Python package
│
│── employees/             # Employee Management Module
│   │── models.py          # Employee authentication
│   │── views.py           # Authentication views (Login, Logout, Register)
│   │── urls.py            # URL routes for user authentication
│   │── templates/         # Authentication templates
│   │── static/            # Static files for authentication
│   │── __init__.py        # Required for Python package
│
│── static/                # Global Static Files (CSS, JS, Images)
│── media/                 # Media Files (User uploads)
│── templates/             # Global Templates (base.html, common components)
│── manage.py              # Django's management command-line tool
│── requirements.txt       # Project dependencies
│── .gitignore             # Ignore unnecessary files for Git
│── .env                   # Environment Variables (Secret keys, database settings)
│── README.md              # Project documentation

## Features

- **Role-Based Access**: Different dashboards and functionalities for Admin, Inventory Manager, and Sales Executive.
- **Inventory Management**: Manage products, categories, brands, and suppliers.
- **Point of Sales**: Handles sales, customer management, and invoice generation.
- **Employee Management**: Authentication and audit logging.

## Technologies

- Python (Django)
- JavaScript
- HTML5 / CSS3
- MySQL
