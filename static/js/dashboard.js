// Dashboard Charts & Interactive Elements
document.addEventListener('DOMContentLoaded', function() {
    // Toggle profile dropdown
    document.getElementById('profile-menu').addEventListener('click', function() {
        document.getElementById('profile-dropdown').classList.toggle('show');
    });

    // Close dropdown when clicking outside
    window.addEventListener('click', function(e) {
        if (!document.getElementById('profile-menu').contains(e.target)) {
            document.getElementById('profile-dropdown').classList.remove('show');
        }
    });

    // Mobile menu toggle
    document.getElementById('menu-toggle').addEventListener('click', function() {
        document.body.classList.toggle('sidebar-shown');
    });

    // Close sidebar on mobile
    document.getElementById('close-sidebar').addEventListener('click', function() {
        document.body.classList.remove('sidebar-shown');
    });

    // Initialize Revenue Chart if element exists
    const revenueChartElement = document.getElementById('revenueChart');
    if (revenueChartElement) {
        const revenueCtx = revenueChartElement.getContext('2d');
        new Chart(revenueCtx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'],
                datasets: [{
                    label: 'Revenue',
                    data: [65000, 59000, 80000, 81000, 56000, 95000, 140000],
                    borderColor: '#1a73e8',
                    backgroundColor: 'rgba(26, 115, 232, 0.1)',
                    tension: 0.3,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        callbacks: {
                            label: function(context) {
                                let label = context.dataset.label || '';
                                if (label) {
                                    label += ': ';
                                }
                                if (context.parsed.y !== null) {
                                    label += new Intl.NumberFormat('en-IN', {
                                        style: 'currency',
                                        currency: 'INR'
                                    }).format(context.parsed.y);
                                }
                                return label;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: {
                            display: false
                        }
                    },
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '₹' + value.toLocaleString('en-IN');
                            }
                        }
                    }
                }
            }
        });
    }

    // Initialize Categories Chart if element exists
    const categoriesChartElement = document.getElementById('categoriesChart');
    if (categoriesChartElement) {
        const categoriesCtx = categoriesChartElement.getContext('2d');
        new Chart(categoriesCtx, {
            type: 'doughnut',
            data: {
                labels: ['Smartphones', 'Accessories', 'Tablets', 'Wearables', 'Others'],
                datasets: [{
                    data: [35, 25, 20, 15, 5],
                    backgroundColor: [
                        '#1a73e8', '#34a853', '#fbbc05', '#ea4335', '#9334e6'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true,
                            pointStyle: 'circle'
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed || 0;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = Math.round((value / total) * 100);
                                return `${label}: ${percentage}%`;
                            }
                        }
                    }
                },
                cutout: '70%'
            }
        });
    }

    // Initialize Sales Chart if element exists
    const salesChartElement = document.getElementById('salesChart');
    if (salesChartElement) {
        const salesCtx = salesChartElement.getContext('2d');
        new Chart(salesCtx, {
            type: 'bar',
            data: {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                datasets: [{
                    label: 'Sales',
                    data: [12, 19, 8, 15, 20, 27, 15],
                    backgroundColor: '#1a73e8'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    x: {
                        grid: {
                            display: false
                        }
                    },
                    y: {
                        beginAtZero: true,
                        ticks: {
                            precision: 0
                        }
                    }
                }
            }
        });
    }

    // Handle date range selectors
    const dateRangeSelectors = document.querySelectorAll('.date-range-selector');
    dateRangeSelectors.forEach(selector => {
        selector.addEventListener('change', function() {
            console.log('Date range changed to:', this.value);
            // Here you would typically fetch new data based on the selected range
            // and update the associated chart
        });
    });

    // Handle table pagination if it exists
    const paginationButtons = document.querySelectorAll('.pagination-button');
    if (paginationButtons) {
        paginationButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                const page = this.getAttribute('data-page');
                console.log('Navigate to page:', page);
                // Here you would handle pagination logic
            });
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