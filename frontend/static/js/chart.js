// ===== CHARTS AND VISUALIZATIONS =====

class ChartManager {
    constructor() {
        this.charts = new Map();
        this.defaultConfig = {
            displayModeBar: false,
            responsive: true,
            displaylogo: false
        };
    }
    
    // Base chart creation method
    createChart(containerId, data, layout, config = {}) {
        const finalConfig = { ...this.defaultConfig, ...config };
        const finalLayout = {
            plot_bgcolor: 'rgba(0,0,0,0)',
            paper_bgcolor: 'rgba(0,0,0,0)',
            font: { family: 'Segoe UI, Arial, sans-serif', size: 12 },
            ...layout
        };
        
        try {
            Plotly.newPlot(containerId, data, finalLayout, finalConfig);
            this.charts.set(containerId, { data, layout: finalLayout, config: finalConfig });
            return true;
        } catch (error) {
            console.error(`Failed to create chart ${containerId}:`, error);
            return false;
        }
    }
    
    // Update existing chart
    updateChart(containerId, newData, newLayout = {}) {
        try {
            if (newData) {
                Plotly.redraw(containerId, newData);
            }
            if (Object.keys(newLayout).length > 0) {
                Plotly.relayout(containerId, newLayout);
            }
            return true;
        } catch (error) {
            console.error(`Failed to update chart ${containerId}:`, error);
            return false;
        }
    }
    
    // Resize all charts
    resizeAll() {
        this.charts.forEach((_, containerId) => {
            try {
                Plotly.Plots.resize(containerId);
            } catch (error) {
                console.warn(`Failed to resize chart ${containerId}:`, error);
            }
        });
    }
    
    // Remove chart
    removeChart(containerId) {
        try {
            Plotly.purge(containerId);
            this.charts.delete(containerId);
        } catch (error) {
            console.error(`Failed to remove chart ${containerId}:`, error);
        }
    }
}

// Real-time Fraud Chart for monitoring page
class RealtimeFraudChart {
    constructor(containerId) {
        this.containerId = containerId;
        this.maxDataPoints = 50;
        this.data = {
            timestamps: [],
            fraudRates: [],
            transactionCounts: []
        };
        
        this.init();
    }
    
    init() {
        // Initialize with empty data
        const trace1 = {
            x: [],
            y: [],
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Fraud Rate (%)',
            line: { color: '#dc3545', width: 2 },
            yaxis: 'y'
        };
        
        const trace2 = {
            x: [],
            y: [],
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Transaction Count',
            line: { color: '#28a745', width: 2 },
            yaxis: 'y2',
            visible: 'legendonly'
        };
        
        const layout = {
            title: 'Real-time Fraud Detection',
            xaxis: {
                title: 'Time',
                type: 'date'
            },
            yaxis: {
                title: 'Fraud Rate (%)',
                side: 'left'
            },
            yaxis2: {
                title: 'Transaction Count',
                side: 'right',
                overlaying: 'y'
            },
            legend: {
                x: 0,
                y: 1.1,
                orientation: 'h'
            },
            margin: { l: 60, r: 60, t: 50, b: 50 }
        };
        
        Plotly.newPlot(this.containerId, [trace1, trace2], layout, {
            displayModeBar: false,
            responsive: true
        });
    }
    
    updateData(transaction) {
        const now = new Date();
        
        // Add new data point
        this.data.timestamps.push(now);
        
        // Calculate current fraud rate (simplified)
        const recentTransactions = this.data.transactionCounts.slice(-10);
        const currentFraudRate = transaction.fraud_probability * 100;
        this.data.fraudRates.push(currentFraudRate);
        this.data.transactionCounts.push(1);
        
        // Limit data points
        if (this.data.timestamps.length > this.maxDataPoints) {
            this.data.timestamps.shift();
            this.data.fraudRates.shift();
            this.data.transactionCounts.shift();
        }
        
        // Update chart
        const update = {
            x: [this.data.timestamps],
            y: [this.data.fraudRates]
        };
        
        Plotly.redraw(this.containerId, [
            {
                x: this.data.timestamps,
                y: this.data.fraudRates,
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Fraud Rate (%)',
                line: { color: '#dc3545', width: 2 }
            }
        ]);
    }
}

// Volume Gauge Chart
class VolumeGauge {
    constructor(containerId) {
        this.containerId = containerId;
        this.currentVolume = 0;
        this.maxVolume = 1000; // transactions per hour
        
        this.init();
    }
    
