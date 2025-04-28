// pos/static/js/sales_dashboard.js
document.addEventListener('DOMContentLoaded', function() {
    // Initialize charts with initially loaded data
    initSalesPerformanceChart();
    initTopProductsChart();

    // Add event listeners for period selectors
    const salesPeriodSelector = document.querySelector('.sales-period-selector');
    if (salesPeriodSelector) {
        salesPeriodSelector.addEventListener('change', function() {
            fetchAndUpdateSalesPerformanceChart(this.value); // Use fetch function
        });
    }

    const productsPeriodSelector = document.querySelector('.products-period-selector');
    if (productsPeriodSelector) {
        productsPeriodSelector.addEventListener('change', function() {
            fetchAndUpdateTopProductsChart(this.value); // Use fetch function
        });
    }
});

// --- Sales Performance Chart ---

// Global variable to hold the chart instance
let salesChart = null;

function initSalesPerformanceChart() {
    const ctx = document.getElementById('salesPerformanceChart')?.getContext('2d');
    if (!ctx) {
        console.error("Sales Performance Chart canvas not found.");
        return;
    }

    // Get initial data from the embedded JSON script tag
    let initialSalesData;
    try {
        const salesDataElement = document.getElementById('sales-data');
        initialSalesData = JSON.parse(salesDataElement?.textContent || '{}');
    } catch (e) {
        console.error("Error parsing initial sales data:", e);
        initialSalesData = {}; // Fallback to empty data
    }

    // Use 'daily' data for initialization, or provide default structure if missing
    const initialData = initialSalesData.daily || {
        labels: [],
        values: []
    };

    // Destroy existing chart instance if it exists
    if (salesChart) {
        salesChart.destroy();
    }

    salesChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: initialData.labels,
            datasets: [{
                label: 'Revenue',
                data: initialData.values,
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

function fetchAndUpdateSalesPerformanceChart(period) {
    if (!salesChart) {
        console.error("Sales chart instance not available for update.");
        return;
    }

    // Construct the URL with the period query parameter
    const url = `/pos/api/sales-performance-data/?period=${encodeURIComponent(period)}`;

    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data && data.labels && data.values) {
                // Update chart data
                salesChart.data.labels = data.labels;
                salesChart.data.datasets[0].data = data.values;
                salesChart.update(); // Redraw the chart
            } else {
                console.error("Invalid data format received from server:", data);
                // Optionally clear the chart or show a default state
                salesChart.data.labels = [];
                salesChart.data.datasets[0].data = [];
                salesChart.update();
            }
        })
        .catch(error => {
            console.error('Error fetching sales performance data:', error);
            // Optionally display an error message to the user on the chart
            // For now, just clear the chart
            salesChart.data.labels = [];
            salesChart.data.datasets[0].data = [];
            salesChart.update();
        });
}


// --- Top Products Chart ---

// Global variable to hold the chart instance
let productsChart = null;

function initTopProductsChart() {
    const ctx = document.getElementById('topProductsChart')?.getContext('2d');
    if (!ctx) {
        console.error("Top Products Chart canvas not found.");
        return;
    }

    // Get initial data from the embedded JSON script tag
    let initialTopProductsData;
    try {
        const topProductsDataElement = document.getElementById('top-products-data');
        initialTopProductsData = JSON.parse(topProductsDataElement?.textContent || '{}');
    } catch (e) {
        console.error("Error parsing initial top products data:", e);
        initialTopProductsData = {}; // Fallback to empty data
    }

    // Use 'today' data for initialization, or provide default structure if missing
    const initialData = initialTopProductsData.today || {
        labels: [],
        values: []
    };

    // Destroy existing chart instance if it exists
    if (productsChart) {
        productsChart.destroy();
    }

    productsChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: initialData.labels,
            datasets: [{
                label: 'Units Sold',
                data: initialData.values,
                backgroundColor: [ // Provide enough colors or use a function
                    '#4285F4', '#EA4335', '#FBBC05', '#34A853', '#8F44AD',
                    '#1E88E5', '#D81B60', '#FFB300', '#00ACC1', '#7CB342'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y', // Keep bars horizontal
            scales: {
                x: {
                    beginAtZero: true
                }
            },
            plugins: {
                legend: {
                    display: false // Hide legend if only one dataset
                }
            }
        }
    });
}

function fetchAndUpdateTopProductsChart(period) {
    if (!productsChart) {
        console.error("Products chart instance not available for update.");
        return;
    }

    // Construct the URL with the period query parameter
    const url = `/pos/api/top-products-data/?period=${encodeURIComponent(period)}`;

    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data && data.labels && data.values) {
                // Update chart data
                productsChart.data.labels = data.labels;
                productsChart.data.datasets[0].data = data.values;
                productsChart.update(); // Redraw the chart
            } else {
                console.error("Invalid data format received from server:", data);
                // Optionally clear the chart or show a default state
                productsChart.data.labels = [];
                productsChart.data.datasets[0].data = [];
                productsChart.update();
            }
        })
        .catch(error => {
            console.error('Error fetching top products data:', error);
            // Optionally display an error message to the user on the chart
            // For now, just clear the chart
            productsChart.data.labels = [];
            productsChart.data.datasets[0].data = [];
            productsChart.update();
        });
}