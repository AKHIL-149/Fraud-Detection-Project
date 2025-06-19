// ===== DASHBOARD FUNCTIONALITY =====

class FraudDetectionDashboard {
    constructor() {
        this.refreshInterval = null;
        this.charts = {};
        this.metrics = {};
        this.isInitialized = false;
    }
    
    init() {
        console.log('🚀 Initializing Fraud Detection Dashboard...');
        
        // Initialize components
        this.initializeCharts();
        this.setupEventListeners();
        this.startRealTimeUpdates();
        
        // Load initial data
        this.loadDashboardData();
        
        this.isInitialized = true;
        console.log('✅ Dashboard initialized successfully');
    }
    
    initializeCharts() {
        // Initialize fraud trends chart
        this.initFraudTrendsChart();
        
        // Initialize fraud category pie chart
        this.initFraudCategoryChart();
        
        // Setup chart resize handler
        window.addEventListener('resize', () => {
            this.resizeCharts();
        });
    }
    
    initFraudTrendsChart() {
        const ctx = document.getElementById('fraudTrendsChart');
        if (!ctx) return;
        
        // Sample data for the last 24 hours
        const hours = Array.from({length: 24}, (_, i) => {
            const date = new Date();
            date.setHours(date.getHours() - (23 - i));
            return date.getHours().toString().padStart(2, '0') + ':00';
        });
        
        const fraudRates = Array.from({length: 24}, () => {
            return (Math.random() * 3 + 0.5).toFixed(2); // 0.5% to 3.5%
        });
        
        // Using Plotly for better interactivity
        const trace = {
            x: hours,
            y: fraudRates,
            type: 'scatter',
            mode: 'lines+markers',
            line: {
                color: '#dc3545',
                width: 3
            },
            marker: {
                color: '#dc3545',
                size: 6
            },
            fill: 'tonexty',
            fillcolor: 'rgba(220, 53, 69, 0.1)',
            name: 'Fraud Rate'
        };
        
        const layout = {
            title: {
                text: 'Fraud Rate Trend (24 Hours)',
                font: { size: 16 }
            },
            xaxis: {
                title: 'Hour',
                showgrid: true,
                gridcolor: '#f1f1f1'
            },
            yaxis: {
                title: 'Fraud Rate (%)',
                showgrid: true,
                gridcolor: '#f1f1f1'
            },
            plot_bgcolor: 'rgba(0,0,0,0)',
            paper_bgcolor: 'rgba(0,0,0,0)',
            margin: { l: 50, r: 20, t: 50, b: 50 },
            showlegend: false
        };
        
        const config = {
            displayModeBar: false,
            responsive: true
        };
        
        Plotly.newPlot('fraudTrendsChart', [trace], layout, config);
        this.charts.fraudTrends = true;
    }
    
    initFraudCategoryChart() {
        const ctx = document.getElementById('fraudCategoryChart');
        if (!ctx) return;
        
        const categories = ['Online', 'ATM', 'Retail', 'Gas Station', 'Restaurant'];
        const values = [35, 25, 20, 12, 8];
        const colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7'];
        
        const data = [{
            values: values,
            labels: categories,
            type: 'pie',
            marker: {
                colors: colors,
                line: {
                    color: '#FFFFFF',
                    width: 2
                }
            },
            textinfo: 'label+percent',
            textposition: 'outside',
            hovertemplate: '<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
        }];
        
        const layout = {
            title: {
                text: 'Fraud by Category',
                font: { size: 16 }
            },
            showlegend: false,
            margin: { l: 20, r: 20, t: 50, b: 20 },
            plot_bgcolor: 'rgba(0,0,0,0)',
            paper_bgcolor: 'rgba(0,0,0,0)'
        };
        
        const config = {
            displayModeBar: false,
            responsive: true
        };
        
        Plotly.newPlot('fraudCategoryChart', data, layout, config);
        this.charts.fraudCategory = true;
    }
    
