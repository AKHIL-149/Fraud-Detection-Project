// ===== WEBSOCKET HANDLER FOR REAL-TIME COMMUNICATION =====

class WebSocketManager {
    constructor(url = null) {
        this.url = url || this.getWebSocketURL();
        this.socket = null;
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 10;
        this.reconnectDelay = 1000; // Start with 1 second
        this.maxReconnectDelay = 30000; // Max 30 seconds
        this.heartbeatInterval = null;
        this.heartbeatDelay = 30000; // 30 seconds
        
        // Event listeners
        this.eventListeners = {
            'open': [],
            'close': [],
            'error': [],
            'message': [],
            'transaction': [],
            'alert': [],
            'status': []
        };
        
        this.init();
    }
    
    getWebSocketURL() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = window.location.host;
        return `${protocol}//${host}/ws/monitor`;
    }
    
    init() {
        console.log('🔌 Initializing WebSocket connection...');
        this.connect();
    }
    
    connect() {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            console.log('⚠️ WebSocket already connected');
            return;
        }
        
        try {
            console.log(`🔗 Connecting to: ${this.url}`);
            this.socket = new WebSocket(this.url);
            this.setupEventHandlers();
        } catch (error) {
            console.error('❌ Failed to create WebSocket connection:', error);
            this.handleConnectionError();
        }
    }
    
    setupEventHandlers() {
        this.socket.onopen = (event) => {
            console.log('✅ WebSocket connected successfully');
            this.isConnected = true;
            this.reconnectAttempts = 0;
            this.reconnectDelay = 1000; // Reset delay
            
            this.startHeartbeat();
            this.emit('open', event);
        };
        
        this.socket.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                console.log('📨 Received message:', data.type);
                
                // Emit general message event
                this.emit('message', data);
                
                // Emit specific event type
                if (data.type && this.eventListeners[data.type]) {
                    this.emit(data.type, data.data || data);
                }
                
                // Handle built-in message types
                this.handleMessage(data);
                
            } catch (error) {
                console.error('❌ Error parsing WebSocket message:', error);
            }
        };
        
        this.socket.onclose = (event) => {
            console.log('🔌 WebSocket connection closed:', event.code, event.reason);
            this.isConnected = false;
            this.stopHeartbeat();
            
            this.emit('close', event);
            
            // Attempt to reconnect unless it was a clean close
            if (event.code !== 1000) {
                this.scheduleReconnect();
            }
        };
        
        this.socket.onerror = (error) => {
            console.error('❌ WebSocket error:', error);
            this.emit('error', error);
            this.handleConnectionError();
        };
    }
    
    handleMessage(data) {
        switch (data.type) {
            case 'transaction':
                this.handleTransaction(data.data);
                break;
            case 'alert':
                this.handleAlert(data.data);
                break;
            case 'status':
                this.handleStatus(data.data);
                break;
            case 'heartbeat':
                this.handleHeartbeat(data.data);
                break;
            default:
                console.log('🔄 Unknown message type:', data.type);
        }
    }
    
    handleTransaction(transaction) {
        console.log('💳 New transaction:', transaction.transaction_id);
        
        // Update UI elements
        this.updateTransactionCount();
        this.addTransactionToStream(transaction);
        
        // Show notification for high-risk transactions
        if (transaction.fraud_probability > 0.7) {
            this.showTransactionAlert(transaction);
        }
    }
    
    handleAlert(alert) {
        console.log('🚨 New fraud alert:', alert.transaction_id);
        
        // Update alert count
        this.updateAlertCount();
        
        // Add to alert list
        this.addAlertToList(alert);
        
        // Show notification
        this.showAlertNotification(alert);
        
        // Play alert sound (if enabled)
        this.playAlertSound(alert.severity);
    }
    
    handleStatus(status) {
        console.log('📊 Status update:', status);
        
        // Update system health indicators
        this.updateSystemHealth(status);
    }
    
    handleHeartbeat(data) {
        console.log('💓 Heartbeat received');
        // Send heartbeat response
        this.send({ type: 'heartbeat_response', timestamp: Date.now() });
    }
    
    send(data) {
        if (this.isConnected && this.socket.readyState === WebSocket.OPEN) {
            try {
                this.socket.send(JSON.stringify(data));
                console.log('📤 Sent message:', data.type || 'unknown');
            } catch (error) {
                console.error('❌ Failed to send message:', error);
            }
        } else {
            console.warn('⚠️ Cannot send message: WebSocket not connected');
        }
    }
    
    scheduleReconnect() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.error('❌ Max reconnection attempts reached');
            this.showMaxReconnectError();
            return;
        }
        
        const delay = Math.min(
            this.reconnectDelay * Math.pow(2, this.reconnectAttempts),
            this.maxReconnectDelay
        );
        
        console.log(`🔄 Scheduling reconnect in ${delay}ms (attempt ${this.reconnectAttempts + 1})`);
        
        setTimeout(() => {
            this.reconnectAttempts++;
            this.connect();
        }, delay);
    }
    
    handleConnectionError() {
        this.isConnected = false;
        this.stopHeartbeat();
        
        // Update UI to show disconnected state
        this.updateConnectionStatus('disconnected');
    }
    
    startHeartbeat() {
        this.stopHeartbeat(); // Clear any existing interval
        
        this.heartbeatInterval = setInterval(() => {
            if (this.isConnected) {
                this.send({ type: 'heartbeat', timestamp: Date.now() });
            }
        }, this.heartbeatDelay);
    }
    
    stopHeartbeat() {
        if (this.heartbeatInterval) {
            clearInterval(this.heartbeatInterval);
            this.heartbeatInterval = null;
        }
    }
    
    // ===== Event System =====
    on(event, callback) {
        if (this.eventListeners[event]) {
            this.eventListeners[event].push(callback);
        } else {
            console.warn(`⚠️ Unknown event type: ${event}`);
        }
    }
    
    off(event, callback) {
        if (this.eventListeners[event]) {
            const index = this.eventListeners[event].indexOf(callback);
            if (index > -1) {
                this.eventListeners[event].splice(index, 1);
            }
        }
    }
    
    emit(event, data) {
        if (this.eventListeners[event]) {
            this.eventListeners[event].forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    console.error(`❌ Error in event callback for ${event}:`, error);
                }
            });
        }
    }
    
    // ===== UI Update Methods =====
    updateConnectionStatus(status) {
        // Update connection indicator
        const indicators = document.querySelectorAll('.connection-status');
        indicators.forEach(indicator => {
            indicator.className = `connection-status status-${status}`;
        });
        
        // Update status text
        const statusTexts = document.querySelectorAll('.connection-status-text');
        statusTexts.forEach(text => {
            text.textContent = status.charAt(0).toUpperCase() + status.slice(1);
        });
        
        // Update WebSocket health in sidebar
        const wsHealth = document.getElementById('ws-health');
        if (wsHealth) {
            const statusClass = status === 'connected' ? 'bg-success' : 'bg-danger';
            const statusText = status === 'connected' ? 'Connected' : 'Disconnected';
            
            wsHealth.className = `badge ${statusClass}`;
            wsHealth.textContent = statusText;
        }
    }
    
    updateTransactionCount() {
        const countElement = document.getElementById('today-transactions');
        if (countElement) {
            const currentCount = parseInt(countElement.textContent) || 0;
            countElement.textContent = currentCount + 1;
        }
    }
    
    updateAlertCount() {
        const alertBadges = document.querySelectorAll('#alert-count, #sidebar-alert-count');
        alertBadges.forEach(badge => {
            const currentCount = parseInt(badge.textContent) || 0;
            badge.textContent = currentCount + 1;
            badge.style.display = 'inline';
        });
    }
    
    addTransactionToStream(transaction) {
        const streamContainer = document.getElementById('transaction-stream');
        if (!streamContainer) return;
        
        const transactionElement = this.createTransactionElement(transaction);
        
        // Add to top of stream
        if (streamContainer.firstChild) {
            streamContainer.insertBefore(transactionElement, streamContainer.firstChild);
        } else {
            streamContainer.appendChild(transactionElement);
        }
        
        // Remove old transactions (keep only last 20)
        while (streamContainer.children.length > 20) {
            streamContainer.removeChild(streamContainer.lastChild);
        }
        
        // Animate new transaction
        transactionElement.style.opacity = '0';
        transactionElement.style.transform = 'translateY(-20px)';
        
        setTimeout(() => {
            transactionElement.style.transition = 'all 0.3s ease';
            transactionElement.style.opacity = '1';
            transactionElement.style.transform = 'translateY(0)';
        }, 10);
    }
    
    createTransactionElement(transaction) {
        const div = document.createElement('div');
        div.className = `transaction-item ${transaction.is_fraud ? 'fraud' : 'legitimate'}`;
        
        const riskClass = this.getRiskClass(transaction.fraud_probability);
        const statusClass = transaction.is_fraud ? 'danger' : 'success';
        const statusText = transaction.is_fraud ? 'Fraud' : 'Legitimate';
        
        div.innerHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <div class="fw-bold">${transaction.transaction_id}</div>
                    <small class="text-muted">
                        ${transaction.merchant_category} • ${transaction.amount?.toFixed(2)}
                    </small>
                </div>
                <div class="text-end">
                    <span class="badge ${riskClass} mb-1">
                        ${(transaction.fraud_probability * 100).toFixed(1)}%
                    </span><br>
                    <span class="badge bg-${statusClass}">${statusText}</span>
                </div>
            </div>
            <div class="mt-2">
                <small class="text-muted">
                    ${new Date(transaction.timestamp).toLocaleTimeString()}
                </small>
            </div>
        `;
        
        // Add click handler for details
        div.style.cursor = 'pointer';
        div.addEventListener('click', () => {
            this.showTransactionDetails(transaction);
        });
        
        return div;
    }
    
    addAlertToList(alert) {
        const alertContainer = document.getElementById('alert-list');
        if (!alertContainer) return;
        
        const alertElement = this.createAlertElement(alert);
        
        // Add to top of list
        if (alertContainer.firstChild) {
            alertContainer.insertBefore(alertElement, alertContainer.firstChild);
        } else {
            alertContainer.appendChild(alertElement);
        }
        
        // Remove old alerts (keep only last 10)
        while (alertContainer.children.length > 10) {
            alertContainer.removeChild(alertContainer.lastChild);
        }
        
        // Animate new alert
        alertElement.style.opacity = '0';
        alertElement.style.transform = 'translateX(-20px)';
        
        setTimeout(() => {
            alertElement.style.transition = 'all 0.3s ease';
            alertElement.style.opacity = '1';
            alertElement.style.transform = 'translateX(0)';
        }, 10);
    }
    
    createAlertElement(alert) {
        const div = document.createElement('div');
        const severityClass = alert.severity === 'HIGH' ? 'high-risk' : 'medium-risk';
        const icon = alert.severity === 'HIGH' ? 'fa-exclamation-triangle' : 'fa-exclamation-circle';
        
        div.className = `alert-item ${severityClass}`;
        div.innerHTML = `
            <div class="d-flex align-items-center justify-content-between">
                <div class="d-flex align-items-center">
                    <i class="fas ${icon} me-2"></i>
                    <div>
                        <strong>Transaction ${alert.transaction_id}</strong><br>
                        <small>
                            Amount: ${alert.amount} • 
                            Risk: ${(alert.fraud_probability * 100).toFixed(1)}%
                        </small>
                    </div>
                </div>
                <div class="text-end">
                    <span class="badge bg-${alert.severity === 'HIGH' ? 'danger' : 'warning'}">
                        ${alert.severity}
                    </span><br>
                    <small class="text-muted">
                        ${new Date(alert.timestamp).toLocaleTimeString()}
                    </small>
                </div>
            </div>
        `;
        
        return div;
    }
    
    updateSystemHealth(status) {
        Object.entries(status).forEach(([component, health]) => {
            const healthElement = document.getElementById(`${component}-health`);
            if (healthElement) {
                const statusClass = health === 'healthy' ? 'bg-success' : 'bg-danger';
                const statusText = health === 'healthy' ? 'Online' : 'Offline';
                
                healthElement.className = `badge ${statusClass}`;
                healthElement.textContent = statusText;
            }
        });
    }
    
    // ===== Notification Methods =====
    showTransactionAlert(transaction) {
        const message = `High-risk transaction detected: ${transaction.amount} (${(transaction.fraud_probability * 100).toFixed(1)}% risk)`;
        this.showNotification(message, 'warning', 5000);
    }
    
    showAlertNotification(alert) {
        const severity = alert.severity === 'HIGH' ? 'danger' : 'warning';
        const message = `${alert.severity} fraud alert: Transaction ${alert.transaction_id}`;
        this.showNotification(message, severity, 7000);
    }
    
    showNotification(message, type = 'info', duration = 3000) {
        // Use the global notification system if available
        if (window.fraudApp && window.fraudApp.showNotification) {
            window.fraudApp.showNotification(message, type, duration);
        } else {
            // Fallback to console
            console.log(`📢 ${type.toUpperCase()}: ${message}`);
        }
    }
    
    showMaxReconnectError() {
        this.showNotification(
            'Connection lost. Please refresh the page to reconnect.',
            'error',
            0 // Don't auto-dismiss
        );
    }
    
    // ===== Audio Alerts =====
    playAlertSound(severity) {
        try {
            // Only play if user has interacted with the page (browser requirement)
            if (this.canPlayAudio()) {
                const frequency = severity === 'HIGH' ? 800 : 600;
                const duration = severity === 'HIGH' ? 300 : 200;
                this.playTone(frequency, duration);
            }
        } catch (error) {
            console.warn('⚠️ Could not play alert sound:', error);
        }
    }
    
    canPlayAudio() {
        // Check if user has interacted with the page
        return document.hasStoredUserActivation || document.userActivation?.hasBeenActive;
    }
    
    playTone(frequency, duration) {
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        oscillator.frequency.setValueAtTime(frequency, audioContext.currentTime);
        oscillator.type = 'sine';
        
        gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + duration / 1000);
        
        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + duration / 1000);
    }
    
    // ===== Utility Methods =====
    getRiskClass(fraudProbability) {
        if (fraudProbability > 0.7) return 'badge-risk-high';
        if (fraudProbability > 0.3) return 'badge-risk-medium';
        return 'badge-risk-low';
    }
    
    showTransactionDetails(transaction) {
        // Create or update transaction details modal
        const modalId = 'transactionDetailModal';
        let modal = document.getElementById(modalId);
        
        if (!modal) {
            modal = this.createTransactionDetailModal(modalId);
            document.body.appendChild(modal);
        }
        
        this.populateTransactionModal(modal, transaction);
        
        // Show modal
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
    }
    
    createTransactionDetailModal(modalId) {
        const modal = document.createElement('div');
        modal.id = modalId;
        modal.className = 'modal fade';
        modal.tabIndex = -1;
        
        modal.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Transaction Details</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body" id="${modalId}-body">
                        <!-- Content will be populated dynamically -->
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    </div>
                </div>
            </div>
        `;
        
        return modal;
    }
    
    populateTransactionModal(modal, transaction) {
        const body = modal.querySelector('.modal-body');
        const riskClass = this.getRiskClass(transaction.fraud_probability);
        const statusClass = transaction.is_fraud ? 'danger' : 'success';
        const statusText = transaction.is_fraud ? 'Fraudulent' : 'Legitimate';
        
        body.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <h6>Transaction Information</h6>
                    <table class="table table-sm">
                        <tr>
                            <td><strong>ID:</strong></td>
                            <td class="font-monospace">${transaction.transaction_id}</td>
                        </tr>
                        <tr>
                            <td><strong>Amount:</strong></td>
                            <td>${transaction.amount?.toFixed(2) || '0.00'}</td>
                        </tr>
                        <tr>
                            <td><strong>Category:</strong></td>
                            <td>${transaction.merchant_category || 'Unknown'}</td>
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
                    <h6>Risk Assessment</h6>
                    <div class="text-center mb-3">
                        <div class="h3 mb-0">
                            <span class="badge ${riskClass} fs-4">
                                ${(transaction.fraud_probability * 100).toFixed(1)}%
                            </span>
                        </div>
                        <small class="text-muted">Fraud Probability</small>
                    </div>
                    <div class="text-center">
                        <span class="badge bg-${statusClass} fs-6 p-2">${statusText}</span>
                    </div>
                </div>
            </div>
        `;
    }
    
    // ===== Public API =====
    disconnect() {
        if (this.socket) {
            this.socket.close(1000, 'Manual disconnect');
        }
        this.stopHeartbeat();
    }
    
    reconnect() {
        this.disconnect();
        setTimeout(() => {
            this.reconnectAttempts = 0;
            this.connect();
        }, 1000);
    }
    
    getConnectionState() {
        return {
            isConnected: this.isConnected,
            readyState: this.socket?.readyState,
            url: this.url,
            reconnectAttempts: this.reconnectAttempts
        };
    }
}

// Export for use in other modules
if (typeof window !== 'undefined') {
    window.WebSocketManager = WebSocketManager;
}

if (typeof module !== 'undefined' && module.exports) {
    module.exports = WebSocketManager;
}