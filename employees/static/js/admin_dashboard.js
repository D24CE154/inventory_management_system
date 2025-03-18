/**
 * Admin Dashboard JavaScript
 * Contains admin-specific functionality for the admin dashboard
 */

document.addEventListener('DOMContentLoaded', function() {
    // Admin-specific initializations

    // Function to handle admin quick actions
    function initAdminQuickActions() {
        const quickActionButtons = document.querySelectorAll('.quick-action-btn');
        if (quickActionButtons) {
            quickActionButtons.forEach(button => {
                button.addEventListener('click', function(e) {
                    const action = this.getAttribute('data-action');
                    const id = this.getAttribute('data-id');

                    if (action === 'disable-user') {
                        if (confirm('Are you sure you want to disable this user?')) {
                            console.log('Disabling user:', id);
                            // Future AJAX call to disable user
                        }
                    } else if (action === 'enable-user') {
                        console.log('Enabling user:', id);
                        // Future AJAX call to enable user
                    } else if (action === 'reset-password') {
                        if (confirm('Are you sure you want to reset password for this user?')) {
                            console.log('Resetting password for user:', id);
                            // Future AJAX call to reset password
                        }
                    }
                });
            });
        }
    }

    // Employee trend chart - shows employee activity over time
    function initEmployeeActivityChart() {
        const employeeActivityEl = document.getElementById('employeeActivityChart');
        if (employeeActivityEl) {
            const ctx = employeeActivityEl.getContext('2d');
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                    datasets: [{
                        label: 'Active Employees',
                        data: [15, 17, 18, 19, 20, 22],
                        borderColor: '#10b981',
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
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
                            min: 0,
                            ticks: {
                                precision: 0
                            }
                        }
                    }
                }
            });
        }
    }

    // Stock value chart - shows inventory value over time
    function initInventoryValueChart() {
        const inventoryValueEl = document.getElementById('inventoryValueChart');
        if (inventoryValueEl) {
            const ctx = inventoryValueEl.getContext('2d');
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                    datasets: [{
                        label: 'Inventory Value',
                        data: [500000, 580000, 630000, 750000, 740000, 850000],
                        borderColor: '#3b82f6',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
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
                            callbacks: {
                                label: function(context) {
                                    return '₹' + context.parsed.y.toLocaleString('en-IN');
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
    }

    // Low stock alert handling
    function initLowStockAlerts() {
        const alertsContainer = document.getElementById('low-stock-alerts');
        if (alertsContainer) {
            // In a real implementation, this would be replaced with AJAX call
            // to fetch current low stock items

            const dismissButtons = alertsContainer.querySelectorAll('.dismiss-alert');
            dismissButtons.forEach(button => {
                button.addEventListener('click', function(e) {
                    e.preventDefault();
                    const alertId = this.getAttribute('data-alert-id');
                    const alertElement = document.getElementById(`alert-${alertId}`);

                    if (alertElement) {
                        alertElement.classList.add('fade-out');
                        setTimeout(() => {
                            alertElement.remove();

                            // Update alert count
                            const countElement = document.getElementById('alert-count');
                            if (countElement) {
                                const currentCount = parseInt(countElement.textContent);
                                countElement.textContent = Math.max(0, currentCount - 1);

                                if (currentCount - 1 <= 0) {
                                    // No more alerts, show empty message
                                    const emptyMessage = document.createElement('div');
                                    emptyMessage.className = 'p-4 text-center text-gray-500';
                                    emptyMessage.textContent = 'No alerts at this time';
                                    alertsContainer.appendChild(emptyMessage);
                                }
                            }
                        }, 300);
                    }
                });
            });
        }
    }

    // System health overview
    function initSystemHealthDisplay() {
        const healthIndicators = document.querySelectorAll('.system-health-indicator');
        if (healthIndicators) {
            // In a real implementation, we'd fetch current system health metrics
            // This is just a placeholder that could simulate status changes

            healthIndicators.forEach(indicator => {
                const status = indicator.getAttribute('data-status');
                const statusElement = indicator.querySelector('.status-indicator');

                if (statusElement) {
                    if (status === 'good') {
                        statusElement.classList.add('bg-green-500');
                    } else if (status === 'warning') {
                        statusElement.classList.add('bg-yellow-500');
                    } else if (status === 'critical') {
                        statusElement.classList.add('bg-red-500');
                    }
                }
            });
        }
    }

    // Initialize admin dashboard components if they exist
    initAdminQuickActions();
    initEmployeeActivityChart();
    initInventoryValueChart();
    initLowStockAlerts();
    initSystemHealthDisplay();

    // Handle filter toggles for the admin dashboard
    const filterToggle = document.getElementById('toggle-filters');
    const filterContainer = document.getElementById('filter-container');

    if (filterToggle && filterContainer) {
        filterToggle.addEventListener('click', function(e) {
            e.preventDefault();
            filterContainer.classList.toggle('hidden');

            // Update button text
            const isHidden = filterContainer.classList.contains('hidden');
            filterToggle.querySelector('span').textContent = isHidden ? 'Show Filters' : 'Hide Filters';

            // Update icon
            const icon = filterToggle.querySelector('i');
            if (isHidden) {
                icon.classList.replace('fa-chevron-up', 'fa-chevron-down');
            } else {
                icon.classList.replace('fa-chevron-down', 'fa-chevron-up');
            }
        });
    }

    // Handle date picker for admin dashboard
    const datePickers = document.querySelectorAll('.admin-date-picker');
    if (datePickers.length > 0) {
        datePickers.forEach(picker => {
            picker.addEventListener('change', function() {
                console.log('Date changed to:', this.value);
                // In a real implementation, this would trigger data reload
            });
        });
    }
});