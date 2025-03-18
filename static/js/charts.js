/**
 * Charts.js - Common chart initialization and utilities
 */

class DashboardCharts {
    /**
     * Initialize a revenue chart
     * @param {string} elementId - The canvas element ID
     * @param {Array} labels - X-axis labels
     * @param {Array} data - Y-axis data points
     */
    static initRevenueChart(elementId, labels = [], data = []) {
        const element = document.getElementById(elementId);
        if (!element) return;

        // Use provided data or fallback to defaults
        const chartLabels = labels.length ? labels : ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'];
        const chartData = data.length ? data : [65000, 59000, 80000, 81000, 56000, 95000, 140000];

        const ctx = element.getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: chartLabels,
                datasets: [{
                    label: 'Revenue',
                    data: chartData,
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

    /**
     * Initialize a category doughnut chart
     * @param {string} elementId - The canvas element ID
     * @param {Array} labels - Category labels
     * @param {Array} data - Category data values
     */
    static initCategoryChart(elementId, labels = [], data = []) {
        const element = document.getElementById(elementId);
        if (!element) return;

        // Use provided data or fallback to defaults
        const chartLabels = labels.length ? labels : ['Smartphones', 'Accessories', 'Tablets', 'Wearables', 'Others'];
        const chartData = data.length ? data : [35, 25, 20, 15, 5];

        const ctx = element.getContext('2d');
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: chartLabels,
                datasets: [{
                    data: chartData,
                    backgroundColor: [
                        '#1a73e8', '#34a853', '#fbbc05', '#ea4335', '#9334e6',
                        '#4285f4', '#0f9d58', '#db4437', '#673ab7', '#ff6d00'
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

    /**
     * Initialize a sales bar chart
     * @param {string} elementId - The canvas element ID
     * @param {Array} labels - X-axis labels
     * @param {Array} data - Y-axis data points
     */
    static initSalesChart(elementId, labels = [], data = []) {
        const element = document.getElementById(elementId);
        if (!element) return;

        // Use provided data or fallback to defaults
        const chartLabels = labels.length ? labels : ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
        const chartData = data.length ? data : [12, 19, 8, 15, 20, 27, 15];

        const ctx = element.getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: chartLabels,
                datasets: [{
                    label: 'Sales',
                    data: chartData,
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

    /**
     * Update chart data via AJAX
     * @param {string} chartId - The chart element ID
     * @param {string} endpoint - API endpoint to fetch data
     * @param {Object} params - Query parameters
     */
    static updateChartData(chartId, endpoint, params = {}) {
        // Convert params to query string
        const queryString = Object.keys(params)
            .map(key => `${encodeURIComponent(key)}=${encodeURIComponent(params[key])}`)
            .join('&');

        // Make AJAX call
        fetch(`${endpoint}?${queryString}`)
            .then(response => response.json())
            .then(data => {
                // Find chart instance
                const chartInstance = Chart.getChart(chartId);
                if (chartInstance) {
                    // Update chart data
                    chartInstance.data.labels = data.labels;
                    chartInstance.data.datasets[0].data = data.data;
                    chartInstance.update();
                }
            })
            .catch(error => console.error('Error updating chart data:', error));
    }
}

// Export for ES6 modules if needed
if (typeof module !== 'undefined') {
    module.exports = DashboardCharts;
}