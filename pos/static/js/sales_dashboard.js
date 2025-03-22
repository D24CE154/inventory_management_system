// pos/static/js/sales_dashboard.js
document.addEventListener('DOMContentLoaded', function() {
    // Initialize charts
    initSalesPerformanceChart();
    initTopProductsChart();

    // Add event listeners for period selectors
    const salesPeriodSelector = document.querySelector('.sales-period-selector');
    if (salesPeriodSelector) {
        salesPeriodSelector.addEventListener('change', function() {
            updateSalesPerformanceChart(this.value);
        });
    }

    const productsPeriodSelector = document.querySelector('.products-period-selector');
    if (productsPeriodSelector) {
        productsPeriodSelector.addEventListener('change', function() {
            updateTopProductsChart(this.value);
        });
    }
});

// Sales Performance Chart
function initSalesPerformanceChart() {
    const ctx = document.getElementById('salesPerformanceChart').getContext('2d');

    // Get data from JSON element
    let salesData;
    try {
        salesData = JSON.parse(document.getElementById('sales-data').textContent || '{}');
    } catch (e) {
        console.error("Error parsing sales data:", e);
        salesData = {
            daily: {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                values: [12500, 19200, 15000, 22400, 18300, 29100, 31200]
            }
        };
    }

    const data = salesData.daily || {
        labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        values: [12500, 19200, 15000, 22400, 18300, 29100, 31200]
    };

    window.salesChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Revenue',
                data: data.values,
                backgroundColor: 'rgba(26, 115, 232, 0.1)',
                borderColor: '#1a73e8',
                borderWidth: 2,
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '₹' + value.toLocaleString();
                        }
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return 'Revenue: ₹' + context.raw.toLocaleString();
                        }
                    }
                }
            }
        }
    });
}

function updateSalesPerformanceChart(period) {
    // Get data from JSON element
    let salesData;
    try {
        salesData = JSON.parse(document.getElementById('sales-data').textContent || '{}');
    } catch (e) {
        salesData = {};
    }

    // If period data doesn't exist, create sample data
    if (!salesData[period]) {
        salesData[period] = period === 'daily' ? {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            values: [12500, 19200, 15000, 22400, 18300, 29100, 31200]
        } : period === 'weekly' ? {
            labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
            values: [98000, 112000, 125000, 138000]
        } : {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            values: [350000, 410000, 395000, 430000, 489000, 520000]
        };
    }

    const data = salesData[period];

    window.salesChart.data.labels = data.labels;
    window.salesChart.data.datasets[0].data = data.values;
    window.salesChart.update();
}

// Top Products Chart
function initTopProductsChart() {
    const ctx = document.getElementById('topProductsChart').getContext('2d');

    // Get data from JSON element
    let topProductsData;
    try {
        topProductsData = JSON.parse(document.getElementById('top-products-data').textContent || '{}');
    } catch (e) {
        console.error("Error parsing top products data:", e);
        const productsToday = JSON.parse(document.getElementById('top-products-today').textContent || '[]');

        topProductsData = {
            today: {
                labels: productsToday.map(product => product.product_id__product_name) || [],
                values: productsToday.map(product => product.units) || []
            }
        };
    }

    if (!topProductsData.today || topProductsData.today.labels.length === 0) {
        topProductsData.today = {
            labels: ['iPhone 15 Pro', 'Samsung S24', 'Redmi Note 12', 'OnePlus 11', 'Vivo V30'],
            values: [42, 38, 35, 29, 24]
        };
    }

    const data = topProductsData.today;

    window.productsChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Units Sold',
                data: data.values,
                backgroundColor: [
                    '#4285F4', '#EA4335', '#FBBC05', '#34A853', '#8F44AD'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            scales: {
                x: {
                    beginAtZero: true
                }
            }
        }
    });
}

function updateTopProductsChart(period) {
    // Get data from JSON element
    let topProductsData;
    try {
        topProductsData = JSON.parse(document.getElementById('top-products-data').textContent || '{}');
    } catch (e) {
        topProductsData = {};
    }

    // If period data doesn't exist, create sample data
    if (!topProductsData[period]) {
        topProductsData[period] = period === 'today' ? {
            labels: ['iPhone 15 Pro', 'Samsung S24', 'Redmi Note 12', 'OnePlus 11', 'Vivo V30'],
            values: [42, 38, 35, 29, 24]
        } : period === 'this_week' ? {
            labels: ['Samsung S24', 'iPhone 15 Pro', 'Redmi Note 12', 'Poco F5', 'OnePlus 11'],
            values: [168, 155, 129, 110, 95]
        } : {
            labels: ['iPhone 15 Pro', 'Samsung S24', 'Samsung A54', 'Redmi Note 12', 'Vivo V30'],
            values: [452, 431, 378, 345, 312]
        };
    }

    const data = topProductsData[period];

    window.productsChart.data.labels = data.labels;
    window.productsChart.data.datasets[0].data = data.values;
    window.productsChart.update();
}