/**
 * Alert Panel Component
 * Manages fraud alerts display, filtering, and actions
 */

class AlertPanel {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        this.options = {
            maxAlerts: options.maxAlerts || 100,
            autoRefresh: options.autoRefresh || true,
            refreshInterval: options.refreshInterval || 5000,
            soundEnabled: options.soundEnabled || true,
            ...options
        };
        
        this.alerts = [];
        this.filteredAlerts = [];
        this.filters = {
            severity: 'all',
            status: 'all',
            timeRange: '24h',
            searchTerm: ''
        };
        
        this.init();
    }

    init() {
        this.createAlertPanel();
        this.bindEvents();
        
        if (this.options.autoRefresh) {
            this.startAutoRefresh();
        }
        
        // Load initial alerts
        this.loadAlerts();
    }

    createAlertPanel() {
        this.container.innerHTML = `
            <div class="alert-panel">
                <!-- Alert Panel Header -->
                <div class="alert-panel-header">
                    <div class="alert-panel-title">
                        <h3>Fraud Alerts</h3>
                        <span class="alert-count badge badge-danger" id="alertCount">0</span>
                    </div>
                    <div class="alert-panel-actions">
                        <button class="btn btn-sm btn-outline-primary" id="refreshAlerts">
                            <i class="fas fa-sync-alt"></i> Refresh
                        </button>
                        <button class="btn btn-sm btn-outline-secondary" id="markAllRead">
                            <i class="fas fa-check-double"></i> Mark All Read
                        </button>
                        <button class="btn btn-sm btn-outline-danger" id="clearAlerts">
                            <i class="fas fa-trash"></i> Clear All
                        </button>
                    </div>
                </div>

                <!-- Alert Filters -->
                <div class="alert-filters">
                    <div class="row">
                        <div class="col-md-3">
                            <select class="form-select form-select-sm" id="severityFilter">
                                <option value="all">All Severities</option>
                                <option value="critical">Critical</option>
                                <option value="high">High</option>
                                <option value="medium">Medium</option>
                                <option value="low">Low</option>
                            </select>
                        </div>
                        <div class="col-md-3">
                            <select class="form-select form-select-sm" id="statusFilter">
                                <option value="all">All Status</option>
                                <option value="new">New</option>
                                <option value="investigating">Investigating</option>
                                <option value="resolved">Resolved</option>
                                <option value="false_positive">False Positive</option>
                            </select>
                        </div>
                        <div class="col-md-3">
                            <select class="form-select form-select-sm" id="timeRangeFilter">
                                <option value="1h">Last Hour</option>
                                <option value="6h">Last 6 Hours</option>
                                <option value="24h" selected>Last 24 Hours</option>
                                <option value="7d">Last 7 Days</option>
                                <option value="30d">Last 30 Days</option>
                            </select>
                        </div>
                        <div class="col-md-3">
                            <input type="text" class="form-control form-control-sm" 
                                   id="searchAlerts" placeholder="Search alerts...">
                        </div>
                    </div>
                </div>

                <!-- Alert Statistics -->
                <div class="alert-stats">
                    <div class="row">
                        <div class="col-md-3">
                            <div class="stat-card critical">
                                <div class="stat-value" id="criticalCount">0</div>
                                <div class="stat-label">Critical</div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="stat-card high">
                                <div class="stat-value" id="highCount">0</div>
                                <div class="stat-label">High</div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="stat-card medium">
                                <div class="stat-value" id="mediumCount">0</div>
                                <div class="stat-label">Medium</div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="stat-card low">
                                <div class="stat-value" id="lowCount">0</div>
                                <div class="stat-label">Low</div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Alert List -->
                <div class="alert-list" id="alertList">
                    <div class="no-alerts text-center py-4">
                        <i class="fas fa-shield-alt fa-3x text-muted mb-3"></i>
                        <p class="text-muted">No alerts to display</p>
                    </div>
                </div>

                <!-- Alert Pagination -->
                <div class="alert-pagination" id="alertPagination"></div>
            </div>

            <!-- Alert Detail Modal -->
            <div class="modal fade" id="alertDetailModal" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Alert Details</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body" id="alertDetailContent">
                            <!-- Alert details will be loaded here -->
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-danger" id="markFraud">Mark as Fraud</button>
                            <button type="button" class="btn btn-warning" id="markFalsePositive">False Positive</button>
                            <button type="button" class="btn btn-success" id="markResolved">Mark Resolved</button>
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    bindEvents() {
        // Refresh alerts
        document.getElementById('refreshAlerts').addEventListener('click', () => {
            this.loadAlerts();
        });

        // Mark all as read
        document.getElementById('markAllRead').addEventListener('click', () => {
            this.markAllAsRead();
        });

        // Clear all alerts
        document.getElementById('clearAlerts').addEventListener('click', () => {
            this.clearAllAlerts();
        });

        // Filter events
        document.getElementById('severityFilter').addEventListener('change', (e) => {
            this.filters.severity = e.target.value;
            this.applyFilters();
        });

        document.getElementById('statusFilter').addEventListener('change', (e) => {
            this.filters.status = e.target.value;
            this.applyFilters();
        });

        document.getElementById('timeRangeFilter').addEventListener('change', (e) => {
            this.filters.timeRange = e.target.value;
            this.applyFilters();
        });

        document.getElementById('searchAlerts').addEventListener('input', (e) => {
            this.filters.searchTerm = e.target.value.toLowerCase();
            this.applyFilters();
        });

        // Alert action events
        document.getElementById('markFraud').addEventListener('click', () => {
            this.updateAlertStatus('confirmed_fraud');
        });

        document.getElementById('markFalsePositive').addEventListener('click', () => {
            this.updateAlertStatus('false_positive');
        });

        document.getElementById('markResolved').addEventListener('click', () => {
            this.updateAlertStatus('resolved');
        });
    }

    async loadAlerts() {
        try {
            const response = await fetch('/api/monitoring/alerts', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            if (response.ok) {
                this.alerts = await response.json();
                this.applyFilters();
                this.updateStatistics();
            } else {
                console.error('Failed to load alerts');
                this.showError('Failed to load alerts');
            }
        } catch (error) {
            console.error('Error loading alerts:', error);
            this.showError('Error loading alerts');
        }
    }

    applyFilters() {
        this.filteredAlerts = this.alerts.filter(alert => {
            // Severity filter
            if (this.filters.severity !== 'all' && alert.severity !== this.filters.severity) {
                return false;
            }

            // Status filter
            if (this.filters.status !== 'all' && alert.status !== this.filters.status) {
                return false;
            }

            // Time range filter
            const alertTime = new Date(alert.timestamp);
            const now = new Date();
            const timeDiff = now - alertTime;
            
            const timeRanges = {
                '1h': 60 * 60 * 1000,
                '6h': 6 * 60 * 60 * 1000,
                '24h': 24 * 60 * 60 * 1000,
                '7d': 7 * 24 * 60 * 60 * 1000,
                '30d': 30 * 24 * 60 * 60 * 1000
            };

            if (timeDiff > timeRanges[this.filters.timeRange]) {
                return false;
            }

            // Search filter
            if (this.filters.searchTerm) {
                const searchFields = [
                    alert.transaction_id,
                    alert.description,
                    alert.user_id,
                    alert.rule_name
                ].join(' ').toLowerCase();

                if (!searchFields.includes(this.filters.searchTerm)) {
                    return false;
                }
            }

            return true;
        });

        this.renderAlerts();
        this.updateCount();
    }

    renderAlerts() {
        const alertList = document.getElementById('alertList');
        
        if (this.filteredAlerts.length === 0) {
            alertList.innerHTML = `
                <div class="no-alerts text-center py-4">
                    <i class="fas fa-shield-alt fa-3x text-muted mb-3"></i>
                    <p class="text-muted">No alerts match your filters</p>
                </div>
            `;
            return;
        }

        const alertsHtml = this.filteredAlerts.map(alert => `
            <div class="alert-item ${alert.severity} ${alert.read ? 'read' : 'unread'}" 
                 data-alert-id="${alert.id}">
                <div class="alert-item-header">
                    <div class="alert-severity">
                        <span class="severity-badge ${alert.severity}">${alert.severity}</span>
                    </div>
                    <div class="alert-timestamp">
                        ${this.formatTimestamp(alert.timestamp)}
                    </div>
                </div>
                
                <div class="alert-item-body">
                    <div class="alert-title">${alert.title}</div>
                    <div class="alert-description">${alert.description}</div>
                    
                    <div class="alert-details">
                        <div class="alert-detail">
                            <strong>Transaction:</strong> ${alert.transaction_id}
                        </div>
                        <div class="alert-detail">
                            <strong>Amount:</strong> $${alert.amount?.toLocaleString()}
                        </div>
                        <div class="alert-detail">
                            <strong>Risk Score:</strong> ${(alert.risk_score * 100).toFixed(1)}%
                        </div>
                        <div class="alert-detail">
                            <strong>Rule:</strong> ${alert.rule_name}
                        </div>
                    </div>
                </div>
                
                <div class="alert-item-footer">
                    <div class="alert-status">
                        <span class="status-badge ${alert.status}">${alert.status.replace('_', ' ')}</span>
                    </div>
                    <div class="alert-actions">
                        <button class="btn btn-sm btn-outline-primary view-details" 
                                data-alert-id="${alert.id}">
                            <i class="fas fa-eye"></i> View
                        </button>
                        <button class="btn btn-sm btn-outline-success mark-resolved" 
                                data-alert-id="${alert.id}">
                            <i class="fas fa-check"></i> Resolve
                        </button>
                        <button class="btn btn-sm btn-outline-danger dismiss-alert" 
                                data-alert-id="${alert.id}">
                            <i class="fas fa-times"></i> Dismiss
                        </button>
                    </div>
                </div>
            </div>
        `).join('');

        alertList.innerHTML = alertsHtml;

        // Bind click events for alert actions
        this.bindAlertActions();
    }

    bindAlertActions() {
        // View details
        document.querySelectorAll('.view-details').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const alertId = e.currentTarget.dataset.alertId;
                this.showAlertDetails(alertId);
            });
        });

        // Mark resolved
        document.querySelectorAll('.mark-resolved').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const alertId = e.currentTarget.dataset.alertId;
                this.updateAlertStatus('resolved', alertId);
            });
        });

        // Dismiss alert
        document.querySelectorAll('.dismiss-alert').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const alertId = e.currentTarget.dataset.alertId;
                this.dismissAlert(alertId);
            });
        });

        // Alert item click to mark as read
        document.querySelectorAll('.alert-item.unread').forEach(item => {
            item.addEventListener('click', (e) => {
                if (!e.target.closest('.alert-actions')) {
                    const alertId = item.dataset.alertId;
                    this.markAsRead(alertId);
                }
            });
        });
    }

    showAlertDetails(alertId) {
        const alert = this.alerts.find(a => a.id === alertId);
        if (!alert) return;

        const detailContent = document.getElementById('alertDetailContent');
        detailContent.innerHTML = `
            <div class="alert-detail-content">
                <div class="row">
                    <div class="col-md-6">
                        <h6>Alert Information</h6>
                        <table class="table table-sm">
                            <tr><td><strong>ID:</strong></td><td>${alert.id}</td></tr>
                            <tr><td><strong>Severity:</strong></td><td><span class="severity-badge ${alert.severity}">${alert.severity}</span></td></tr>
                            <tr><td><strong>Status:</strong></td><td><span class="status-badge ${alert.status}">${alert.status}</span></td></tr>
                            <tr><td><strong>Created:</strong></td><td>${this.formatTimestamp(alert.timestamp)}</td></tr>
                            <tr><td><strong>Rule:</strong></td><td>${alert.rule_name}</td></tr>
                        </table>
                    </div>
                    <div class="col-md-6">
                        <h6>Transaction Details</h6>
                        <table class="table table-sm">
                            <tr><td><strong>Transaction ID:</strong></td><td>${alert.transaction_id}</td></tr>
                            <tr><td><strong>User ID:</strong></td><td>${alert.user_id}</td></tr>
                            <tr><td><strong>Amount:</strong></td><td>$${alert.amount?.toLocaleString()}</td></tr>
                            <tr><td><strong>Risk Score:</strong></td><td>${(alert.risk_score * 100).toFixed(1)}%</td></tr>
                            <tr><td><strong>Location:</strong></td><td>${alert.location || 'N/A'}</td></tr>
                        </table>
                    </div>
                </div>
                
                <div class="row mt-3">
                    <div class="col-12">
                        <h6>Description</h6>
                        <p>${alert.description}</p>
                        
                        ${alert.additional_info ? `
                            <h6>Additional Information</h6>
                            <pre class="bg-light p-2 rounded">${JSON.stringify(alert.additional_info, null, 2)}</pre>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;

        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('alertDetailModal'));
        modal.show();

        // Store current alert ID for actions
        this.currentAlertId = alertId;
    }

    async updateAlertStatus(status, alertId = null) {
        const targetAlertId = alertId || this.currentAlertId;
        if (!targetAlertId) return;

        try {
            const response = await fetch(`/api/monitoring/alerts/${targetAlertId}/status`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ status })
            });

            if (response.ok) {
                // Update local alert
                const alert = this.alerts.find(a => a.id === targetAlertId);
                if (alert) {
                    alert.status = status;
                    alert.updated_at = new Date().toISOString();
                }

                this.applyFilters();
                this.updateStatistics();
                
                // Close modal if open
                const modal = bootstrap.Modal.getInstance(document.getElementById('alertDetailModal'));
                if (modal) {
                    modal.hide();
                }

                this.showSuccess(`Alert marked as ${status.replace('_', ' ')}`);
            } else {
                this.showError('Failed to update alert status');
            }
        } catch (error) {
            console.error('Error updating alert status:', error);
            this.showError('Error updating alert status');
        }
    }

    async markAsRead(alertId) {
        const alert = this.alerts.find(a => a.id === alertId);
        if (!alert || alert.read) return;

        try {
            const response = await fetch(`/api/monitoring/alerts/${alertId}/read`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            if (response.ok) {
                alert.read = true;
                this.applyFilters();
                this.updateCount();
            }
        } catch (error) {
            console.error('Error marking alert as read:', error);
        }
    }

    async markAllAsRead() {
        try {
            const response = await fetch('/api/monitoring/alerts/mark-all-read', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            if (response.ok) {
                this.alerts.forEach(alert => alert.read = true);
                this.applyFilters();
                this.updateCount();
                this.showSuccess('All alerts marked as read');
            } else {
                this.showError('Failed to mark all alerts as read');
            }
        } catch (error) {
            console.error('Error marking all alerts as read:', error);
            this.showError('Error marking all alerts as read');
        }
    }

    async clearAllAlerts() {
        if (!confirm('Are you sure you want to clear all alerts? This action cannot be undone.')) {
            return;
        }

        try {
            const response = await fetch('/api/monitoring/alerts', {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            if (response.ok) {
                this.alerts = [];
                this.applyFilters();
                this.updateStatistics();
                this.showSuccess('All alerts cleared');
            } else {
                this.showError('Failed to clear alerts');
            }
        } catch (error) {
            console.error('Error clearing alerts:', error);
            this.showError('Error clearing alerts');
        }
    }

    async dismissAlert(alertId) {
        try {
            const response = await fetch(`/api/monitoring/alerts/${alertId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            if (response.ok) {
                this.alerts = this.alerts.filter(a => a.id !== alertId);
                this.applyFilters();
                this.updateStatistics();
                this.showSuccess('Alert dismissed');
            } else {
                this.showError('Failed to dismiss alert');
            }
        } catch (error) {
            console.error('Error dismissing alert:', error);
            this.showError('Error dismissing alert');
        }
    }

    updateCount() {
        const unreadCount = this.filteredAlerts.filter(alert => !alert.read).length;
        document.getElementById('alertCount').textContent = unreadCount;
    }

    updateStatistics() {
        const stats = {
            critical: 0,
            high: 0,
            medium: 0,
            low: 0
        };

        this.alerts.forEach(alert => {
            if (stats.hasOwnProperty(alert.severity)) {
                stats[alert.severity]++;
            }
        });

        document.getElementById('criticalCount').textContent = stats.critical;
        document.getElementById('highCount').textContent = stats.high;
        document.getElementById('mediumCount').textContent = stats.medium;
        document.getElementById('lowCount').textContent = stats.low;
    }

    formatTimestamp(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = now - date;

        if (diff < 60000) {
            return 'Just now';
        } else if (diff < 3600000) {
            return `${Math.floor(diff / 60000)}m ago`;
        } else if (diff < 86400000) {
            return `${Math.floor(diff / 3600000)}h ago`;
        } else {
            return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
        }
    }

    startAutoRefresh() {
        setInterval(() => {
            this.loadAlerts();
        }, this.options.refreshInterval);
    }

    showSuccess(message) {
        this.showToast(message, 'success');
    }

    showError(message) {
        this.showToast(message, 'error');
    }

    showToast(message, type) {
        // Create toast notification
        const toast = document.createElement('div');
        toast.className = `toast alert-toast ${type}`;
        toast.innerHTML = `
            <div class="toast-content">
                <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
                <span>${message}</span>
            </div>
        `;

        document.body.appendChild(toast);

        // Show toast
        setTimeout(() => toast.classList.add('show'), 100);

        // Hide and remove toast
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    // Public method to add new alert (for real-time updates)
    addAlert(alert) {
        this.alerts.unshift(alert);
        
        // Limit alerts array size
        if (this.alerts.length > this.options.maxAlerts) {
            this.alerts = this.alerts.slice(0, this.options.maxAlerts);
        }

        this.applyFilters();
        this.updateStatistics();

        // Play sound for high priority alerts
        if (this.options.soundEnabled && (alert.severity === 'critical' || alert.severity === 'high')) {
            this.playAlertSound();
        }
    }

    playAlertSound() {
        // Create audio context for alert sound
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();

        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);

        oscillator.frequency.setValueAtTime(800, audioContext.currentTime);
        oscillator.frequency.setValueAtTime(600, audioContext.currentTime + 0.1);
        
        gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.2);

        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.2);
    }

    // Public method to destroy the component
    destroy() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
        this.container.innerHTML = '';
    }
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AlertPanel;
}