    setupEventListeners() {
        // Refresh dashboard button
        const refreshBtn = document.getElementById('refresh-dashboard');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.refreshDashboard();
            });
        }
        
        // Model retrain button
        const retrainBtn = document.getElementById('retrain-model');
        if (retrainBtn) {
            retrainBtn.addEventListener('click', () => {
                this.handleModelRetrain();
            });
        }
        
        // Time range selectors
        document.querySelectorAll('[data-range]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const range = btn.dataset.range;
                this.changeTimeRange(range);
            });
        });
        
        // Chart type selectors
        document.querySelectorAll('[data-chart-type]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const chartType = btn.dataset.chartType;
                this.updateFraudTrendsChart(chartType);
            });
        });
    }
    
    async loadDashboardData() {
        try {
            // Load metrics
            await this.loadMetrics();
            
            // Load recent transactions
            await this.loadRecentTransactions();
            
            // Load recent alerts
            await this.loadRecentAlerts();
            
            // Update charts with new data
            await this.updateChartsData();
            
        } catch (error) {
            console.error('❌ Error loading dashboard data:', error);
            this.showNotification('Error loading dashboard data', 'error');
        }
    }
    
    async loadMetrics() {
        try {
            const response = await fetch('/api/analytics/metrics');
            const data = await response.json();
            
            this.updateMetricCards(data);
            this.updateModelPerformance(data.model_performance);
            
        } catch (error) {
            console.error('❌ Error loading metrics:', error);
        }
    }
    
    updateMetricCards(data) {
        const metrics = {
            'total-transactions': data.total_transactions || 0,
            'fraud-detected': data.fraud_detected || 0,
            'prevention-rate': data.prevention_rate || 0,
            'amount-protected': data.amount_protected || 0
        };
        
        Object.entries(metrics).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                // Remove loading spinner and update value
                if (typeof value === 'number') {
                    if (id === 'amount-protected') {
                        element.textContent = this.formatCurrency(value);
                    } else if (id === 'prevention-rate') {
                        element.textContent = value + '%';
                    } else {
                        element.textContent = value.toLocaleString();
                    }
                } else {
                    element.textContent = value;
                }
                
                // Add animation effect
                element.classList.add('metric-updated');
                setTimeout(() => {
                    element.classList.remove('metric-updated');
                }, 1000);
            }
        });
    }
    
    updateModelPerformance(performance) {
        if (!performance) return;
        
        const metrics = {
            'model-accuracy-dashboard': performance.accuracy,
            'model-precision-dashboard': performance.precision,
            'model-recall-dashboard': performance.recall,
            'model-f1-dashboard': performance.f1_score,
            'model-auc-dashboard': performance.auc_roc
        };
        
        Object.entries(metrics).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element && value !== undefined) {
                element.textContent = (value * 100).toFixed(1) + '%';
            }
        });
    }
    
    async loadRecentTransactions() {
        try {
            const response = await fetch('/api/transactions/recent?limit=10');
            const data = await response.json();
            
            this.updateRecentTransactionsTable(data.transactions || []);
            
        } catch (error) {
            console.error('❌ Error loading recent transactions:', error);
        }
    }
    
    updateRecentTransactionsTable(transactions) {
        const tbody = document.getElementById('recent-transactions-body');
        if (!tbody) return;
        
        if (transactions.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="5" class="text-center text-muted">
                        No recent transactions available
                    </td>
                </tr>
            `;
            return;
        }
        
        tbody.innerHTML = transactions.map(transaction => {
            const riskClass = this.getRiskBadgeClass(transaction.fraud_probability);
            const statusClass = transaction.is_fraud ? 'danger' : 'success';
            const statusText = transaction.is_fraud ? 'Fraud' : 'Legitimate';
            
            return `
                <tr class="transaction-row cursor-pointer" data-transaction-id="${transaction.transaction_id}">
                    <td>${this.formatTime(transaction.timestamp)}</td>
                    <td>${this.formatCurrency(transaction.amount)}</td>
                    <td>
                        <span class="badge bg-secondary">${transaction.merchant_category}</span>
                    </td>
                    <td>
                        <span class="badge ${riskClass}">
                            ${(transaction.fraud_probability * 100).toFixed(1)}%
                        </span>
                    </td>
                    <td>
                        <span class="badge bg-${statusClass}">${statusText}</span>
                    </td>
                </tr>
            `;
        }).join('');
        
        // Add click handlers for transaction details
        tbody.querySelectorAll('.transaction-row').forEach(row => {
            row.addEventListener('click', () => {
                const transactionId = row.dataset.transactionId;
                this.showTransactionDetails(transactionId);
            });
        });
    }
    
    async loadRecentAlerts() {
        try {
            const response = await fetch('/api/monitoring/alerts/recent?limit=5');
            const data = await response.json();
            
            this.updateRecentAlerts(data.alerts || []);
            
        } catch (error) {
            console.error('❌ Error loading recent alerts:', error);
        }
    }
    
    updateRecentAlerts(alerts) {
        const container = document.getElementById('recent-alerts');
        if (!container) return;
        
        if (alerts.length === 0) {
            container.innerHTML = `
                <div class="text-center p-4 text-muted">
                    <i class="fas fa-shield-alt fa-2x mb-3"></i>
                    <div>No recent fraud alerts</div>
                </div>
            `;
            return;
        }
        
        container.innerHTML = alerts.map(alert => {
            const severityClass = alert.severity === 'HIGH' ? 'danger' : 'warning';
            const icon = alert.severity === 'HIGH' ? 'fa-exclamation-triangle' : 'fa-exclamation-circle';
            
            return `
                <div class="alert alert-${severityClass} alert-dismissible fade show mb-2">
                    <div class="d-flex align-items-center">
                        <i class="fas ${icon} me-2"></i>
                        <div class="flex-grow-1">
                            <strong>Transaction ${alert.transaction_id}</strong><br>
                            <small>
                                Amount: ${this.formatCurrency(alert.amount)} • 
                                Risk: ${(alert.fraud_probability * 100).toFixed(1)}% • 
                                ${this.formatTime(alert.timestamp)}
                            </small>
                        </div>
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                </div>
            `;
        }).join('');
    }
    
    async updateChartsData() {
        try {
            // Update fraud trends chart with real data
            const response = await fetch('/api/analytics/fraud-trends?period=24h');
            const data = await response.json();
            
            if (data.trends && this.charts.fraudTrends) {
                this.updateFraudTrendsWithData(data.trends);
            }
            
            // Update category chart
            const categoryResponse = await fetch('/api/analytics/fraud-by-category');
            const categoryData = await categoryResponse.json();
            
            if (categoryData.categories && this.charts.fraudCategory) {
                this.updateFraudCategoryWithData(categoryData.categories);
            }
            
        } catch (error) {
            console.error('❌ Error updating charts:', error);
        }
    }
    
    updateFraudTrendsWithData(trendsData) {
        const trace = {
            x: trendsData.timestamps,
            y: trendsData.fraud_rates,
            type: 'scatter',
            mode: 'lines+markers',
            line: { color: '#dc3545', width: 3 },
            marker: { color: '#dc3545', size: 6 },
            fill: 'tonexty',
            fillcolor: 'rgba(220, 53, 69, 0.1)'
        };
        
        Plotly.redraw('fraudTrendsChart', [trace]);
    }
    
    updateFraudCategoryWithData(categoryData) {
        const data = [{
            values: categoryData.values,
            labels: categoryData.labels,
            type: 'pie',
            marker: {
                colors: ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7'],
                line: { color: '#FFFFFF', width: 2 }
            },
            textinfo: 'label+percent',
            textposition: 'outside'
        }];
        
        Plotly.redraw('fraudCategoryChart', data);
    }
    
    startRealTimeUpdates() {
        // Update dashboard every 30 seconds
        this.refreshInterval = setInterval(() => {
            if (document.visibilityState === 'visible') {
                this.loadMetrics();
                this.loadRecentTransactions();
            }
        }, 30000);
        
        // Listen for WebSocket events
        document.addEventListener('newTransaction', (event) => {
            this.handleNewTransaction(event.detail);
        });
        
        document.addEventListener('newAlert', (event) => {
            this.handleNewAlert(event.detail);
        });
    }
    
    handleNewTransaction(transaction) {
        // Add to recent transactions table
        this.prependToRecentTransactions(transaction);
        
        // Update live indicators
        this.updateLiveIndicators();
        
        // Update metrics counters
        this.incrementTransactionCount();
    }
    
    handleNewAlert(alert) {
        // Add to recent alerts
        this.prependToRecentAlerts(alert);
        
        // Update alert count
        this.incrementAlertCount();
        
        // Show notification for high-severity alerts
        if (alert.severity === 'HIGH') {
            this.showNotification(
                `High-risk fraud detected: ${this.formatCurrency(alert.amount)}`,
                'warning',
                5000
            );
        }
    }
    
    prependToRecentTransactions(transaction) {
        const tbody = document.getElementById('recent-transactions-body');
        if (!tbody) return;
        
        // Remove "no transactions" message if present
        const noDataRow = tbody.querySelector('td[colspan="5"]');
        if (noDataRow) {
            tbody.innerHTML = '';
        }
        
        const riskClass = this.getRiskBadgeClass(transaction.fraud_probability);
        const statusClass = transaction.is_fraud ? 'danger' : 'success';
        const statusText = transaction.is_fraud ? 'Fraud' : 'Legitimate';
        
        const newRow = document.createElement('tr');
        newRow.className = 'transaction-row cursor-pointer table-row-new';
        newRow.dataset.transactionId = transaction.transaction_id;
        newRow.innerHTML = `
            <td>${this.formatTime(transaction.timestamp)}</td>
            <td>${this.formatCurrency(transaction.amount)}</td>
            <td><span class="badge bg-secondary">${transaction.merchant_category}</span></td>
            <td><span class="badge ${riskClass}">${(transaction.fraud_probability * 100).toFixed(1)}%</span></td>
            <td><span class="badge bg-${statusClass}">${statusText}</span></td>
        `;
        
        // Add click handler
        newRow.addEventListener('click', () => {
            this.showTransactionDetails(transaction.transaction_id);
        });
        
        // Insert at the beginning
        tbody.insertBefore(newRow, tbody.firstChild);
        
        // Remove animation class after animation
        setTimeout(() => {
            newRow.classList.remove('table-row-new');
        }, 1000);
        
        // Keep only the last 10 rows
        while (tbody.children.length > 10) {
            tbody.removeChild(tbody.lastChild);
        }
    }
    
    prependToRecentAlerts(alert) {
        const container = document.getElementById('recent-alerts');
        if (!container) return;
        
        // Remove "no alerts" message if present
        const noAlertsMsg = container.querySelector('.text-center');
        if (noAlertsMsg) {
            container.innerHTML = '';
        }
        
        const severityClass = alert.severity === 'HIGH' ? 'danger' : 'warning';
        const icon = alert.severity === 'HIGH' ? 'fa-exclamation-triangle' : 'fa-exclamation-circle';
        
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${severityClass} alert-dismissible fade show mb-2 alert-new`;
        alertDiv.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="fas ${icon} me-2"></i>
                <div class="flex-grow-1">
                    <strong>Transaction ${alert.transaction_id}</strong><br>
                    <small>
                        Amount: ${this.formatCurrency(alert.amount)} • 
                        Risk: ${(alert.fraud_probability * 100).toFixed(1)}% • 
                        ${this.formatTime(alert.timestamp)}
                    </small>
                </div>
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        // Insert at the beginning
        container.insertBefore(alertDiv, container.firstChild);
        
        // Remove animation class after animation
        setTimeout(() => {
            alertDiv.classList.remove('alert-new');
        }, 1000);
        
        // Keep only the last 5 alerts
        while (container.children.length > 5) {
            container.removeChild(container.lastChild);
        }
    }
    
    // Utility methods
    getRiskBadgeClass(fraudProbability) {
        if (fraudProbability > 0.7) return 'bg-danger';
        if (fraudProbability > 0.3) return 'bg-warning';
        return 'bg-success';
    }
    
    formatCurrency(amount) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(amount);
    }
    
    formatTime(timestamp) {
        return new Date(timestamp).toLocaleTimeString();
    }
    
    showNotification(message, type = 'info', duration = 3000) {
        // Use the global notification system if available
        if (window.fraudApp && window.fraudApp.showNotification) {
            window.fraudApp.showNotification(message, type, duration);
        } else {
            console.log(`📢 ${type.toUpperCase()}: ${message}`);
        }
    }
    
    async refreshDashboard() {
        const refreshBtn = document.getElementById('refresh-dashboard');
        if (refreshBtn) {
            refreshBtn.classList.add('loading');
            refreshBtn.disabled = true;
        }
        
        try {
            await this.loadDashboardData();
            this.showNotification('Dashboard refreshed successfully', 'success');
        } catch (error) {
            this.showNotification('Error refreshing dashboard', 'error');
        } finally {
            if (refreshBtn) {
                refreshBtn.classList.remove('loading');
                refreshBtn.disabled = false;
            }
        }
    }
    
    async handleModelRetrain() {
        if (!confirm('Are you sure you want to retrain the fraud detection model? This may take several minutes.')) {
            return;
        }
        
        const retrainBtn = document.getElementById('retrain-model');
        if (retrainBtn) {
            retrainBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Retraining...';
            retrainBtn.disabled = true;
        }
        
        try {
            const response = await fetch('/api/models/retrain', { method: 'POST' });
            const result = await response.json();
            
            if (response.ok) {
                this.showNotification('Model retraining started successfully', 'success');
                // Reload model performance after a delay
                setTimeout(() => {
                    this.loadMetrics();
                }, 5000);
            } else {
                throw new Error(result.error || 'Retraining failed');
            }
        } catch (error) {
            this.showNotification('Error starting model retraining', 'error');
        } finally {
            if (retrainBtn) {
                retrainBtn.innerHTML = '<i class="fas fa-sync me-2"></i>Retrain Model';
                retrainBtn.disabled = false;
            }
        }
    }
    
    changeTimeRange(range) {
        console.log(`Changing time range to: ${range}`);
        
        // Update charts with new time range
        this.updateChartsTimeRange(range);
        
        // Update active button state
        document.querySelectorAll('[data-range]').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-range="${range}"]`)?.classList.add('active');
    }
    
    async updateChartsTimeRange(range) {
        try {
            const response = await fetch(`/api/analytics/fraud-trends?period=${range}`);
            const data = await response.json();
            
            if (data.trends && this.charts.fraudTrends) {
                this.updateFraudTrendsWithData(data.trends);
            }
        } catch (error) {
            console.error('❌ Error updating charts for time range:', error);
        }
    }
    
    updateFraudTrendsChart(chartType) {
        console.log(`Updating fraud trends chart to: ${chartType}`);
        
        // This would typically fetch different aggregated data
        // For now, we'll simulate different views
        let title, xAxisTitle;
        
        switch (chartType) {
            case 'hourly':
                title = 'Hourly Fraud Rate';
                xAxisTitle = 'Hour';
                break;
            case 'daily':
                title = 'Daily Fraud Rate';
                xAxisTitle = 'Day';
                break;
            case 'weekly':
                title = 'Weekly Fraud Rate';
                xAxisTitle = 'Week';
                break;
            default:
                return;
        }
        
        // Update chart layout
        const update = {
            'title.text': title,
            'xaxis.title': xAxisTitle
        };
        
        Plotly.relayout('fraudTrendsChart', update);
    }
    
    showTransactionDetails(transactionId) {
        // This would typically fetch detailed transaction data
        console.log(`Showing details for transaction: ${transactionId}`);
        
        // For now, show a simple modal or navigate to detail view
        if (window.fraudApp && window.fraudApp.showTransactionDetails) {
            window.fraudApp.showTransactionDetails(transactionId);
        }
    }
    
    updateLiveIndicators() {
        const liveStatus = document.getElementById('live-status');
        if (liveStatus) {
            liveStatus.classList.add('btn-pulse');
            setTimeout(() => {
                liveStatus.classList.remove('btn-pulse');
            }, 1000);
        }
    }
    
    incrementTransactionCount() {
        const countElement = document.getElementById('total-transactions');
        if (countElement) {
            const currentCount = parseInt(countElement.textContent.replace(/,/g, '')) || 0;
            countElement.textContent = (currentCount + 1).toLocaleString();
        }
    }
    
    incrementAlertCount() {
        const alertBadges = document.querySelectorAll('#alert-count, #sidebar-alert-count');
        alertBadges.forEach(badge => {
            const currentCount = parseInt(badge.textContent) || 0;
            badge.textContent = currentCount + 1;
            badge.style.display = 'inline';
        });
    }
    
    resizeCharts() {
        // Resize Plotly charts when window is resized
        if (this.charts.fraudTrends) {
            Plotly.Plots.resize('fraudTrendsChart');
        }
        if (this.charts.fraudCategory) {
            Plotly.Plots.resize('fraudCategoryChart');
        }
    }
    
    destroy() {
        // Clean up when dashboard is destroyed
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
        
        // Remove event listeners
        window.removeEventListener('resize', this.resizeCharts);
        
        console.log('🧹 Dashboard destroyed');
    }
}

// Export for global use
window.FraudDetectionDashboard = FraudDetectionDashboard;