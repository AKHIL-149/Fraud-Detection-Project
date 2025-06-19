/**
 * Fraud Tester Component
 * Interactive tool for testing fraud detection with custom transaction parameters
 */

class FraudTester {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        this.options = {
            apiEndpoint: options.apiEndpoint || '/api/transactions/test-fraud',
            enableRealTimeTest: options.enableRealTimeTest || false,
            showAdvancedOptions: options.showAdvancedOptions || true,
            ...options
        };
        
        this.currentTransaction = null;
        this.testResults = [];
        this.isTestingRealTime = false;
        
        this.init();
    }

    init() {
        this.createFraudTester();
        this.bindEvents();
        this.loadDefaultValues();
    }

    createFraudTester() {
        this.container.innerHTML = `
            <div class="fraud-tester">
                <!-- Fraud Tester Header -->
                <div class="fraud-tester-header">
                    <h4>Fraud Detection Tester</h4>
                    <p class="text-muted">Test fraud detection algorithms with custom transaction parameters</p>
                </div>

                <!-- Test Configuration Tabs -->
                <ul class="nav nav-tabs" id="testerTabs" role="tablist">
                    <li class="nav-item" role="presentation">
                        <button class="nav-link active" id="basic-tab" data-bs-toggle="tab" 
                                data-bs-target="#basic" type="button">Basic Test</button>
                    </li>
                    <li class="nav-item" role="presentation">
                        <button class="nav-link" id="advanced-tab" data-bs-toggle="tab" 
                                data-bs-target="#advanced" type="button">Advanced Test</button>
                    </li>
                    <li class="nav-item" role="presentation">
                        <button class="nav-link" id="batch-tab" data-bs-toggle="tab" 
                                data-bs-target="#batch" type="button">Batch Test</button>
                    </li>
                    <li class="nav-item" role="presentation">
                        <button class="nav-link" id="results-tab" data-bs-toggle="tab" 
                                data-bs-target="#results" type="button">Results History</button>
                    </li>
                </ul>

                <div class="tab-content" id="testerTabContent">
                    <!-- Basic Test Tab -->
                    <div class="tab-pane fade show active" id="basic" role="tabpanel">
                        <div class="fraud-tester-form">
                            <form id="basicTestForm">
                                <div class="row">
                                    <!-- Basic Transaction Details -->
                                    <div class="col-md-6">
                                        <h5>Transaction Details</h5>
                                        
                                        <div class="mb-3">
                                            <label for="transactionAmount" class="form-label">Amount ($)</label>
                                            <input type="range" class="form-range" id="transactionAmount" 
                                                   min="1" max="10000" value="100" step="1">
                                            <div class="range-value">$<span id="amountValue">100</span></div>
                                        </div>

                                        <div class="mb-3">
                                            <label for="merchantCategory" class="form-label">Merchant Category</label>
                                            <select class="form-select" id="merchantCategory">
                                                <option value="grocery">Grocery</option>
                                                <option value="gas">Gas Station</option>
                                                <option value="restaurant">Restaurant</option>
                                                <option value="online">Online</option>
                                                <option value="atm">ATM</option>
                                                <option value="retail">Retail</option>
                                                <option value="entertainment">Entertainment</option>
                                                <option value="travel">Travel</option>
                                                <option value="healthcare">Healthcare</option>
                                            </select>
                                        </div>

                                        <div class="mb-3">
                                            <label for="transactionType" class="form-label">Transaction Type</label>
                                            <select class="form-select" id="transactionType">
                                                <option value="purchase">Purchase</option>
                                                <option value="withdrawal">Withdrawal</option>
                                                <option value="transfer">Transfer</option>
                                                <option value="payment">Payment</option>
                                                <option value="refund">Refund</option>
                                            </select>
                                        </div>

                                        <div class="mb-3">
                                            <label for="location" class="form-label">Location</label>
                                            <select class="form-select" id="location">
                                                <option value="New York">New York</option>
                                                <option value="Los Angeles">Los Angeles</option>
                                                <option value="Chicago">Chicago</option>
                                                <option value="Houston">Houston</option>
                                                <option value="Phoenix">Phoenix</option>
                                                <option value="Philadelphia">Philadelphia</option>
                                                <option value="San Antonio">San Antonio</option>
                                                <option value="San Diego">San Diego</option>
                                                <option value="Dallas">Dallas</option>
                                                <option value="International">International</option>
                                            </select>
                                        </div>
                                    </div>

                                    <!-- Risk Factors -->
                                    <div class="col-md-6">
                                        <h5>Risk Factors</h5>
                                        
                                        <div class="mb-3">
                                            <label for="hourOfDay" class="form-label">Hour of Day</label>
                                            <input type="range" class="form-range" id="hourOfDay" 
                                                   min="0" max="23" value="12" step="1">
                                            <div class="range-value"><span id="hourValue">12</span>:00</div>
                                        </div>

                                        <div class="mb-3">
                                            <label for="velocityFactor" class="form-label">Transaction Velocity</label>
                                            <input type="range" class="form-range" id="velocityFactor" 
                                                   min="1" max="10" value="3" step="1">
                                            <div class="range-value"><span id="velocityValue">3</span> transactions/hour</div>
                                        </div>

                                        <div class="mb-3">
                                            <label for="merchantRisk" class="form-label">Merchant Risk Score</label>
                                            <input type="range" class="form-range" id="merchantRisk" 
                                                   min="0" max="100" value="30" step="1">
                                            <div class="range-value"><span id="merchantRiskValue">30</span>%</div>
                                        </div>

                                        <div class="mb-3">
                                            <div class="form-check">
                                                <input class="form-check-input" type="checkbox" id="isWeekend">
                                                <label class="form-check-label" for="isWeekend">
                                                    Weekend Transaction
                                                </label>
                                            </div>
                                        </div>

                                        <div class="mb-3">
                                            <div class="form-check">
                                                <input class="form-check-input" type="checkbox" id="newDevice">
                                                <label class="form-check-label" for="newDevice">
                                                    New Device
                                                </label>
                                            </div>
                                        </div>

                                        <div class="mb-3">
                                            <div class="form-check">
                                                <input class="form-check-input" type="checkbox" id="foreignLocation">
                                                <label class="form-check-label" for="foreignLocation">
                                                    Foreign Location
                                                </label>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <!-- Test Controls -->
                                <div class="test-controls mt-4">
                                    <div class="row">
                                        <div class="col-md-8">
                                            <button type="submit" class="btn btn-primary btn-lg" id="runBasicTest">
                                                <i class="fas fa-play"></i> Run Fraud Test
                                            </button>
                                            <button type="button" class="btn btn-secondary" id="randomizeValues">
                                                <i class="fas fa-random"></i> Randomize
                                            </button>
                                            <button type="button" class="btn btn-warning" id="presetHighRisk">
                                                <i class="fas fa-exclamation-triangle"></i> High Risk Preset
                                            </button>
                                        </div>
                                        <div class="col-md-4 text-end">
                                            <div class="form-check form-switch">
                                                <input class="form-check-input" type="checkbox" id="realTimeTest">
                                                <label class="form-check-label" for="realTimeTest">
                                                    Real-time Testing
                                                </label>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </form>
                        </div>

                        <!-- Test Results -->
                        <div class="test-results" id="basicTestResults" style="display: none;">
                            <div class="results-header">
                                <h5>Test Results</h5>
                                <button class="btn btn-sm btn-outline-secondary" id="clearResults">
                                    <i class="fas fa-trash"></i> Clear
                                </button>
                            </div>
                            <div class="results-content" id="basicResultsContent">
                                <!-- Results will be populated here -->
                            </div>
                        </div>
                    </div>

                    <!-- Advanced Test Tab -->
                    <div class="tab-pane fade" id="advanced" role="tabpanel">
                        <div class="advanced-tester-form">
                            <form id="advancedTestForm">
                                <div class="row">
                                    <div class="col-md-4">
                                        <h5>User Profile</h5>
                                        
                                        <div class="mb-3">
                                            <label for="userAge" class="form-label">User Age</label>
                                            <input type="number" class="form-control" id="userAge" value="35" min="18" max="100">
                                        </div>

                                        <div class="mb-3">
                                            <label for="accountAge" class="form-label">Account Age (months)</label>
                                            <input type="number" class="form-control" id="accountAge" value="24" min="1" max="600">
                                        </div>

                                        <div class="mb-3">
                                            <label for="creditScore" class="form-label">Credit Score</label>
                                            <input type="number" class="form-control" id="creditScore" value="750" min="300" max="850">
                                        </div>

                                        <div class="mb-3">
                                            <label for="avgMonthlySpend" class="form-label">Avg Monthly Spend ($)</label>
                                            <input type="number" class="form-control" id="avgMonthlySpend" value="2500" min="0" max="50000">
                                        </div>
                                    </div>

                                    <div class="col-md-4">
                                        <h5>Transaction Context</h5>
                                        
                                        <div class="mb-3">
                                            <label for="deviceFingerprint" class="form-label">Device Fingerprint Risk</label>
                                            <input type="range" class="form-range" id="deviceFingerprint" 
                                                   min="0" max="100" value="20" step="1">
                                            <div class="range-value"><span id="deviceFingerprintValue">20</span>%</div>
                                        </div>

                                        <div class="mb-3">
                                            <label for="ipRisk" class="form-label">IP Address Risk</label>
                                            <input type="range" class="form-range" id="ipRisk" 
                                                   min="0" max="100" value="15" step="1">
                                            <div class="range-value"><span id="ipRiskValue">15</span>%</div>
                                        </div>

                                        <div class="mb-3">
                                            <label for="timeSinceLastTxn" class="form-label">Time Since Last Transaction (hours)</label>
                                            <input type="number" class="form-control" id="timeSinceLastTxn" value="2" min="0" max="168">
                                        </div>

                                        <div class="mb-3">
                                            <label for="geographicRisk" class="form-label">Geographic Risk</label>
                                            <input type="range" class="form-range" id="geographicRisk" 
                                                   min="0" max="100" value="25" step="1">
                                            <div class="range-value"><span id="geographicRiskValue">25</span>%</div>
                                        </div>
                                    </div>

                                    <div class="col-md-4">
                                        <h5>Behavioral Patterns</h5>
                                        
                                        <div class="mb-3">
                                            <label for="spendingPattern" class="form-label">Spending Pattern Deviation</label>
                                            <input type="range" class="form-range" id="spendingPattern" 
                                                   min="0" max="100" value="30" step="1">
                                            <div class="range-value"><span id="spendingPatternValue">30</span>%</div>
                                        </div>

                                        <div class="mb-3">
                                            <label for="frequencyDeviation" class="form-label">Frequency Deviation</label>
                                            <input type="range" class="form-range" id="frequencyDeviation" 
                                                   min="0" max="100" value="20" step="1">
                                            <div class="range-value"><span id="frequencyDeviationValue">20</span>%</div>
                                        </div>

                                        <div class="mb-3">
                                            <div class="form-check">
                                                <input class="form-check-input" type="checkbox" id="unusualMerchant">
                                                <label class="form-check-label" for="unusualMerchant">
                                                    Unusual Merchant for User
                                                </label>
                                            </div>
                                        </div>

                                        <div class="mb-3">
                                            <div class="form-check">
                                                <input class="form-check-input" type="checkbox" id="roundAmount">
                                                <label class="form-check-label" for="roundAmount">
                                                    Round Amount (Suspicious)
                                                </label>
                                            </div>
                                        </div>

                                        <div class="mb-3">
                                            <div class="form-check">
                                                <input class="form-check-input" type="checkbox" id="vpnUsage">
                                                <label class="form-check-label" for="vpnUsage">
                                                    VPN Usage Detected
                                                </label>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <div class="test-controls mt-4">
                                    <button type="submit" class="btn btn-primary btn-lg">
                                        <i class="fas fa-cog"></i> Run Advanced Test
                                    </button>
                                    <button type="button" class="btn btn-secondary" id="saveAdvancedPreset">
                                        <i class="fas fa-save"></i> Save Preset
                                    </button>
                                    <button type="button" class="btn btn-outline-secondary" id="loadAdvancedPreset">
                                        <i class="fas fa-folder-open"></i> Load Preset
                                    </button>
                                </div>
                            </form>
                        </div>

                        <!-- Advanced Test Results -->
                        <div class="test-results" id="advancedTestResults" style="display: none;">
                            <div class="results-content" id="advancedResultsContent">
                                <!-- Advanced results will be populated here -->
                            </div>
                        </div>
                    </div>

                    <!-- Batch Test Tab -->
                    <div class="tab-pane fade" id="batch" role="tabpanel">
                        <div class="batch-tester">
                            <h5>Batch Testing</h5>
                            <p class="text-muted">Test multiple transactions at once or upload a CSV file</p>

                            <div class="batch-options">
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="card">
                                            <div class="card-body">
                                                <h6 class="card-title">Generate Random Batch</h6>
                                                <div class="mb-3">
                                                    <label for="batchSize" class="form-label">Number of Transactions</label>
                                                    <input type="number" class="form-control" id="batchSize" value="100" min="1" max="1000">
                                                </div>
                                                <div class="mb-3">
                                                    <label for="fraudPercentage" class="form-label">Expected Fraud Percentage</label>
                                                    <input type="range" class="form-range" id="fraudPercentage" 
                                                           min="0" max="50" value="5" step="1">
                                                    <div class="range-value"><span id="fraudPercentageValue">5</span>%</div>
                                                </div>
                                                <button class="btn btn-primary" id="generateBatch">
                                                    <i class="fas fa-random"></i> Generate Batch
                                                </button>
                                            </div>
                                        </div>
                                    </div>

                                    <div class="col-md-6">
                                        <div class="card">
                                            <div class="card-body">
                                                <h6 class="card-title">Upload CSV File</h6>
                                                <div class="mb-3">
                                                    <input type="file" class="form-control" id="csvUpload" accept=".csv">
                                                    <div class="form-text">
                                                        Upload a CSV file with transaction data for batch testing
                                                    </div>
                                                </div>
                                                <button class="btn btn-success" id="uploadBatch" disabled>
                                                    <i class="fas fa-upload"></i> Process CSV
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- Batch Progress -->
                            <div class="batch-progress" id="batchProgress" style="display: none;">
                                <div class="progress-header">
                                    <h6>Processing Batch...</h6>
                                    <button class="btn btn-sm btn-outline-danger" id="cancelBatch">
                                        <i class="fas fa-stop"></i> Cancel
                                    </button>
                                </div>
                                <div class="progress mb-3">
                                    <div class="progress-bar" id="batchProgressBar" style="width: 0%"></div>
                                </div>
                                <div class="progress-stats">
                                    <span>Processed: <strong id="processedCount">0</strong></span>
                                    <span>Fraud Detected: <strong id="fraudDetectedCount">0</strong></span>
                                    <span>Processing Rate: <strong id="processingRate">0</strong> txn/sec</span>
                                </div>
                            </div>

                            <!-- Batch Results -->
                            <div class="batch-results" id="batchResults" style="display: none;">
                                <div class="results-summary">
                                    <h6>Batch Test Summary</h6>
                                    <div class="row">
                                        <div class="col-md-3">
                                            <div class="stat-card">
                                                <div class="stat-value" id="totalProcessed">0</div>
                                                <div class="stat-label">Total Processed</div>
                                            </div>
                                        </div>
                                        <div class="col-md-3">
                                            <div class="stat-card fraud">
                                                <div class="stat-value" id="totalFraud">0</div>
                                                <div class="stat-label">Fraud Detected</div>
                                            </div>
                                        </div>
                                        <div class="col-md-3">
                                            <div class="stat-card">
                                                <div class="stat-value" id="falsePositives">0</div>
                                                <div class="stat-label">False Positives</div>
                                            </div>
                                        </div>
                                        <div class="col-md-3">
                                            <div class="stat-card">
                                                <div class="stat-value" id="avgProcessingTime">0ms</div>
                                                <div class="stat-label">Avg Processing Time</div>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <div class="results-actions mt-3">
                                    <button class="btn btn-primary" id="downloadResults">
                                        <i class="fas fa-download"></i> Download Results
                                    </button>
                                    <button class="btn btn-secondary" id="viewDetailedResults">
                                        <i class="fas fa-table"></i> View Details
                                    </button>
                                    <button class="btn btn-outline-danger" id="clearBatchResults">
                                        <i class="fas fa-trash"></i> Clear Results
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Results History Tab -->
                    <div class="tab-pane fade" id="results" role="tabpanel">
                        <div class="results-history">
                            <div class="results-header">
                                <h5>Test Results History</h5>
                                <div class="results-filters">
                                    <select class="form-select form-select-sm" id="resultsFilter">
                                        <option value="all">All Tests</option>
                                        <option value="basic">Basic Tests</option>
                                        <option value="advanced">Advanced Tests</option>
                                        <option value="batch">Batch Tests</option>
                                    </select>
                                    <button class="btn btn-sm btn-outline-primary" id="exportHistory">
                                        <i class="fas fa-file-export"></i> Export
                                    </button>
                                </div>
                            </div>

                            <div class="results-list" id="resultsHistoryList">
                                <!-- Results history will be populated here -->
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    bindEvents() {
        // Range sliders
        this.bindRangeSliders();

        // Basic test form
        document.getElementById('basicTestForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.runBasicTest();
        });

        // Advanced test form
        document.getElementById('advancedTestForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.runAdvancedTest();
        });

        // Control buttons
        document.getElementById('randomizeValues').addEventListener('click', () => {
            this.randomizeBasicValues();
        });

        document.getElementById('presetHighRisk').addEventListener('click', () => {
            this.loadHighRiskPreset();
        });

        document.getElementById('clearResults').addEventListener('click', () => {
            this.clearTestResults();
        });

        // Real-time testing
        document.getElementById('realTimeTest').addEventListener('change', (e) => {
            this.toggleRealTimeTest(e.target.checked);
        });

        // Batch testing
        document.getElementById('generateBatch').addEventListener('click', () => {
            this.generateBatchTest();
        });

        document.getElementById('csvUpload').addEventListener('change', (e) => {
            document.getElementById('uploadBatch').disabled = !e.target.files.length;
        });

        document.getElementById('uploadBatch').addEventListener('click', () => {
            this.processCsvBatch();
        });

        // Advanced presets
        document.getElementById('saveAdvancedPreset').addEventListener('click', () => {
            this.saveAdvancedPreset();
        });

        document.getElementById('loadAdvancedPreset').addEventListener('click', () => {
            this.loadAdvancedPreset();
        });

        // Results history
        document.getElementById('resultsFilter').addEventListener('change', (e) => {
            this.filterResultsHistory(e.target.value);
        });

        document.getElementById('exportHistory').addEventListener('click', () => {
            this.exportResultsHistory();
        });
    }

    bindRangeSliders() {
        const rangeSliders = [
            { id: 'transactionAmount', display: 'amountValue', prefix: ' },
            { id: 'hourOfDay', display: 'hourValue', suffix: ':00' },
            { id: 'velocityFactor', display: 'velocityValue', suffix: ' transactions/hour' },
            { id: 'merchantRisk', display: 'merchantRiskValue', suffix: '%' },
            { id: 'deviceFingerprint', display: 'deviceFingerprintValue', suffix: '%' },
            { id: 'ipRisk', display: 'ipRiskValue', suffix: '%' },
            { id: 'geographicRisk', display: 'geographicRiskValue', suffix: '%' },
            { id: 'spendingPattern', display: 'spendingPatternValue', suffix: '%' },
            { id: 'frequencyDeviation', display: 'frequencyDeviationValue', suffix: '%' },
            { id: 'fraudPercentage', display: 'fraudPercentageValue', suffix: '%' }
        ];

        rangeSliders.forEach(slider => {
            const element = document.getElementById(slider.id);
            const display = document.getElementById(slider.display);
            
            if (element && display) {
                element.addEventListener('input', (e) => {
                    const value = e.target.value;
                    const prefix = slider.prefix || '';
                    const suffix = slider.suffix || '';
                    display.textContent = `${prefix}${value}${suffix}`;
                });
            }
        });
    }

    loadDefaultValues() {
        // Set default values for range sliders
        document.getElementById('amountValue').textContent = '100';
        document.getElementById('hourValue').textContent = '12';
        document.getElementById('velocityValue').textContent = '3';
        document.getElementById('merchantRiskValue').textContent = '30';
        document.getElementById('deviceFingerprintValue').textContent = '20';
        document.getElementById('ipRiskValue').textContent = '15';
        document.getElementById('geographicRiskValue').textContent = '25';
        document.getElementById('spendingPatternValue').textContent = '30';
        document.getElementById('frequencyDeviationValue').textContent = '20';
        document.getElementById('fraudPercentageValue').textContent = '5';
    }

    async runBasicTest() {
        const formData = this.getBasicTestData();
        
        try {
            document.getElementById('runBasicTest').disabled = true;
            document.getElementById('runBasicTest').innerHTML = '<i class="fas fa-spinner fa-spin"></i> Testing...';

            const response = await fetch(this.options.apiEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    ...formData,
                    test_type: 'basic'
                })
            });

            if (response.ok) {
                const result = await response.json();
                this.displayBasicTestResult(result);
                this.addToHistory(result, 'basic');
            } else {
                throw new Error('Test failed');
            }
        } catch (error) {
            console.error('Error running basic test:', error);
            this.showError('Failed to run fraud test');
        } finally {
            document.getElementById('runBasicTest').disabled = false;
            document.getElementById('runBasicTest').innerHTML = '<i class="fas fa-play"></i> Run Fraud Test';
        }
    }

    async runAdvancedTest() {
        const formData = this.getAdvancedTestData();
        
        try {
            const response = await fetch(this.options.apiEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    ...formData,
                    test_type: 'advanced'
                })
            });

            if (response.ok) {
                const result = await response.json();
                this.displayAdvancedTestResult(result);
                this.addToHistory(result, 'advanced');
            } else {
                throw new Error('Advanced test failed');
            }
        } catch (error) {
            console.error('Error running advanced test:', error);
            this.showError('Failed to run advanced fraud test');
        }
    }

    getBasicTestData() {
        return {
            amount: parseFloat(document.getElementById('transactionAmount').value),
            merchant_category: document.getElementById('merchantCategory').value,
            transaction_type: document.getElementById('transactionType').value,
            location: document.getElementById('location').value,
            hour_of_day: parseInt(document.getElementById('hourOfDay').value),
            velocity_factor: parseInt(document.getElementById('velocityFactor').value),
            merchant_risk_score: parseFloat(document.getElementById('merchantRisk').value) / 100,
            is_weekend: document.getElementById('isWeekend').checked,
            new_device: document.getElementById('newDevice').checked,
            foreign_location: document.getElementById('foreignLocation').checked
        };
    }

    getAdvancedTestData() {
        const basicData = this.getBasicTestData();
        
        return {
            ...basicData,
            user_age: parseInt(document.getElementById('userAge').value),
            account_age_months: parseInt(document.getElementById('accountAge').value),
            credit_score: parseInt(document.getElementById('creditScore').value),
            avg_monthly_spend: parseFloat(document.getElementById('avgMonthlySpend').value),
            device_fingerprint_risk: parseFloat(document.getElementById('deviceFingerprint').value) / 100,
            ip_risk_score: parseFloat(document.getElementById('ipRisk').value) / 100,
            time_since_last_txn: parseFloat(document.getElementById('timeSinceLastTxn').value),
            geographic_risk: parseFloat(document.getElementById('geographicRisk').value) / 100,
            spending_pattern_deviation: parseFloat(document.getElementById('spendingPattern').value) / 100,
            frequency_deviation: parseFloat(document.getElementById('frequencyDeviation').value) / 100,
            unusual_merchant: document.getElementById('unusualMerchant').checked,
            round_amount: document.getElementById('roundAmount').checked,
            vpn_usage: document.getElementById('vpnUsage').checked
        };
    }

    displayBasicTestResult(result) {
        const resultsContainer = document.getElementById('basicTestResults');
        const resultsContent = document.getElementById('basicResultsContent');
        
        const riskScore = result.risk_score * 100;
        const riskLevel = this.getRiskLevel(result.risk_score);
        
        resultsContent.innerHTML = `
            <div class="test-result-card ${riskLevel.toLowerCase()}">
                <div class="result-header">
                    <div class="risk-score">
                        <div class="score-circle ${riskLevel.toLowerCase()}">
                            <span class="score-value">${riskScore.toFixed(1)}%</span>
                        </div>
                        <div class="risk-label">
                            <strong>Risk Level: ${riskLevel}</strong>
                            <div class="prediction">${result.is_fraud ? 'FRAUD DETECTED' : 'LEGITIMATE'}</div>
                        </div>
                    </div>
                    <div class="test-timestamp">
                        <small class="text-muted">Tested: ${new Date().toLocaleString()}</small>
                    </div>
                </div>
                
                <div class="result-details">
                    <div class="row">
                        <div class="col-md-6">
                            <h6>Transaction Details</h6>
                            <ul class="list-unstyled">
                                <li><strong>Amount:</strong> ${result.transaction.amount}</li>
                                <li><strong>Category:</strong> ${result.transaction.merchant_category}</li>
                                <li><strong>Type:</strong> ${result.transaction.transaction_type}</li>
                                <li><strong>Location:</strong> ${result.transaction.location}</li>
                                <li><strong>Time:</strong> ${result.transaction.hour_of_day}:00</li>
                            </ul>
                        </div>
                        <div class="col-md-6">
                            <h6>Risk Factors</h6>
                            <div class="risk-factors">
                                ${result.risk_factors.map(factor => `
                                    <div class="risk-factor ${factor.impact > 0.1 ? 'high-impact' : ''}">
                                        <span class="factor-name">${factor.name}</span>
                                        <span class="factor-impact">+${(factor.impact * 100).toFixed(1)}%</span>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="result-actions">
                    <button class="btn btn-sm btn-outline-primary" onclick="fraudTester.saveTestResult('${result.test_id}')">
                        <i class="fas fa-save"></i> Save Result
                    </button>
                    <button class="btn btn-sm btn-outline-secondary" onclick="fraudTester.shareTestResult('${result.test_id}')">
                        <i class="fas fa-share"></i> Share
                    </button>
                </div>
            </div>
        `;
        
        resultsContainer.style.display = 'block';
    }

    displayAdvancedTestResult(result) {
        const resultsContainer = document.getElementById('advancedTestResults');
        const resultsContent = document.getElementById('advancedResultsContent');
        
        const riskScore = result.risk_score * 100;
        const riskLevel = this.getRiskLevel(result.risk_score);
        
        resultsContent.innerHTML = `
            <div class="advanced-test-result">
                <div class="result-overview">
                                            <div class="risk-gauge">
                            <canvas id="riskGauge" width="200" height="200"></canvas>
                        </div>
                        <div class="risk-breakdown">
                            <h6>Model Confidence: ${(result.confidence * 100).toFixed(1)}%</h6>
                            <div class="model-scores">
                                ${result.model_scores.map(model => `
                                    <div class="model-score">
                                        <span class="model-name">${model.name}</span>
                                        <div class="score-bar">
                                            <div class="score-fill" style="width: ${model.score * 100}%"></div>
                                        </div>
                                        <span class="score-value">${(model.score * 100).toFixed(1)}%</span>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="detailed-analysis">
                    <div class="row">
                        <div class="col-md-4">
                            <h6>Feature Analysis</h6>
                            <div class="feature-importance">
                                ${result.feature_importance.map(feature => `
                                    <div class="feature-item">
                                        <div class="feature-name">${feature.name}</div>
                                        <div class="importance-bar">
                                            <div class="importance-fill" style="width: ${feature.importance * 100}%"></div>
                                        </div>
                                        <span class="importance-value">${(feature.importance * 100).toFixed(1)}%</span>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                        
                        <div class="col-md-4">
                            <h6>Behavioral Analysis</h6>
                            <div class="behavioral-metrics">
                                <div class="metric">
                                    <span class="metric-label">Spending Deviation:</span>
                                    <span class="metric-value ${result.behavioral.spending_deviation > 0.5 ? 'high' : 'normal'}">
                                        ${(result.behavioral.spending_deviation * 100).toFixed(1)}%
                                    </span>
                                </div>
                                <div class="metric">
                                    <span class="metric-label">Pattern Match:</span>
                                    <span class="metric-value ${result.behavioral.pattern_match < 0.5 ? 'low' : 'normal'}">
                                        ${(result.behavioral.pattern_match * 100).toFixed(1)}%
                                    </span>
                                </div>
                                <div class="metric">
                                    <span class="metric-label">Velocity Risk:</span>
                                    <span class="metric-value ${result.behavioral.velocity_risk > 0.7 ? 'high' : 'normal'}">
                                        ${(result.behavioral.velocity_risk * 100).toFixed(1)}%
                                    </span>
                                </div>
                            </div>
                        </div>
                        
                        <div class="col-md-4">
                            <h6>Risk Mitigation</h6>
                            <div class="mitigation-suggestions">
                                ${result.mitigation_suggestions.map(suggestion => `
                                    <div class="suggestion-item">
                                        <i class="fas fa-${suggestion.icon}"></i>
                                        <span>${suggestion.text}</span>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        resultsContainer.style.display = 'block';
        
        // Draw risk gauge
        this.drawRiskGauge('riskGauge', result.risk_score);
    }

    drawRiskGauge(canvasId, riskScore) {
        const canvas = document.getElementById(canvasId);
        const ctx = canvas.getContext('2d');
        const centerX = canvas.width / 2;
        const centerY = canvas.height / 2;
        const radius = 80;

        // Clear canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Draw gauge background
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, Math.PI, 2 * Math.PI);
        ctx.lineWidth = 20;
        ctx.strokeStyle = '#e0e0e0';
        ctx.stroke();

        // Draw risk score arc
        const angle = Math.PI + (riskScore * Math.PI);
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, Math.PI, angle);
        ctx.lineWidth = 20;
        
        // Color based on risk level
        if (riskScore < 0.3) {
            ctx.strokeStyle = '#28a745';
        } else if (riskScore < 0.7) {
            ctx.strokeStyle = '#ffc107';
        } else {
            ctx.strokeStyle = '#dc3545';
        }
        ctx.stroke();

        // Draw center text
        ctx.fillStyle = '#333';
        ctx.font = 'bold 24px Arial';
        ctx.textAlign = 'center';
        ctx.fillText(`${(riskScore * 100).toFixed(0)}%`, centerX, centerY + 8);
    }

    getRiskLevel(riskScore) {
        if (riskScore < 0.3) return 'LOW';
        if (riskScore < 0.7) return 'MEDIUM';
        return 'HIGH';
    }

    randomizeBasicValues() {
        // Randomize amount (weighted towards normal ranges)
        const amount = Math.random() < 0.8 ? 
            Math.random() * 500 + 10 : 
            Math.random() * 5000 + 500;
        document.getElementById('transactionAmount').value = Math.round(amount);
        document.getElementById('amountValue').textContent = Math.round(amount);

        // Randomize hour (weighted towards business hours)
        const hour = Math.random() < 0.7 ? 
            Math.floor(Math.random() * 12) + 9 : 
            Math.floor(Math.random() * 24);
        document.getElementById('hourOfDay').value = hour;
        document.getElementById('hourValue').textContent = hour;

        // Randomize other values
        document.getElementById('velocityFactor').value = Math.floor(Math.random() * 10) + 1;
        document.getElementById('velocityValue').textContent = document.getElementById('velocityFactor').value;

        document.getElementById('merchantRisk').value = Math.floor(Math.random() * 100);
        document.getElementById('merchantRiskValue').textContent = document.getElementById('merchantRisk').value;

        // Randomize checkboxes
        document.getElementById('isWeekend').checked = Math.random() > 0.7;
        document.getElementById('newDevice').checked = Math.random() > 0.8;
        document.getElementById('foreignLocation').checked = Math.random() > 0.9;

        // Randomize select options
        const categories = document.getElementById('merchantCategory').options;
        document.getElementById('merchantCategory').selectedIndex = Math.floor(Math.random() * categories.length);

        const types = document.getElementById('transactionType').options;
        document.getElementById('transactionType').selectedIndex = Math.floor(Math.random() * types.length);

        const locations = document.getElementById('location').options;
        document.getElementById('location').selectedIndex = Math.floor(Math.random() * locations.length);
    }

    loadHighRiskPreset() {
        // Set high-risk values
        document.getElementById('transactionAmount').value = 5000;
        document.getElementById('amountValue').textContent = '5000';

        document.getElementById('hourOfDay').value = 3;
        document.getElementById('hourValue').textContent = '3';

        document.getElementById('velocityFactor').value = 8;
        document.getElementById('velocityValue').textContent = '8';

        document.getElementById('merchantRisk').value = 80;
        document.getElementById('merchantRiskValue').textContent = '80';

        document.getElementById('isWeekend').checked = true;
        document.getElementById('newDevice').checked = true;
        document.getElementById('foreignLocation').checked = true;

        document.getElementById('merchantCategory').value = 'online';
        document.getElementById('transactionType').value = 'withdrawal';
        document.getElementById('location').value = 'International';
    }

    toggleRealTimeTest(enabled) {
        this.isTestingRealTime = enabled;
        
        if (enabled) {
            this.startRealTimeTest();
        } else {
            this.stopRealTimeTest();
        }
    }

    startRealTimeTest() {
        this.realTimeInterval = setInterval(() => {
            this.randomizeBasicValues();
            this.runBasicTest();
        }, 5000);
    }

    stopRealTimeTest() {
        if (this.realTimeInterval) {
            clearInterval(this.realTimeInterval);
            this.realTimeInterval = null;
        }
    }

    async generateBatchTest() {
        const batchSize = parseInt(document.getElementById('batchSize').value);
        const fraudPercentage = parseFloat(document.getElementById('fraudPercentage').value) / 100;

        try {
            document.getElementById('generateBatch').disabled = true;
            document.getElementById('batchProgress').style.display = 'block';

            const response = await fetch('/api/transactions/generate-batch', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    size: batchSize,
                    fraud_percentage: fraudPercentage
                })
            });

            if (response.ok) {
                const result = await response.json();
                this.processBatchResults(result);
            } else {
                throw new Error('Failed to generate batch');
            }
        } catch (error) {
            console.error('Error generating batch:', error);
            this.showError('Failed to generate batch test');
        } finally {
            document.getElementById('generateBatch').disabled = false;
        }
    }

    async processCsvBatch() {
        const fileInput = document.getElementById('csvUpload');
        const file = fileInput.files[0];

        if (!file) {
            this.showError('Please select a CSV file');
            return;
        }

        const formData = new FormData();
        formData.append('csv_file', file);

        try {
            document.getElementById('uploadBatch').disabled = true;
            document.getElementById('batchProgress').style.display = 'block';

            const response = await fetch('/api/transactions/batch-test', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const result = await response.json();
                this.processBatchResults(result);
            } else {
                throw new Error('Failed to process CSV batch');
            }
        } catch (error) {
            console.error('Error processing CSV batch:', error);
            this.showError('Failed to process CSV file');
        } finally {
            document.getElementById('uploadBatch').disabled = false;
        }
    }

    processBatchResults(result) {
        document.getElementById('batchProgress').style.display = 'none';
        document.getElementById('batchResults').style.display = 'block';

        // Update summary statistics
        document.getElementById('totalProcessed').textContent = result.total_processed;
        document.getElementById('totalFraud').textContent = result.fraud_detected;
        document.getElementById('falsePositives').textContent = result.false_positives;
        document.getElementById('avgProcessingTime').textContent = `${result.avg_processing_time}ms`;

        this.addToHistory(result, 'batch');
    }

    saveAdvancedPreset() {
        const presetData = this.getAdvancedTestData();
        const presetName = prompt('Enter preset name:');
        
        if (presetName) {
            const presets = JSON.parse(localStorage.getItem('fraudTesterPresets') || '{}');
            presets[presetName] = presetData;
            localStorage.setItem('fraudTesterPresets', JSON.stringify(presets));
            this.showSuccess(`Preset "${presetName}" saved`);
        }
    }

    loadAdvancedPreset() {
        const presets = JSON.parse(localStorage.getItem('fraudTesterPresets') || '{}');
        const presetNames = Object.keys(presets);
        
        if (presetNames.length === 0) {
            this.showError('No presets saved');
            return;
        }

        // Create preset selection modal
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Load Preset</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <select class="form-select" id="presetSelect">
                            ${presetNames.map(name => `<option value="${name}">${name}</option>`).join('')}
                        </select>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-primary" id="loadPreset">Load</button>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
        const bootstrapModal = new bootstrap.Modal(modal);
        bootstrapModal.show();

        modal.querySelector('#loadPreset').addEventListener('click', () => {
            const selectedPreset = modal.querySelector('#presetSelect').value;
            const presetData = presets[selectedPreset];
            this.applyAdvancedPreset(presetData);
            bootstrapModal.hide();
            modal.remove();
        });
    }

    applyAdvancedPreset(presetData) {
        // Apply basic values
        Object.keys(presetData).forEach(key => {
            const element = document.getElementById(key);
            if (element) {
                if (element.type === 'checkbox') {
                    element.checked = presetData[key];
                } else {
                    element.value = presetData[key];
                }
            }
        });

        // Update range slider displays
        this.bindRangeSliders();
    }

    addToHistory(result, testType) {
        const historyItem = {
            id: Date.now(),
            timestamp: new Date().toISOString(),
            type: testType,
            result: result
        };

        this.testResults.unshift(historyItem);
        
        // Limit history size
        if (this.testResults.length > 100) {
            this.testResults = this.testResults.slice(0, 100);
        }

        this.updateResultsHistory();
    }

    updateResultsHistory() {
        const historyList = document.getElementById('resultsHistoryList');
        
        if (this.testResults.length === 0) {
            historyList.innerHTML = `
                <div class="no-results text-center py-4">
                    <i class="fas fa-history fa-3x text-muted mb-3"></i>
                    <p class="text-muted">No test results yet</p>
                </div>
            `;
            return;
        }

        const historyHtml = this.testResults.map(item => `
            <div class="history-item" data-test-type="${item.type}">
                <div class="history-header">
                    <div class="test-info">
                        <span class="test-type badge badge-${item.type}">${item.type.toUpperCase()}</span>
                        <span class="test-timestamp">${new Date(item.timestamp).toLocaleString()}</span>
                    </div>
                    <div class="test-result">
                        <span class="risk-score ${this.getRiskLevel(item.result.risk_score).toLowerCase()}">
                            ${(item.result.risk_score * 100).toFixed(1)}%
                        </span>
                    </div>
                </div>
                <div class="history-actions">
                    <button class="btn btn-sm btn-outline-primary" onclick="fraudTester.viewHistoryDetails('${item.id}')">
                        <i class="fas fa-eye"></i> View
                    </button>
                    <button class="btn btn-sm btn-outline-secondary" onclick="fraudTester.rerunTest('${item.id}')">
                        <i class="fas fa-redo"></i> Rerun
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="fraudTester.removeFromHistory('${item.id}')">
                        <i class="fas fa-trash"></i> Remove
                    </button>
                </div>
            </div>
        `).join('');

        historyList.innerHTML = historyHtml;
    }

    filterResultsHistory(filterType) {
        const historyItems = document.querySelectorAll('.history-item');
        
        historyItems.forEach(item => {
            if (filterType === 'all' || item.dataset.testType === filterType) {
                item.style.display = 'block';
            } else {
                item.style.display = 'none';
            }
        });
    }

    exportResultsHistory() {
        const dataStr = JSON.stringify(this.testResults, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        
        const link = document.createElement('a');
        link.href = URL.createObjectURL(dataBlob);
        link.download = `fraud-test-history-${new Date().toISOString().split('T')[0]}.json`;
        link.click();
    }

    clearTestResults() {
        document.getElementById('basicTestResults').style.display = 'none';
        document.getElementById('advancedTestResults').style.display = 'none';
    }

    viewHistoryDetails(testId) {
        const historyItem = this.testResults.find(item => item.id == testId);
        if (!historyItem) return;

        // Show details in modal
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Test Result Details</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <pre>${JSON.stringify(historyItem.result, null, 2)}</pre>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
        const bootstrapModal = new bootstrap.Modal(modal);
        bootstrapModal.show();

        modal.addEventListener('hidden.bs.modal', () => {
            modal.remove();
        });
    }

    rerunTest(testId) {
        const historyItem = this.testResults.find(item => item.id == testId);
        if (!historyItem) return;

        // Apply the test parameters and run again
        if (historyItem.type === 'basic') {
            this.applyBasicTestData(historyItem.result.transaction);
            this.runBasicTest();
        } else if (historyItem.type === 'advanced') {
            this.applyAdvancedTestData(historyItem.result.transaction);
            this.runAdvancedTest();
        }
    }

    removeFromHistory(testId) {
        this.testResults = this.testResults.filter(item => item.id != testId);
        this.updateResultsHistory();
    }

    applyBasicTestData(transactionData) {
        Object.keys(transactionData).forEach(key => {
            const element = document.getElementById(key);
            if (element) {
                if (element.type === 'checkbox') {
                    element.checked = transactionData[key];
                } else {
                    element.value = transactionData[key];
                }
            }
        });
    }

    applyAdvancedTestData(transactionData) {
        this.applyBasicTestData(transactionData);
        // Additional advanced fields would be applied here
    }

    showSuccess(message) {
        this.showToast(message, 'success');
    }

    showError(message) {
        this.showToast(message, 'error');
    }

    showToast(message, type) {
        const toast = document.createElement('div');
        toast.className = `toast fraud-tester-toast ${type}`;
        toast.innerHTML = `
            <div class="toast-content">
                <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
                <span>${message}</span>
            </div>
        `;

        document.body.appendChild(toast);

        setTimeout(() => toast.classList.add('show'), 100);

        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    // Public method to destroy the component
    destroy() {
        if (this.realTimeInterval) {
            clearInterval(this.realTimeInterval);
        }
        this.container.innerHTML = '';
    }
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = FraudTester;
}

// Initialize global instance
let fraudTester;
document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('fraudTesterContainer');
    if (container) {
        fraudTester = new FraudTester('fraudTesterContainer');
    }
});