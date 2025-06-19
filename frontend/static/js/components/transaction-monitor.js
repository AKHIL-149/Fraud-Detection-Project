// ===== TRANSACTION MONITOR COMPONENT =====

class TransactionMonitor {
    constructor(containerId = 'transaction-stream') {
        this.containerId = containerId;
        this.container = document.getElementById(containerId);
        this.transactions = [];
        this.maxTransactions = 50;
        this.isActive = true;
        this.filters = {
            type: 'all', // all, fraud, legitimate, high-risk
            category: 'all',
            amount: { min: 0, max: Infinity }
        };
        this.sortBy = 'timestamp';
        this.sortOrder = 'desc';
        
        this.init();
    }
    
    init() {
        if (!this.container) {
            console.error(`Transaction monitor container '${this.containerId}' not found`);
            return;
        }
        
        this.setupEventListeners();
        this.renderEmptyState();
        
        console.log('📊 Transaction Monitor initialized');
    }
    
    setupEventListeners() {
        // Listen for new transactions from WebSocket
        document.addEventListener('newTransaction', (event) => {
            if (this.isActive) {
                this.addTransaction(event.detail);
            }
        });
        
        // Filter controls
        const filterButtons = document.querySelectorAll('.filter-option');
        filterButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                const filterType = button.dataset.filter;
                this.applyFilter(filterType);
            });
        });
        
        // Clear stream button
        const clearButton = document.getElementById('clear-stream');
        if (clearButton) {
            clearButton.addEventListener('click', () => {
                this.clearStream();
            });
        }
        
        // Pause/Resume button
        const pauseButton = document.getElementById('pause-monitoring');
        if (pauseButton) {
            pauseButton.addEventListener('click', () => {
                this.toggleMonitoring();
            });
        }
    }
    
    addTransaction(transaction) {
        // Add timestamp if not present
        if (!transaction.timestamp) {
            transaction.timestamp = new Date().toISOString();
        }
        
        // Add to transactions array
        this.transactions.unshift(transaction);
        
        // Limit array size
        if (this.transactions.length > this.maxTransactions) {
            this.transactions = this.transactions.slice(0, this.maxTransactions);
        }
        
        // Update display
        this.renderTransactions();
        
        // Update count
        this.updateTransactionCount();
        
        // Play sound for high-risk transactions
        if (transaction.fraud_probability > 0.7) {
            this.playAlertSound();
        }
    }
    
    renderTransactions() {
        if (!this.container) return;
        
        const filteredTransactions = this.getFilteredTransactions();
        
        if (filteredTransactions.length === 0) {
            this.renderEmptyState();
            return;
        }
        
        // Sort transactions
        const sortedTransactions = this.sortTransactions(filteredTransactions);
        
        // Render transaction items
        this.container.innerHTML = sortedTransactions
            .map(transaction => this.createTransactionElement(transaction))
            .join('');
        
        // Add click event listeners
        this.attachClickListeners();
    }
    
    createTransactionElement(transaction) {
        const riskLevel = this.getRiskLevel(transaction.fraud_probability);
        const riskClass = this.getRiskClass(riskLevel);
        const statusClass = transaction.is_fraud ? 'fraud' : 'legitimate';
        const timeAgo = this.getTimeAgo(transaction.timestamp);
        
        return `
            <div class="transaction-item ${statusClass} new-transaction" 
                 data-transaction-id="${transaction.transaction_id}"
                 data-fraud-probability="${transaction.fraud_probability}"
                 data-is-fraud="${transaction.is_fraud}">
                
                <div class="transaction-meta">
                    <div class="transaction-id">${transaction.transaction_id}</div>
                    <div class="transaction-timestamp">${timeAgo}</div>
                </div>
                
                <div class="transaction-details">
                    <div class="transaction-amount">
                        ${this.formatCurrency(transaction.amount)}
                    </div>
                    
                    <div class="transaction-category">
                        ${transaction.merchant_category || 'Unknown'}
                    </div>
                    
                    <span class="badge badge-modern ${riskClass}">
                        ${(transaction.fraud_probability * 100).toFixed(1)}% Risk
                    </span>
                    
                    <span class="badge badge-modern ${transaction.is_fraud ? 'badge-status-fraud' : 'badge-status-legitimate'}">
                        ${transaction.is_fraud ? 'Fraud' : 'Legitimate'}
                    </span>
                </div>
                
                <div class="transaction-actions mt-2" style="display: none;">
                    <button class="btn btn-sm btn-outline-primary me-1" onclick="transactionMonitor.viewDetails('${transaction.transaction_id}')">
                        <i class="fas fa-eye"></i> Details
                    </button>
                    <button class="btn btn-sm btn-outline-secondary me-1" onclick="transactionMonitor.flagTransaction('${transaction.transaction_id}')">
                        <i class="fas fa-flag"></i> Flag
                    </button>
                    <button class="btn btn-sm btn-outline-info" onclick="transactionMonitor.blockTransaction('${transaction.transaction_id}')">
                        <i class="fas fa-ban"></i> Block
                    </button>
                </div>
            </div>
        `;
    }
    
    attachClickListeners() {
        const transactionItems = this.container.querySelectorAll('.transaction-item');
        
        transactionItems.forEach(item => {
            // Show actions on hover
            item.addEventListener('mouseenter', () => {
                const actions = item.querySelector('.transaction-actions');
                if (actions) actions.style.display = 'block';
            });
            
            item.addEventListener('mouseleave', () => {
                const actions = item.querySelector('.transaction-actions');
                if (actions) actions.style.display = 'none';
            });
            
            // Click to view details
            item.addEventListener('click', (e) => {
                if (!e.target.closest('.transaction-actions')) {
                    const transactionId = item.dataset.transactionId;
                    this.viewDetails(transactionId);
                }
            });
            
            // Remove animation class after animation completes
            setTimeout(() => {
                item.classList.remove('new-transaction');
            }, 2000);
        });
    }
    
    getFilteredTransactions() {
        return this.transactions.filter(transaction => {
            // Type filter
            if (this.filters.type === 'fraud' && !transaction.is_fraud) return false;
            if (this.filters.type === 'legitimate' && transaction.is_fraud) return false;
            if (this.filters.type === 'high-risk' && transaction.fraud_probability <= 0.7) return false;
            
            // Category filter
            if (this.filters.category !== 'all' && transaction.merchant_category !== this.filters.category) return false;
            
            // Amount filter
            if (transaction.amount < this.filters.amount.min || transaction.amount > this.filters.amount.max) return false;
            
            return true;
        });
    }
    
    sortTransactions(transactions) {
        return transactions.sort((a, b) => {
            let aValue = a[this.sortBy];
            let bValue = b[this.sortBy];
            
            // Handle different data types
            if (this.sortBy === 'timestamp') {
                aValue = new Date(aValue);
                bValue = new Date(bValue);
            } else if (typeof aValue === 'string') {
                aValue = aValue.toLowerCase();
                bValue = bValue.toLowerCase();
            }
            
            if (this.sortOrder === 'asc') {
                return aValue < bValue ? -1 : aValue > bValue ? 1 : 0;
            } else {
                return aValue > bValue ? -1 : aValue < bValue ? 1 : 0;
            }
        });
    }
    
    applyFilter(filterType) {
        this.filters.type = filterType;
        this.renderTransactions();
        
        // Update active filter button
        document.querySelectorAll('.filter-option').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-filter="${filterType}"]`)?.classList.add('active');
        
        console.log(`📊 Applied filter: ${filterType}`);
    }
    
    clearStream() {
        this.transactions = [];
        this.renderEmptyState();
        this.updateTransactionCount();
        
        console.log('📊 Transaction stream cleared');
    }
    
    toggleMonitoring() {
        this.isActive = !this.isActive;
        
        const button = document.getElementById('pause-monitoring');
        if (button) {
            if (this.isActive) {
                button.innerHTML = '<i class="fas fa-pause"></i> Pause';
                button.classList.remove('btn-warning');
                button.classList.add('btn-outline-secondary');
            } else {
                button.innerHTML = '<i class="fas fa-play"></i> Resume';
                button.classList.remove('btn-outline-secondary');
                button.classList.add('btn-warning');
            }
        }
        
        console.log(`📊 Monitoring ${this.isActive ? 'resumed' : 'paused'}`);
    }
    
    renderEmptyState() {
        if (!this.container) return;
        
        const message = this.isActive ? 
            'Waiting for transactions...' : 
            'Monitoring paused';
            
        const icon = this.isActive ? 
            'fa-spinner fa-spin' : 
            'fa-pause';
        
        this.container.innerHTML = `
            <div class="text-center p-4 text-muted">
                <i class="fas ${icon} fa-2x mb-3"></i>
                <div>${message}</div>
            </div>
        `;
    }
    
    updateTransactionCount() {
        const countElement = document.getElementById('stream-count');
        if (countElement) {
            countElement.textContent = this.transactions.length;
        }
        
        // Update transactions per minute
        const tpmElement = document.getElementById('transactions-per-minute');
        if (tpmElement) {
            const recentTransactions = this.getRecentTransactions(60000); // Last minute
            tpmElement.textContent = recentTransactions.length;
        }
    }
    
    getRecentTransactions(timeWindow) {
        const now = Date.now();
        return this.transactions.filter(transaction => {
            const transactionTime = new Date(transaction.timestamp).getTime();
            return (now - transactionTime) <= timeWindow;
        });
    }
    
    // Action methods
    viewDetails(transactionId) {
        const transaction = this.transactions.find(t => t.transaction_id === transactionId);
        if (!transaction) return;
        
        // Create or show transaction details modal
        this.showTransactionModal(transaction);
        
        console.log(`👁️ Viewing details for transaction: ${transactionId}`);
    }
    
    flagTransaction(transactionId) {
        // Flag transaction for manual review
        fetch(`/api/transactions/${transactionId}/flag`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        })
        .then(response => response.json())
        .then(data => {
            this.showNotification('Transaction flagged for review', 'success');
        })
        .catch(error => {
            this.showNotification('Failed to flag transaction', 'error');
            console.error('Flag transaction error:', error);
        });
        
        console.log(`🚩 Flagged transaction: ${transactionId}`);
    }
    
    blockTransaction(transactionId) {
        if (!confirm('Are you sure you want to block this transaction?')) return;
        
        // Block transaction
        fetch(`/api/transactions/${transactionId}/block`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        })
        .then(response => response.json())
        .then(data => {
            this.showNotification('Transaction blocked successfully', 'success');
            // Update transaction status in the list
            this.updateTransactionStatus(transactionId, 'blocked');
        })
        .catch(error => {
            this.showNotification('Failed to block transaction', 'error');
            console.error('Block transaction error:', error);
        });
        
        console.log(`🚫 Blocked transaction: ${transactionId}`);
    }
    
    showTransactionModal(transaction) {
        const modalId = 'transactionDetailModal';
        let modal = document.getElementById(modalId);
        
        if (!modal) {
            modal = this.createTransactionModal(modalId);
            document.body.appendChild(modal);
        }
        
        this.populateTransactionModal(modal, transaction);
        
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
    }
    
    createTransactionModal(modalId) {
        const modal = document.createElement('div');
        modal.id = modalId;
        modal.className = 'modal fade';
        modal.tabIndex = -1;
        
        modal.innerHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header bg-primary text-white">
                        <h5 class="modal-title">Transaction Details</h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body" id="${modalId}-body"></div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                        <button type="button" class="btn btn-primary" id="export-transaction">Export</button>
                    </div>
                </div>
            </div>
        `;
        
        return modal;
    }
    
    populateTransactionModal(modal, transaction) {
        const body = modal.querySelector('.modal-body');
        const riskLevel = this.getRiskLevel(transaction.fraud_probability);
        const riskClass = this.getRiskClass(riskLevel);
        
        body.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <h6 class="text-primary mb-3">Transaction Information</h6>
                    <table class="table table-sm">
                        <tr>
                            <td><strong>Transaction ID:</strong></td>
                            <td class="font-monospace">${transaction.transaction_id}</td>
                        </tr>
                        <tr>
                            <td><strong>Amount:</strong></td>
                            <td class="fw-bold">${this.formatCurrency(transaction.amount)}</td>
                        </tr>
                        <tr>
                            <td><strong>Merchant Category:</strong></td>
                            <td>${transaction.merchant_category || 'Unknown'}</td>
                        </tr>
                        <tr>
                            <td><strong>Transaction Type:</strong></td>
                            <td>${transaction.transaction_type || 'Unknown'}</td>
                        </tr>
                        <tr>
                            <td><strong>Location:</strong></td>
                            <td>${transaction.location || 'Unknown'}</td>
                        </tr>
                        <tr>
                            <td><strong>Timestamp:</strong></td>
                            <td>${new Date(transaction.timestamp).toLocaleString()}</td>
                        </tr>
                    </table>
                </div>
                
                <div class="col-md-6">
                    <h6 class="text-primary mb-3">Risk Assessment</h6>
                    <div class="text-center mb-3">
                        <div class="h2 mb-0">
                            <span class="badge ${riskClass} fs-4 p-3">
                                ${(transaction.fraud_probability * 100).toFixed(1)}%
                            </span>
                        </div>
                        <small class="text-muted">Fraud Probability</small>
                    </div>
                    
                    <div class="progress progress-modern mb-3">
                        <div class="progress-bar ${riskLevel === 'high' ? 'bg-danger' : riskLevel === 'medium' ? 'bg-warning' : 'bg-success'}" 
                             style="width: ${transaction.fraud_probability * 100}%"></div>
                    </div>
                    
                    <div class="text-center">
                        <span class="badge ${transaction.is_fraud ? 'badge-status-fraud' : 'badge-status-legitimate'} fs-6 p-2">
                            ${transaction.is_fraud ? 'Fraudulent' : 'Legitimate'}
                        </span>
                    </div>
                    
                    <hr>
                    
                    <h6 class="text-primary mb-2">Risk Factors</h6>
                    <div class="small">
                        ${this.generateRiskFactors(transaction)}
                    </div>
                </div>
            </div>
        `;
    }
    
    generateRiskFactors(transaction) {
        const factors = [];
        
        if (transaction.amount > 1000) {
            factors.push('<span class="badge bg-warning me-1">High Amount</span>');
        }
        
        if (transaction.hour_of_day < 6 || transaction.hour_of_day > 22) {
            factors.push('<span class="badge bg-warning me-1">Unusual Hour</span>');
        }
        
        if (transaction.is_weekend) {
            factors.push('<span class="badge bg-info me-1">Weekend</span>');
        }
        
        if (transaction.merchant_risk_score > 0.5) {
            factors.push('<span class="badge bg-danger me-1">High-Risk Merchant</span>');
        }
        
        if (factors.length === 0) {
            factors.push('<span class="text-muted">No significant risk factors detected</span>');
        }
        
        return factors.join(' ');
    }
    
    // Utility methods
    getRiskLevel(fraudProbability) {
        if (fraudProbability > 0.7) return 'high';
        if (fraudProbability > 0.3) return 'medium';
        return 'low';
    }
    
    getRiskClass(riskLevel) {
        switch (riskLevel) {
            case 'high': return 'badge-risk-high';
            case 'medium': return 'badge-risk-medium';
            case 'low': return 'badge-risk-low';
            default: return 'badge-risk-low';
        }
    }
    
    formatCurrency(amount) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(amount);
    }
    
    getTimeAgo(timestamp) {
        const now = Date.now();
        const transactionTime = new Date(timestamp).getTime();
        const diffMs = now - transactionTime;
        
        const diffSecs = Math.floor(diffMs / 1000);
        const diffMins = Math.floor(diffSecs / 60);
        const diffHours = Math.floor(diffMins / 60);
        
        if (diffSecs < 60) return 'Just now';
        if (diffMins < 60) return `${diffMins}m ago`;
        if (diffHours < 24) return `${diffHours}h ago`;
        
        return new Date(timestamp).toLocaleDateString();
    }
    
    playAlertSound() {
        try {
            // Create a simple beep sound
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);
            
            oscillator.frequency.setValueAtTime(800, audioContext.currentTime);
            oscillator.type = 'sine';
            
            gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.3);
            
            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + 0.3);
        } catch (error) {
            console.warn('Could not play alert sound:', error);
        }
    }
    
    updateTransactionStatus(transactionId, status) {
        const transaction = this.transactions.find(t => t.transaction_id === transactionId);
        if (transaction) {
            transaction.status = status;
            this.renderTransactions();
        }
    }
    
    showNotification(message, type = 'info') {
        // Use global notification system if available
        if (window.fraudApp && window.fraudApp.showNotification) {
            window.fraudApp.showNotification(message, type);
        } else {
            console.log(`${type.toUpperCase()}: ${message}`);
        }
    }
    
    // Export functionality
    exportTransactions(format = 'csv') {
        const data = this.getFilteredTransactions();
        
        if (format === 'csv') {
            this.exportToCSV(data);
        } else if (format === 'json') {
            this.exportToJSON(data);
        }
    }
    
    exportToCSV(transactions) {
        const headers = [
            'Transaction ID', 'Amount', 'Merchant Category', 'Fraud Probability', 
            'Is Fraud', 'Timestamp', 'Location'
        ];
        
        const csvContent = [
            headers.join(','),
            ...transactions.map(t => [
                t.transaction_id,
                t.amount,
                t.merchant_category || '',
                t.fraud_probability,
                t.is_fraud,
                t.timestamp,
                t.location || ''
            ].join(','))
        ].join('\n');
        
        this.downloadFile(csvContent, 'transactions.csv', 'text/csv');
    }
    
    exportToJSON(transactions) {
        const jsonContent = JSON.stringify(transactions, null, 2);
        this.downloadFile(jsonContent, 'transactions.json', 'application/json');
    }
    
    downloadFile(content, filename, mimeType) {
        const blob = new Blob([content], { type: mimeType });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    }
    
    // Public API methods
    getTransactionCount() {
        return this.transactions.length;
    }
    
    getFraudCount() {
        return this.transactions.filter(t => t.is_fraud).length;
    }
    
    getAverageRiskScore() {
        if (this.transactions.length === 0) return 0;
        const total = this.transactions.reduce((sum, t) => sum + t.fraud_probability, 0);
        return total / this.transactions.length;
    }
    
    getTransactionsByTimeRange(startTime, endTime) {
        return this.transactions.filter(t => {
            const transactionTime = new Date(t.timestamp).getTime();
            return transactionTime >= startTime && transactionTime <= endTime;
        });
    }
    
    // Cleanup method
    destroy() {
        // Remove event listeners and clean up
        document.removeEventListener('newTransaction', this.handleNewTransaction);
        
        if (this.container) {
            this.container.innerHTML = '';
        }
        
        console.log('📊 Transaction Monitor destroyed');
    }
}

// Global instance for easy access
window.TransactionMonitor = TransactionMonitor;

// Initialize if container exists
document.addEventListener('DOMContentLoaded', function() {
    const container = document.getElementById('transaction-stream');
    if (container) {
        window.transactionMonitor = new TransactionMonitor();
    }
});