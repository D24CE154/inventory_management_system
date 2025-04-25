// inventory/static/js/inventoryManager_dashboard.js
document.addEventListener('DOMContentLoaded', function() {
    // Initialize charts
    initStockLevelChart();
    initTurnoverChart();

    // Add event listeners for period selector
    const periodSelector = document.querySelector('.chart-actions select');
    if (periodSelector) {
        periodSelector.addEventListener('change', function() {
            updateTurnoverChart(this.value.toLowerCase().replace(/\s+/g, '').includes('30') ? '30days' :
                this.value.toLowerCase().replace(/\s+/g, '').includes('90') ? '90days' : 'year');
        });
    }
});

// Stock Level Chart
function initStockLevelChart() {
    const ctx = document.getElementById('stockLevelChart').getContext('2d');

    // Get data from JSON element
    let categoryData = [];
    try {
        const stockByCategory = JSON.parse(document.getElementById('stock-by-category-data').textContent || '[]');
        categoryData = stockByCategory.map(item => ({
            category: item.name,
            stock: item.stock
        }));
    } catch (e) {
        console.error("Error parsing stock category data:", e);
        categoryData = [];
    }

    const labels = categoryData.map(item => item.category);
    const data = categoryData.map(item => item.stock);

    window.stockChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Current Stock',
                data: data,
                backgroundColor: '#1a73e8',
                barThickness: 30
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
                    display: false
                }
            }
        }
    });
}

// Turnover Chart
function initTurnoverChart() {
    const ctx = document.getElementById('turnoverChart').getContext('2d');

    // Get data from JSON element
    let turnoverData;
    try {
        turnoverData = JSON.parse(document.getElementById('turnover-data').textContent || '{}');
    } catch (e) {
        console.error("Error parsing turnover data:", e);
        turnoverData = {
            '30days': {
                'labels': ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
                'fast_moving': [14, 16, 19, 21],
                'slow_moving': [4, 5, 3, 2]
            }
        };
    }

    const data = turnoverData['30days'] || {
        labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
        fast_moving: [14, 16, 19, 21],
        slow_moving: [4, 5, 3, 2]
    };

    window.turnoverChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Fast Moving',
                data: data.fast_moving,
                borderColor: '#34a853',
                backgroundColor: 'rgba(52, 168, 83, 0.1)',
                tension: 0.4,
                fill: true
            },
                {
                    label: 'Slow Moving',
                    data: data.slow_moving,
                    borderColor: '#fbbc05',
                    backgroundColor: 'rgba(251, 188, 5, 0.1)',
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
                    title: {
                        display: true,
                        text: 'Turnover Rate (%)'
                    }
                }
            },
            plugins: {
                tooltip: {
                    mode: 'index',
                    intersect: false
                },
                hover: {
                    mode: 'nearest',
                    intersect: true
                }
            }
        }
    });
}

function updateTurnoverChart(period) {
    // Default data if JSON data is not available
    let turnoverData;
    try {
        turnoverData = JSON.parse(document.getElementById('turnover-data').textContent || '{}');
    } catch (e) {
        turnoverData = {};
    }

    // If period data doesn't exist, create sample data
    if (!turnoverData[period]) {
        turnoverData[period] = period === '30days' ? {
            labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
            fast_moving: [14, 16, 19, 21],
            slow_moving: [4, 5, 3, 2]
        } : period === '90days' ? {
            labels: ['Month 1', 'Month 2', 'Month 3'],
            fast_moving: [12, 15, 18],
            slow_moving: [5, 4, 3]
        } : {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            fast_moving: [10, 12, 15, 14, 16, 18, 20, 22, 21, 19, 18, 20],
            slow_moving: [6, 5, 4, 5, 3, 4, 3, 2, 3, 4, 5, 4]
        };
    }

    const data = turnoverData[period];

    window.turnoverChart.data.labels = data.labels;
    window.turnoverChart.data.datasets[0].data = data.fast_moving;
    window.turnoverChart.data.datasets[1].data = data.slow_moving;
    window.turnoverChart.update();
}