    init() {
        const data = [{
            type: "indicator",
            mode: "gauge+number+delta",
            value: this.currentVolume,
            domain: { x: [0, 1], y: [0, 1] },
            title: { text: "Transactions/Hour" },
            delta: { reference: 500 },
            gauge: {
                axis: { range: [null, this.maxVolume] },
                bar: { color: "#1f77b4" },
                steps: [
                    { range: [0, 250], color: "#f0f0f0" },
                    { range: [250, 500], color: "#d0d0d0" },
                    { range: [500, 750], color: "#b0b0b0" },
                    { range: [750, 1000], color: "#909090" }
                ],
                threshold: {
                    line: { color: "red", width: 4 },
                    thickness: 0.75,
                    value: 900
                }
            }
        }];
        
        const layout = {
            margin: { t: 25, b: 25, l: 25, r: 25 },
            font: { size: 12 }
        };
        
        Plotly.newPlot(this.containerId, data, layout, {
            displayModeBar: false,
            responsive: true
        });
    }
    
    updateVolume(newVolume = null) {
        if (newVolume !== null) {
            this.currentVolume = newVolume;
        } else {
            // Increment by 1
            this.currentVolume++;
        }
        
        const update = {
            'value': this.currentVolume
        };
        
        Plotly.restyle(this.containerId, update, [0]);
    }
}

// Risk Distribution Chart
class RiskDistributionChart {
    constructor(containerId) {
        this.containerId = containerId;
        this.riskBuckets = {
            'low': 0,      // 0-30%
            'medium': 0,   // 30-70%
            'high': 0      // 70-100%
        };
        
        this.init();
    }
    
    init() {
        const data = [{
            x: ['Low Risk', 'Medium Risk', 'High Risk'],
            y: [0, 0, 0],
            type: 'bar',
            marker: {
                color: ['#28a745', '#ffc107', '#dc3545'],
                opacity: 0.8
            },
            text: ['0', '0', '0'],
            textposition: 'auto'
        }];
        
        const layout = {
            title: 'Risk Distribution',
            xaxis: { title: 'Risk Level' },
            yaxis: { title: 'Count' },
            margin: { l: 50, r: 20, t: 50, b: 50 }
        };
        
        Plotly.newPlot(this.containerId, data, layout, {
            displayModeBar: false,
            responsive: true
        });
    }
    
    addDataPoint(riskScore) {
        // Categorize risk score
        let category;
        if (riskScore < 0.3) {
            category = 'low';
        } else if (riskScore < 0.7) {
            category = 'medium';
        } else {
            category = 'high';
        }
        
        // Update bucket count
        this.riskBuckets[category]++;
        
        // Update chart
        const update = {
            y: [[
                this.riskBuckets.low,
                this.riskBuckets.medium,
                this.riskBuckets.high
            ]],
            text: [[
                this.riskBuckets.low.toString(),
                this.riskBuckets.medium.toString(),
                this.riskBuckets.high.toString()
            ]]
        };
        
        Plotly.restyle(this.containerId, update, [0]);
    }
    
    reset() {
        this.riskBuckets = { low: 0, medium: 0, high: 0 };
        this.addDataPoint(0); // This will update the chart with zeros
    }
}

// Advanced Analytics Charts
class AdvancedAnalyticsChart {
    constructor(containerId) {
        this.containerId = containerId;
        this.currentView = 'correlation';
    }
    
    showCorrelationMatrix() {
        const features = ['Amount', 'Hour', 'Merchant Risk', 'Geographic Risk', 'Device Risk', 'Transaction Velocity'];
        const correlationMatrix = [
            [1.00, 0.12, 0.34, 0.28, 0.15, 0.67],
            [0.12, 1.00, 0.08, 0.19, 0.25, 0.14],
            [0.34, 0.08, 1.00, 0.45, 0.32, 0.28],
            [0.28, 0.19, 0.45, 1.00, 0.23, 0.31],
            [0.15, 0.25, 0.32, 0.23, 1.00, 0.18],
            [0.67, 0.14, 0.28, 0.31, 0.18, 1.00]
        ];
        
        const data = [{
            z: correlationMatrix,
            x: features,
            y: features,
            type: 'heatmap',
            colorscale: [
                [0, '#3B82F6'],
                [0.5, '#FFFFFF'],
                [1, '#EF4444']
            ],
            zmid: 0,
            showscale: true,
            colorbar: {
                title: 'Correlation',
                titleside: 'right'
            }
        }];
        
        const layout = {
            title: 'Feature Correlation Matrix',
            xaxis: { 
                title: 'Features',
                tickangle: -45
            },
            yaxis: { 
                title: 'Features'
            },
            margin: { l: 120, r: 80, t: 60, b: 120 }
        };
        
        Plotly.newPlot(this.containerId, data, layout, {
            displayModeBar: false,
            responsive: true
        });
    }
    
