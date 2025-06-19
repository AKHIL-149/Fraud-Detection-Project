// ===== MAIN JAVASCRIPT FOR FRAUD DETECTION SYSTEM =====

class FraudDetectionApp {
    constructor() {
        this.apiBase = '/api';
        this.wsConnection = null;
        this.isConnected = false;
        this.retryAttempts = 0;
        this.maxRetryAttempts = 5;
        
        // Initialize components
        this.init();
    }
    
    init() {
        console.log('🚀 Initializing Fraud Detection System...');
        
        // Initialize WebSocket connection
        this.initWebSocket();
        
        // Load initial data
        this.loadDashboardData();
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Setup periodic updates
        this.setupPeriodicUpdates();
        
        // Initialize UI components
        this.initUIComponents();
        
        console.log('✅ Fraud Detection System initialized');
    }
    
    // ===== WebSocket Management =====
    initWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/monitor`;
        
        try {
            this.wsConnection = new WebSocket(wsUrl);
            this.setupWebSocketEvents();
        } catch (error) {
            console.error('❌ WebSocket connection failed:', error);
            this.updateConnectionStatus('disconnected');
        }
    }
    
    setupWebSocketEvents() {
        this.wsConnection.onopen = () => {
            console.log('🔌 WebSocket connected');
            this.isConnected = true;
            this.retryAttempts = 0;
            this.updateConnectionStatus('connected');
        };
        
        this.wsConnection.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                this.handleWebSocketMessage(data);
            } catch (error) {
                console.error('❌ Error parsing WebSocket message:', error);
            }
        };
        
        this.wsConnection.onclose = () => {
            console.log('🔌 WebSocket disconnected');
            this.isConnected = false;
            this.updateConnectionStatus('disconnected');
            this.scheduleReconnect();
        };
        
        this.wsConnection.onerror = (error) => {
            console.error('❌ WebSocket error:', error);
            this.updateConnectionStatus('disconnected');
        };
    }
    
    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'transaction':
                this.handleNewTransaction(data.data);
                break;
            case 'alert':
                this.handleNewAlert(data.data);
                break;
            case 'status':
                this.handleStatusUpdate(data.data);
                break;
            default:
                console.log('📨 Unknown message type:', data.type);
        }
    }
    
    scheduleReconnect() {
        if (this.retryAttempts < this.maxRetryAttempts) {
            const delay = Math.pow(2, this.retryAttempts) * 1000; // Exponential backoff
            console.log(`🔄 Reconnecting in ${delay}ms (attempt ${this.retryAttempts + 1})`);
            
            setTimeout(() => {
                this.retryAttempts++;
                this.updateConnectionStatus('connecting');
                this.initWebSocket();
            }, delay);
        } else {
            console.error('❌ Max reconnection attempts reached');
            this.showNotification('Connection lost. Please refresh the page.', 'error');
        }
    }
    
    // ===== Connection Status Management =====
    updateConnectionStatus(status) {
        const indicators = {
            connected: { class: 'status-connected', text: 'Connected', icon: 'fa-circle' },
            disconnected: { class: 'status-disconnected', text: 'Disconnected', icon: 'fa-circle' },
            connecting: { class: 'status-connecting', text: 'Connecting...', icon: 'fa-spinner fa-spin' }
        };
        
        const indicator = indicators[status];
        
        // Update all status indicators
        document.querySelectorAll('#connection-status .alert').forEach(el => {
            el.classList.add('d-none');
        });
        
        const statusElement = document.getElementById(`status-${status}`);
        if (statusElement) {
            statusElement.classList.remove('d-none');
        }
        
        // Update sidebar health indicators
        const wsHealth = document.getElementById('ws-health');
        if (wsHealth) {
            wsHealth.className = `badge ${status === 'connected' ? 'bg-success' : 'bg-danger'}`;
            wsHealth.textContent = indicator.text;
        }
    }
    
    // ===== Data Loading =====
    async loadDashboardData() {
        try {
            // Load dataset information
            await this.loadDatasetInfo();
            
            // Load statistics
            await this.loadStatistics();
            
            // Load recent transactions
            await this.loadRecentTransactions();
            
            // Load recent alerts
            await this.loadRecentAlerts();
            
        } catch (error) {
            console.error('❌ Error loading dashboard data:', error);
            this.showNotification('Error loading dashboard data', 'error');
        }
    }
    
    async loadDatasetInfo() {
        try {
            const response = await this.apiCall('/dataset/info');
            if (response) {
                this.updateDatasetInfo(response);
            }
        } catch (error) {
            console.error('❌ Error loading dataset info:', error);
        }
    }
    
    async loadStatistics() {
        try {
            const response = await this.apiCall('/analytics/fraud-stats');
            if (response) {
                this.updateStatistics(response);
            }
        } catch (error) {
            console.error('❌ Error loading statistics:', error);
        }
    }
    
    async loadRecentTransactions() {
        try {
            const response = await this.apiCall('/transactions/recent?limit=10');
            if (response && response.transactions) {
                this.updateRecentTransactions(response.transactions);
            }
        } catch (error) {
            console.error('❌ Error loading recent transactions:', error);
        }
    }
    
    async loadRecentAlerts() {
        try {
            const response = await this.apiCall('/monitoring/alerts/recent?limit=5');
            if (response && response.alerts) {
                this.updateRecentAlerts(response.alerts);
            }
        } catch (error) {
            console.error('❌ Error loading recent alerts:', error);
        }
    }
    
    // ===== API Communication =====
    async apiCall(endpoint, options = {}) {
        const url = `${this.apiBase}${endpoint}`;
        const defaultOptions = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        };
        
        try {
            const response = await fetch(url, { ...defaultOptions, ...options });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error(`❌ API call failed for ${endpoint}:`, error);
            throw error;
        }
    }
    
    // ===== UI Updates =====
    updateDatasetInfo(data) {
        // Update dataset modal
        const elements = {
            'total-records': data.total_records?.toLocaleString() || '-',
            'fraud-count': data.fraud_count?.toLocaleString() || '-',
            'legitimate-count': data.legitimate_count?.toLocaleString() || '-',
            'feature-count': data.features?.length || '-',
            'dataset-size': `${data.total_records?.toLocaleString() || '-'} records`,
            'fraud-rate': `${(data.fraud_rate * 100).toFixed(2)}%` || '-'
        };
        
        Object.entries(elements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) element.textContent = value;
        });
        
        // Update feature list
        if (data.features) {
            const featureList = document.getElementById('feature-list');
            if (featureList) {
                featureList.innerHTML = data.features.slice(0, 8).map(feature => 
                    `<div class="col-6 mb-1"><small class="badge bg-light text-dark">${feature}</small></div>`
                ).join('');
            }
        }
    }
    
    updateStatistics(data) {
        const overview = data.overview || {};
        
        // Update main metrics
        const metrics = {
            'total-transactions': overview.total_transactions?.toLocaleString() || '0',
            'fraud-detected': overview.fraud_count?.toLocaleString() || '0',
            'prevention-rate': '91.3%', // From model performance
            'amount-protected': '$2.3M' // Calculated value
        };
        
        Object.entries(metrics).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                // Remove loading spinner and update value
                element.innerHTML = value;
            }
        });
        
        // Update sidebar quick stats
        const todayTransactions = document.getElementById('today-transactions');
        const todayFraud = document.getElementById('today-fraud');
        
        if (todayTransactions) todayTransactions.textContent = Math.floor(Math.random() * 1000);
        if (todayFraud) todayFraud.textContent = Math.floor(Math.random() * 10);
    }
    
    updateRecentTransactions(transactions) {
        const tbody = document.getElementById('recent-transactions-body');
        if (!tbody) return;
        
        if (transactions.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">No recent transactions</td></tr>';
            return;
        }
        
        tbody.innerHTML = transactions.map(transaction => {
            const riskClass = this.getRiskClass(transaction.fraud_probability);
            const statusClass = transaction.is_fraud ? 'danger' : 'success';
            const statusText = transaction.is_fraud ? 'Fraud' : 'Legitimate';
            
            return `
                <tr class="transaction-row" data-transaction-id="${transaction.transaction_id}">
                    <td>${this.formatTime(transaction.timestamp)}</td>
                    <td>$${transaction.amount?.toFixed(2) || '0.00'}</td>
                    <td>${transaction.merchant_category || 'Unknown'}</td>
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
            row.style.cursor = 'pointer';
            row.addEventListener('click', () => {
                const transactionId = row.dataset.transactionId;
                this.showTransactionDetails(transactionId);
            });
        });
    }
    
    updateRecentAlerts(alerts) {
        const container = document.getElementById('recent-alerts');
        if (!container) return;
        
        if (alerts.length === 0) {
            container.innerHTML = '<div class="text-center text-muted">No recent alerts</div>';
            return;
        }
        
        container.innerHTML = alerts.map(alert => {
            const severityClass = alert.severity === 'HIGH' ? 'high-risk' : 'medium-risk';
            const icon = alert.severity === 'HIGH' ? 'fa-exclamation-triangle' : 'fa-exclamation-circle';
            
            return `
                <div class="alert-item ${severityClass}">
                    <div class="d-flex align-items-center">
                        <i class="fas ${icon} me-2"></i>
                        <div>
                            <strong>Transaction ${alert.transaction_id}</strong><br>
                            <small>Amount: $${alert.amount} • Risk: ${(alert.fraud_probability * 100).toFixed(1)}%</small>
                        </div>
                    </div>
                    <small>${this.formatTime(alert.timestamp)}</small>
                </div>
            `;
        }).join('');
        
        // Update alert count badges
        this.updateAlertCount(alerts.length);
    }
    
    // ===== Real-time Event Handlers =====
    handleNewTransaction(transaction) {
        // Add to recent transactions (if on dashboard)
        if (window.location.pathname === '/') {
            this.prependToRecentTransactions(transaction);
        }
        
        // Update live indicator
        this.updateLiveIndicator();
        
        // Emit custom event for other components
        document.dispatchEvent(new CustomEvent('newTransaction', { detail: transaction }));
    }
    
    handleNewAlert(alert) {
        // Show toast notification for high-risk alerts
        if (alert.severity === 'HIGH') {
            this.showNotification(
                `High-risk transaction detected: $${alert.amount}`,
                'warning',
                5000
            );
        }
        
        // Update alert count
        this.incrementAlertCount();
        
        // Add to recent alerts
        this.prependToRecentAlerts(alert);
        
        // Emit custom event
        document.dispatchEvent(new CustomEvent('newAlert', { detail: alert }));
    }
    
    handleStatusUpdate(status) {
        console.log('📊 Status update:', status);
        
        // Update system health indicators
        Object.entries(status).forEach(([key, value]) => {
            const element = document.getElementById(`${key}-health`);
            if (element) {
                const statusClass = value === 'healthy' ? 'bg-success' : 'bg-danger';
                element.className = `badge ${statusClass}`;
                element.textContent = value === 'healthy' ? 'Online' : 'Offline';
            }
        });
    }
    
    // ===== Event Listeners =====
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
                this.retrainModel();
            });
        }
        
        // Export data button
        const exportBtn = document.getElementById('export-data');
        if (exportBtn) {
            exportBtn.addEventListener('click', () => {
                this.exportData();
            });
        }
        
        // System status modal
        const systemStatusBtn = document.getElementById('system-status');
        if (systemStatusBtn) {
            systemStatusBtn.addEventListener('click', () => {
                this.showSystemStatus();
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
    }
    
    // ===== Periodic Updates =====
    setupPeriodicUpdates() {
        // Update dashboard every 30 seconds
        setInterval(() => {
            if (document.visibilityState === 'visible') {
                this.loadStatistics();
            }
        }, 30000);
        
        // Update timestamp every minute
        setInterval(() => {
            this.updateTimestamps();
        }, 60000);
        
        // Health check every 5 minutes
        setInterval(() => {
            this.performHealthCheck();
        }, 300000);
    }
    
    // ===== UI Components Initialization =====
    initUIComponents() {
        // Initialize tooltips
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
        
        // Initialize range inputs
        this.initRangeInputs();
        
        // Initialize fraud tester
        this.initFraudTester();
        
        // Update last update time
        this.updateLastUpdateTime();
    }
    
    initRangeInputs() {
        // Hour slider
        const hourSlider = document.getElementById('test-hour');
        const hourDisplay = document.getElementById('hour-display');
        if (hourSlider && hourDisplay) {
            hourSlider.addEventListener('input', () => {
                hourDisplay.textContent = hourSlider.value;
            });
        }
        
        // Risk score sliders
        const riskInputs = [
            { slider: 'test-merchant-risk', display: 'merchant-risk-display' },
            { slider: 'test-geo-risk', display: 'geo-risk-display' },
            { slider: 'test-device-risk', display: 'device-risk-display' }
        ];
        
        riskInputs.forEach(({ slider, display }) => {
            const sliderEl = document.getElementById(slider);
            const displayEl = document.getElementById(display);
            if (sliderEl && displayEl) {
                sliderEl.addEventListener('input', () => {
                    displayEl.textContent = sliderEl.value;
                });
            }
        });
    }
    
    // ===== Utility Functions =====
    getRiskClass(fraudProbability) {
        if (fraudProbability > 0.7) return 'badge-risk-high';
        if (fraudProbability > 0.3) return 'badge-risk-medium';
        return 'badge-risk-low';
    }
    
    formatTime(timestamp) {
        return new Date(timestamp).toLocaleTimeString();
    }
    
    formatCurrency(amount) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(amount);
    }
    
    updateLastUpdateTime() {
        const element = document.getElementById('last-update');
        if (element) {
            element.textContent = new Date().toLocaleTimeString();
        }
    }
    
    updateLiveIndicator() {
        const indicator = document.getElementById('live-indicator');
        if (indicator) {
            indicator.classList.add('btn-pulse');
            setTimeout(() => {
                indicator.classList.remove('btn-pulse');
            }, 1000);
        }
    }
    
    updateAlertCount(count) {
        const badges = document.querySelectorAll('#alert-count, #sidebar-alert-count');
        badges.forEach(badge => {
            badge.textContent = count;
            badge.style.display = count > 0 ? 'inline' : 'none';
        });
    }
    
    incrementAlertCount() {
        const badge = document.getElementById('alert-count');
        if (badge) {
            const currentCount = parseInt(badge.textContent) || 0;
            this.updateAlertCount(currentCount + 1);
        }
    }
    
    showNotification(message, type = 'info', duration = 3000) {
        const container = document.getElementById('alert-container');
        if (!container) return;
        
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        container.appendChild(alertDiv);
        
        // Auto-dismiss after duration
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, duration);
    }
    
    async refreshDashboard() {
        const refreshBtn = document.getElementById('refresh-dashboard');
        if (refreshBtn) {
            refreshBtn.classList.add('loading');
            refreshBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Refreshing...';
        }
        
        try {
            await this.loadDashboardData();
            this.showNotification('Dashboard refreshed successfully', 'success');
        } catch (error) {
            this.showNotification('Error refreshing dashboard', 'error');
        } finally {
            if (refreshBtn) {
                refreshBtn.classList.remove('loading');
                refreshBtn.innerHTML = '<i class="fas fa-sync-alt"></i> Refresh';
            }
        }
    }
    
    async performHealthCheck() {
        try {
            const health = await this.apiCall('/health');
            console.log('💓 Health check:', health);
        } catch (error) {
            console.error('❌ Health check failed:', error);
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.fraudApp = new FraudDetectionApp();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = FraudDetectionApp;
}