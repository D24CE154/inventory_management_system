// Dashboard Core Functionality
document.addEventListener('DOMContentLoaded', function() {
    // Toggle profile dropdown
    document.getElementById('profile-menu')?.addEventListener('click', function() {
        document.getElementById('profile-dropdown').classList.toggle('show');
    });

    // Close dropdown when clicking outside
    window.addEventListener('click', function(e) {
        const profileMenu = document.getElementById('profile-menu');
        if (profileMenu && !profileMenu.contains(e.target)) {
            document.getElementById('profile-dropdown').classList.remove('show');
        }
    });

    // Mobile menu toggle
    document.getElementById('menu-toggle')?.addEventListener('click', function() {
        document.body.classList.toggle('sidebar-shown');
    });

    // Close sidebar on mobile
    document.getElementById('close-sidebar')?.addEventListener('click', function() {
        document.body.classList.remove('sidebar-shown');
    });

    // Check for saved sidebar state
    const sidebarCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
    if (sidebarCollapsed) {
        document.body.classList.add('sidebar-collapsed');
    }

    // Desktop sidebar toggle
    const sidebarToggle = document.getElementById('sidebar-toggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            document.body.classList.toggle('sidebar-collapsed');
            localStorage.setItem(
                'sidebarCollapsed',
                document.body.classList.contains('sidebar-collapsed')
            );
        });
    }

    // Handle notifications
    const notificationBell = document.querySelector('.notification-bell');
    if (notificationBell) {
        notificationBell.addEventListener('click', function() {
            console.log('Notifications clicked');
            // Here you would toggle a notifications panel
        });
    }

    // Current date for the dashboard
    const currentDate = document.getElementById('current-date');
    if (currentDate) {
        const now = new Date();
        const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
        currentDate.textContent = now.toLocaleDateString('en-IN', options);
    }
});

// Message handling
document.addEventListener('DOMContentLoaded', function() {
    // Handle alert dismissals
    document.querySelectorAll('.alert-dismissible .close').forEach(function(button) {
        button.addEventListener('click', function() {
            const alert = this.closest('.alert');
            alert.style.animation = 'fadeOut 0.3s forwards';
            setTimeout(function() {
                alert.remove();
            }, 300);
        });
    });

    // Auto-dismiss alerts after 5 seconds
    document.querySelectorAll('.alert').forEach(function(alert) {
        setTimeout(function() {
            if (alert) {
                alert.style.animation = 'fadeOut 0.3s forwards';
                setTimeout(function() {
                    alert.remove();
                }, 300);
            }
        }, 5000);
    });
});