    showCohortAnalysis() {
        const weeks = ['Week 1', 'Week 2', 'Week 3', 'Week 4'];
        const cohorts = ['Cohort 1', 'Cohort 2', 'Cohort 3', 'Cohort 4'];
        
        const retentionRates = [
            [100, 85, 72, 68],
            [100, 88, 75, 71],
            [100, 90, 78, 74],
            [100, 87, 76, 72]
        ];
        
        const data = [{
            z: retentionRates,
            x: weeks,
            y: cohorts,
            type: 'heatmap',
            colorscale: 'Viridis',
            showscale: true,
            colorbar: {
                title: 'Retention %',
                titleside: 'right'
            }
        }];
        
        const layout = {
            title: 'Customer Cohort Analysis',
            xaxis: { title: 'Time Period' },
            yaxis: { title: 'Customer Cohort' },
            margin: { l: 80, r: 80, t: 60, b: 50 }
        };
        
        Plotly.newPlot(this.containerId, data, layout, {
            displayModeBar: false,
            responsive: true
        });
    }
    
    showFraudFunnel() {
        const stages = ['Total Transactions', 'Flagged for Review', 'Manual Investigation', 'Confirmed Fraud', 'Action Taken'];
        const values = [10000, 500, 300, 150, 140];
        const colors = ['#E5E7EB', '#FDE68A', '#FCD34D', '#F59E0B', '#D97706'];
        
        const data = [{
            type: 'funnel',
            y: stages,
            x: values,
            textinfo: 'value+percent initial',
            marker: {
                color: colors
            }
        }];
        
        const layout = {
            title: 'Fraud Detection Funnel',
            margin: { l: 150, r: 50, t: 60, b: 50 }
        };
        
        Plotly.newPlot(this.containerId, data, layout, {
            displayModeBar: false,
            responsive: true
        });
    }
    
    switchView(viewType) {
        this.currentView = viewType;
        
        switch (viewType) {
            case 'correlation':
                this.showCorrelationMatrix();
                break;
            case 'cohort':
                this.showCohortAnalysis();
                break;
            case 'funnel':
                this.showFraudFunnel();
                break;
            default:
                console.warn(`Unknown view type: ${viewType}`);
        }
    }
}

// Geographic Heat Map
class GeographicHeatMap {
    constructor(containerId) {
        this.containerId = containerId;
        this.init();
    }
    
    init() {
        // Sample geographic data
        const locationData = [
            { country: 'USA', fraudRate: 1.2, totalTransactions: 50000 },
            { country: 'Canada', fraudRate: 0.8, totalTransactions: 8000 },
            { country: 'UK', fraudRate: 1.5, totalTransactions: 12000 },
            { country: 'Germany', fraudRate: 0.9, totalTransactions: 9000 },
            { country: 'France', fraudRate: 1.1, totalTransactions: 7500 },
            { country: 'International', fraudRate: 3.2, totalTransactions: 5000 }
        ];
        
        const data = [{
            x: locationData.map(d => d.country),
            y: locationData.map(d => d.fraudRate),
            type: 'bar',
            marker: {
                color: locationData.map(d => d.fraudRate),
                colorscale: [
                    [0, '#28a745'],
                    [0.5, '#ffc107'],
                    [1, '#dc3545']
                ],
                showscale: true,
                colorbar: {
                    title: 'Fraud Rate (%)',
                    titleside: 'right'
                }
            },
            text: locationData.map(d => `${d.fraudRate}%`),
            textposition: 'auto',
            hovertemplate: '<b>%{x}</b><br>Fraud Rate: %{y}%<br>Total Transactions: %{customdata}<extra></extra>',
            customdata: locationData.map(d => d.totalTransactions.toLocaleString())
        }];
        
        const layout = {
            title: 'Fraud Rate by Location',
            xaxis: { title: 'Location' },
            yaxis: { title: 'Fraud Rate (%)' },
            margin: { l: 60, r: 80, t: 60, b: 100 }
        };
        
        Plotly.newPlot(this.containerId, data, layout, {
            displayModeBar: false,
            responsive: true
        });
    }
    
