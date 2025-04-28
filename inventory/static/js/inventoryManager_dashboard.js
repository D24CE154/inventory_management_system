// inventory/static/js/inventoryManager_dashboard.js
document.addEventListener('DOMContentLoaded', function() {
    // Initialize charts with data passed from the view
    initStockLevelChart();
    initTurnoverChart(); // Initializes with default period data ('30days')

    // Add event listener for turnover period selector
    const periodSelector = document.querySelector('#turnoverChart')?.closest('.chart-card')?.querySelector('.chart-actions select');
    if (periodSelector) {
        periodSelector.addEventListener('change', function() {
            // Map dropdown value to period key ('Last 30 Days' -> '30days', etc.)
            let periodKey = '30days'; // Default
            const selectedValue = this.value.toLowerCase();
            if (selectedValue.includes('90')) {
                periodKey = '90days';
            } else if (selectedValue.includes('year')) {
                periodKey = 'year';
            }
            fetchAndUpdateTurnoverChart(periodKey); // Fetch data for the selected period
        });
    } else {
        console.warn("Turnover chart period selector not found.");
    }
});

// --- Stock Level Chart ---
let stockChart = null; // Use let for reassignment

function initStockLevelChart() {
    const ctx = document.getElementById('stockLevelChart')?.getContext('2d');
    if (!ctx) {
        console.error("Stock Level Chart canvas not found.");
        return;
    }

    // Get data from the embedded JSON script tag
    let categoryData = [];
    try {
        const stockDataElement = document.getElementById('stock-by-category-data');
        const parsedData = JSON.parse(stockDataElement?.textContent || '[]');
        // Ensure data format is as expected by the chart
        categoryData = parsedData.map(item => ({
            category: item.name || 'Unknown', // Use name field from view context
            stock: item.stock || 0          // Use stock field from view context
        }));
    } catch (e) {
        console.error("Error parsing stock category data:", e);
        categoryData = []; // Fallback to empty data
    }

    const labels = categoryData.map(item => item.category);
    const data = categoryData.map(item => item.stock);

    // Destroy existing chart instance if it exists
    if (stockChart) {
        stockChart.destroy();
    }

    stockChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Current Stock',
                data: data,
                backgroundColor: '#1a73e8', // Example color
                borderColor: '#1a73e8',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Units in Stock'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Product Category'
                    }
                }
            },
            plugins: {
                legend: {
                    display: false // Hide legend if only one dataset
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `Stock: ${context.raw || 0}`;
                        }
                    }
                }
            }
        }
    });
}

// --- Turnover Chart ---
let turnoverChart = null; // Use let for reassignment

function initTurnoverChart() {
    const ctx = document.getElementById('turnoverChart')?.getContext('2d');
    if (!ctx) {
        console.error("Turnover Chart canvas not found.");
        return;
    }

    // Get initial data (e.g., for '30days') from the embedded JSON
    let initialTurnoverData;
    try {
        const turnoverDataElement = document.getElementById('turnover-data');
        initialTurnoverData = JSON.parse(turnoverDataElement?.textContent || '{}');
    } catch (e) {
        console.error("Error parsing initial turnover data:", e);
        initialTurnoverData = {}; // Fallback
    }

    // Use the default period data ('30days' from the view) or provide defaults
    const initialData = initialTurnoverData['30days'] || {
        labels: [],
        fast_moving: [],
        slow_moving: []
    };

    // Destroy existing chart instance if it exists
    if (turnoverChart) {
        turnoverChart.destroy();
    }

    turnoverChart = new Chart(ctx, {
        type: 'line', // Using line chart for turnover trends
        data: {
            labels: initialData.labels,
            datasets: [{
                label: 'Fast Moving', // Placeholder name
                data: initialData.fast_moving,
                borderColor: '#34A853', // Green
                backgroundColor: 'rgba(52, 168, 83, 0.1)',
                tension: 0.1,
                fill: true
            },
                {
                    label: 'Slow Moving', // Placeholder name
                    data: initialData.slow_moving,
                    borderColor: '#EA4335', // Red
                    backgroundColor: 'rgba(234, 67, 53, 0.1)',
                    tension: 0.1,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Turnover Metric (e.g., Units Sold)' // Adjust as needed
                    }
                }
            },
            plugins: {
                tooltip: {
                    mode: 'index',
                    intersect: false,
                },
                legend: {
                    position: 'top',
                }
            }
        }
    });
}

function fetchAndUpdateTurnoverChart(periodKey) {
    if (!turnoverChart) {
        console.error("Turnover chart instance not available for update.");
        return;
    }

    // Construct the URL to the Django API view
    // Assumes the view is mapped to '/inventory/api/turnover-data/' in urls.py
    const url = `/inventory/api/turnover-data/?period=${encodeURIComponent(periodKey)}`;

    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            // Check if the received data has the expected structure
            if (data && data.labels && data.fast_moving && data.slow_moving) {
                // Update chart data
                turnoverChart.data.labels = data.labels;
                turnoverChart.data.datasets[0].data = data.fast_moving; // Update fast moving
                turnoverChart.data.datasets[1].data = data.slow_moving; // Update slow moving
                turnoverChart.update(); // Redraw the chart
            } else {
                console.error("Invalid data format received from server for turnover:", data);
                // Optionally clear the chart or show a default state
                turnoverChart.data.labels = [];
                turnoverChart.data.datasets[0].data = [];
                turnoverChart.data.datasets[1].data = [];
                turnoverChart.update();
            }
        })
        .catch(error => {
            console.error('Error fetching turnover data:', error);
            // Optionally display an error message to the user on the chart
            // For now, just clear the chart
            turnoverChart.data.labels = [];
            turnoverChart.data.datasets[0].data = [];
            turnoverChart.data.datasets[1].data = [];
            turnoverChart.update();
        });
}