    updateData(newLocationData) {
        const update = {
            x: [newLocationData.map(d => d.country)],
            y: [newLocationData.map(d => d.fraudRate)],
            'marker.color': [newLocationData.map(d => d.fraudRate)],
            text: [newLocationData.map(d => `${d.fraudRate}%`)],
            customdata: [newLocationData.map(d => d.totalTransactions.toLocaleString())]
        };
        
        Plotly.restyle(this.containerId, update, [0]);
    }
}

// Time Series Chart for Trends
class TimeSeriesChart {
    constructor(containerId, options = {}) {
        this.containerId = containerId;
        this.options = {
            title: 'Time Series Analysis',
            yAxisTitle: 'Value',
            showLegend: true,
            ...options
        };
        
        this.series = [];
    }
    
    addSeries(name, data, color = null) {
        const seriesData = {
            x: data.timestamps,
            y: data.values,
            type: 'scatter',
            mode: 'lines+markers',
            name: name,
            line: {
                color: color || this.getRandomColor(),
                width: 2
            },
            marker: { size: 4 }
        };
        
        this.series.push(seriesData);
        this.render();
    }
    
    render() {
        const layout = {
            title: this.options.title,
            xaxis: {
                title: 'Time',
                type: 'date'
            },
            yaxis: {
                title: this.options.yAxisTitle
            },
            showlegend: this.options.showLegend,
            legend: {
                x: 0,
                y: 1.1,
                orientation: 'h'
            },
            margin: { l: 60, r: 20, t: 60, b: 50 }
        };
        
        Plotly.newPlot(this.containerId, this.series, layout, {
            displayModeBar: false,
            responsive: true
        });
    }
    
    updateSeries(seriesIndex, newData) {
        if (seriesIndex >= 0 && seriesIndex < this.series.length) {
            const update = {
                x: [newData.timestamps],
                y: [newData.values]
            };
            
            Plotly.restyle(this.containerId, update, [seriesIndex]);
        }
    }
    
    getRandomColor() {
        const colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F'];
        return colors[Math.floor(Math.random() * colors.length)];
    }
    
    clear() {
        this.series = [];
        Plotly.purge(this.containerId);
    }
}

// Chart Utilities
const ChartUtils = {
    // Generate color palette
    getColorPalette(count) {
        const colors = [
            '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
            '#DDA0DD', '#98D8C8', '#F7DC6F', '#85C1E9', '#F8C471'
        ];
        
        if (count <= colors.length) {
            return colors.slice(0, count);
        }
        
        // Generate additional colors if needed
        const additionalColors = [];
        for (let i = colors.length; i < count; i++) {
            additionalColors.push(this.generateRandomColor());
        }
        
        return [...colors, ...additionalColors];
    },
    
    // Generate random color
    generateRandomColor() {
        const hue = Math.floor(Math.random() * 360);
        return `hsl(${hue}, 70%, 60%)`;
    },
    
    // Format numbers for charts
    formatNumber(num, decimals = 1) {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(decimals) + 'M';
        } else if (num >= 1000) {
            return (num / 1000).toFixed(decimals) + 'K';
        }
        return num.toFixed(decimals);
    },
    
    // Format percentage
    formatPercentage(value, decimals = 1) {
        return (value * 100).toFixed(decimals) + '%';
    },
    
    // Generate sample time series data
    generateTimeSeriesData(days = 30, baseValue = 100, volatility = 0.1) {
        const data = [];
        const now = new Date();
        
        for (let i = 0; i < days; i++) {
            const date = new Date(now.getTime() - (days - i - 1) * 24 * 60 * 60 * 1000);
            const randomChange = (Math.random() - 0.5) * volatility;
            const value = baseValue * (1 + randomChange);
            
            data.push({
                timestamp: date.toISOString(),
                value: Math.max(0, value)
            });
        }
        
        return {
            timestamps: data.map(d => d.timestamp),
            values: data.map(d => d.value)
        };
    }
};

// Global chart manager instance
window.chartManager = new ChartManager();

// Handle window resize for all charts
window.addEventListener('resize', () => {
    window.chartManager.resizeAll();
});

// Export classes for use in other modules
window.RealtimeFraudChart = RealtimeFraudChart;
window.VolumeGauge = VolumeGauge;
window.RiskDistributionChart = RiskDistributionChart;
window.AdvancedAnalyticsChart = AdvancedAnalyticsChart;
window.GeographicHeatMap = GeographicHeatMap;
window.TimeSeriesChart = TimeSeriesChart;
window.ChartUtils = ChartUtils;