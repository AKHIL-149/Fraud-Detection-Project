"""
Plotly Dash Application for Fraud Detection Dashboard
Professional, interactive dashboard with real-time data visualization
"""

import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import pandas as pd
from datetime import datetime
import json

# Initialize Dash app with Bootstrap theme
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.CYBORG, dbc.icons.FONT_AWESOME],
    suppress_callback_exceptions=True,
    meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0'}]
)

app.title = "FraudGuard - ML Fraud Detection Dashboard"

# API Configuration
API_BASE_URL = 'http://localhost:5000'

# ==================== LAYOUT COMPONENTS ====================

def create_navbar():
    """Create navigation bar"""
    return dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("Dashboard", href="/", active="exact")),
            dbc.NavItem(dbc.NavLink("Predict", href="/predict", active="exact")),
            dbc.NavItem(dbc.NavLink("Alerts", href="/alerts", active="exact")),
            dbc.NavItem(dbc.NavLink("Monitoring", href="/monitoring", active="exact")),
            dbc.NavItem(dbc.NavLink("Reports", href="/reports", active="exact")),
        ],
        brand="🛡️ FraudGuard",
        brand_href="/",
        color="primary",
        dark=True,
        fluid=True,
        className="mb-4"
    )

def create_metric_card(title, value_id, icon, color="primary"):
    """Create a metric card component"""
    return dbc.Card([
        dbc.CardBody([
            html.Div([
                html.I(className=f"fas {icon} fa-3x mb-3", style={"color": f"var(--bs-{color})"}),
                html.H3(id=value_id, children="0", className="mb-1"),
                html.P(title, className="text-muted mb-0")
            ], className="text-center")
        ])
    ], className="h-100 shadow-sm")

# ==================== PAGE LAYOUTS ====================

def create_dashboard_layout():
    """Main dashboard page"""
    return dbc.Container([
        html.H1([html.I(className="fas fa-tachometer-alt me-2"), "Fraud Detection Dashboard"],
                className="mb-4 text-primary"),

        # Key Metrics Row
        dbc.Row([
            dbc.Col(create_metric_card("Total Transactions", "total-transactions", "fa-exchange-alt", "info"), md=3),
            dbc.Col(create_metric_card("Fraud Detected", "fraud-detected", "fa-exclamation-triangle", "danger"), md=3),
            dbc.Col(create_metric_card("Fraud Rate", "fraud-rate", "fa-percentage", "warning"), md=3),
            dbc.Col(create_metric_card("Amount at Risk", "amount-at-risk", "fa-dollar-sign", "success"), md=3),
        ], className="mb-4"),

        # Charts Row
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5([html.I(className="fas fa-chart-pie me-2"), "Risk Distribution"])),
                    dbc.CardBody([dcc.Graph(id="risk-distribution-chart", config={'displayModeBar': False})])
                ], className="shadow-sm h-100")
            ], md=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5([html.I(className="fas fa-chart-bar me-2"), "Transactions by Risk Level"])),
                    dbc.CardBody([dcc.Graph(id="risk-levels-chart", config={'displayModeBar': False})])
                ], className="shadow-sm h-100")
            ], md=6),
        ], className="mb-4"),

        # Recent Transactions
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.Div([
                            html.H5([html.I(className="fas fa-list me-2"), "Recent Transactions"], className="mb-0"),
                            dbc.Button([html.I(className="fas fa-sync me-2"), "Refresh"],
                                     id="refresh-dashboard", color="primary", size="sm")
                        ], className="d-flex justify-content-between align-items-center")
                    ]),
                    dbc.CardBody([
                        html.Div(id="recent-transactions-table")
                    ])
                ], className="shadow-sm")
            ], md=12)
        ]),

        # Auto-refresh interval
        dcc.Interval(id='dashboard-interval', interval=30*1000, n_intervals=0)
    ], fluid=True)

def create_predict_layout():
    """Prediction page"""
    return dbc.Container([
        html.H1([html.I(className="fas fa-brain me-2"), "Fraud Prediction"], className="mb-4 text-primary"),

        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5([html.I(className="fas fa-edit me-2"), "Transaction Details"])),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Amount ($)"),
                                dbc.Input(id="pred-amount", type="number", placeholder="100.00", step=0.01)
                            ], md=6),
                            dbc.Col([
                                dbc.Label("Merchant State"),
                                dbc.Select(id="pred-state", options=[
                                    {"label": "California (CA)", "value": "CA"},
                                    {"label": "New York (NY)", "value": "NY"},
                                    {"label": "Texas (TX)", "value": "TX"},
                                    {"label": "Florida (FL)", "value": "FL"},
                                    {"label": "Nevada (NV)", "value": "NV"},
                                ])
                            ], md=6)
                        ], className="mb-3"),

                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Merchant City"),
                                dbc.Input(id="pred-city", placeholder="San Francisco")
                            ], md=6),
                            dbc.Col([
                                dbc.Label("MCC"),
                                dbc.Select(id="pred-mcc", options=[
                                    {"label": "Grocery (5411)", "value": "5411"},
                                    {"label": "Gas Station (5541)", "value": "5541"},
                                    {"label": "Restaurant (5812)", "value": "5812"},
                                    {"label": "Jewelry (5944)", "value": "5944"},
                                    {"label": "Gambling (7995)", "value": "7995"},
                                ])
                            ], md=6)
                        ], className="mb-3"),

                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Transaction Type"),
                                dbc.Select(id="pred-chip", options=[
                                    {"label": "Chip Transaction", "value": "Chip Transaction"},
                                    {"label": "Swipe Transaction", "value": "Swipe Transaction"},
                                    {"label": "Online Transaction", "value": "Online Transaction"},
                                ])
                            ], md=12)
                        ], className="mb-3"),

                        dbc.Button([html.I(className="fas fa-check me-2"), "Analyze Transaction"],
                                 id="predict-button", color="primary", size="lg", className="w-100 mt-3")
                    ])
                ], className="shadow-sm mb-4"),

                # Quick scenarios
                dbc.Card([
                    dbc.CardHeader(html.H5([html.I(className="fas fa-bolt me-2"), "Quick Test Scenarios"])),
                    dbc.CardBody([
                        dbc.Button([html.I(className="fas fa-check-circle me-2"), "Low Risk"],
                                 id="scenario-low", color="success", className="w-100 mb-2"),
                        dbc.Button([html.I(className="fas fa-exclamation-triangle me-2"), "Medium Risk"],
                                 id="scenario-medium", color="warning", className="w-100 mb-2"),
                        dbc.Button([html.I(className="fas fa-times-circle me-2"), "High Risk"],
                                 id="scenario-high", color="danger", className="w-100")
                    ])
                ], className="shadow-sm")
            ], md=6),

            dbc.Col([
                html.Div(id="prediction-result")
            ], md=6)
        ])
    ], fluid=True)

def create_alerts_layout():
    """Alerts page"""
    return dbc.Container([
        html.H1([html.I(className="fas fa-bell me-2"), "Fraud Alerts"], className="mb-4 text-primary"),

        # Filters
        dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Severity Filter"),
                        dbc.Select(id="alert-severity-filter", options=[
                            {"label": "All Severities", "value": ""},
                            {"label": "Critical", "value": "critical"},
                            {"label": "High", "value": "high"},
                            {"label": "Medium", "value": "medium"}
                        ])
                    ], md=3),
                    dbc.Col([
                        dbc.Label("Limit"),
                        dbc.Select(id="alert-limit-filter", value="25", options=[
                            {"label": "10 Alerts", "value": "10"},
                            {"label": "25 Alerts", "value": "25"},
                            {"label": "50 Alerts", "value": "50"},
                            {"label": "100 Alerts", "value": "100"}
                        ])
                    ], md=3),
                    dbc.Col([
                        html.Label("\u00A0"),
                        dbc.Button([html.I(className="fas fa-sync me-2"), "Refresh"],
                                 id="refresh-alerts", color="primary", className="w-100")
                    ], md=3)
                ])
            ])
        ], className="mb-4 shadow-sm"),

        # Alert counts
        dbc.Row([
            dbc.Col(create_metric_card("Critical", "critical-count", "fa-exclamation-circle", "danger"), md=3),
            dbc.Col(create_metric_card("High", "high-count", "fa-exclamation-triangle", "warning"), md=3),
            dbc.Col(create_metric_card("Medium", "medium-count", "fa-info-circle", "info"), md=3),
            dbc.Col(create_metric_card("Total", "total-count", "fa-bell", "primary"), md=3),
        ], className="mb-4"),

        # Alerts list
        html.Div(id="alerts-container"),

        dcc.Interval(id='alerts-interval', interval=30*1000, n_intervals=0)
    ], fluid=True)

def create_monitoring_layout():
    """Monitoring page"""
    return dbc.Container([
        html.H1([html.I(className="fas fa-chart-line me-2"), "Real-Time Monitoring"],
                className="mb-4 text-primary"),

        # Live metrics
        dbc.Row([
            dbc.Col(create_metric_card("Recent Transactions", "monitor-txn-count", "fa-exchange-alt", "info"), md=4),
            dbc.Col(create_metric_card("Current Fraud Rate", "monitor-fraud-rate", "fa-percentage", "danger"), md=4),
            dbc.Col(create_metric_card("Average Risk", "monitor-avg-risk", "fa-chart-line", "warning"), md=4),
        ], className="mb-4"),

        # Timeline chart
        dbc.Card([
            dbc.CardHeader([
                html.Div([
                    html.H5([html.I(className="fas fa-chart-area me-2"), "Transaction Timeline"], className="mb-0"),
                    dbc.Button([html.I(className="fas fa-sync me-2"), "Refresh"],
                             id="refresh-monitoring", color="primary", size="sm")
                ], className="d-flex justify-content-between align-items-center")
            ]),
            dbc.CardBody([dcc.Graph(id="timeline-chart", config={'displayModeBar': False})])
        ], className="mb-4 shadow-sm"),

        # Transaction stream
        dbc.Card([
            dbc.CardHeader(html.H5([html.I(className="fas fa-stream me-2"), "Live Transaction Stream"])),
            dbc.CardBody([html.Div(id="transaction-stream")])
        ], className="shadow-sm"),

        dcc.Interval(id='monitoring-interval', interval=15*1000, n_intervals=0)
    ], fluid=True)

def create_reports_layout():
    """Reports page"""
    return dbc.Container([
        html.H1([html.I(className="fas fa-file-alt me-2"), "Analytics & Reports"],
                className="mb-4 text-primary"),

        # Merchant stats chart
        dbc.Card([
            dbc.CardHeader([
                html.Div([
                    html.H5([html.I(className="fas fa-map-marker-alt me-2"), "Merchant Statistics"], className="mb-0"),
                    dbc.Button([html.I(className="fas fa-sync me-2"), "Refresh"],
                             id="refresh-reports", color="primary", size="sm")
                ], className="d-flex justify-content-between align-items-center")
            ]),
            dbc.CardBody([dcc.Graph(id="merchant-chart", config={'displayModeBar': False})])
        ], className="mb-4 shadow-sm"),

        # Merchant table
        dbc.Card([
            dbc.CardHeader(html.H5([html.I(className="fas fa-table me-2"), "Detailed Merchant Analysis"])),
            dbc.CardBody([html.Div(id="merchant-table")])
        ], className="shadow-sm")
    ], fluid=True)

# ==================== APP LAYOUT ====================

app.layout = dbc.Container([
    dcc.Location(id='url', refresh=False),
    create_navbar(),
    html.Div(id='page-content'),
    dcc.Store(id='prediction-store')  # Store for prediction results
], fluid=True, className="dbc")

# ==================== CALLBACKS ====================

@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    """Route to different pages"""
    if pathname == '/predict':
        return create_predict_layout()
    elif pathname == '/alerts':
        return create_alerts_layout()
    elif pathname == '/monitoring':
        return create_monitoring_layout()
    elif pathname == '/reports':
        return create_reports_layout()
    else:
        return create_dashboard_layout()

# Dashboard callbacks
@app.callback(
    [Output('total-transactions', 'children'),
     Output('fraud-detected', 'children'),
     Output('fraud-rate', 'children'),
     Output('amount-at-risk', 'children'),
     Output('risk-distribution-chart', 'figure'),
     Output('risk-levels-chart', 'figure'),
     Output('recent-transactions-table', 'children')],
    [Input('dashboard-interval', 'n_intervals'),
     Input('refresh-dashboard', 'n_clicks')]
)
def update_dashboard(n, clicks):
    """Update dashboard data"""
    try:
        # Fetch statistics
        stats_response = requests.get(f'{API_BASE_URL}/api/statistics', timeout=5)
        stats = stats_response.json()

        # Fetch transactions
        trans_response = requests.get(f'{API_BASE_URL}/api/dashboard/recent-transactions?limit=100', timeout=5)
        trans_data = trans_response.json()
        transactions = trans_data.get('transactions', [])

        # Fetch risk distribution
        risk_response = requests.get(f'{API_BASE_URL}/api/dashboard/risk-distribution', timeout=5)
        risk_data = risk_response.json()
        distribution = risk_data.get('distribution', [])

        # Update metrics
        total_txn = stats.get('total_predictions', 0)
        fraud_count = stats.get('fraud_detected', 0)
        fraud_rate = f"{stats.get('fraud_rate', 0):.2f}%"
        amount = f"${stats.get('amount_at_risk', 0):,.0f}"

        # Risk distribution pie chart
        if distribution:
            risk_pie = px.pie(
                values=[d['count'] for d in distribution],
                names=[d['risk_level'].upper() for d in distribution],
                color_discrete_map={'LOW': '#28a745', 'MEDIUM': '#ffc107', 'HIGH': '#dc3545'}
            )
            risk_pie.update_layout(
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(t=0, b=0, l=0, r=0),
                height=300
            )
        else:
            risk_pie = go.Figure()
            risk_pie.add_annotation(text="No data available", xref="paper", yref="paper",
                                   x=0.5, y=0.5, showarrow=False)

        # Risk levels bar chart
        if distribution:
            risk_bar = px.bar(
                x=[d['risk_level'].upper() for d in distribution],
                y=[d['count'] for d in distribution],
                color=[d['risk_level'].upper() for d in distribution],
                color_discrete_map={'LOW': '#28a745', 'MEDIUM': '#ffc107', 'HIGH': '#dc3545'}
            )
            risk_bar.update_layout(
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                showlegend=False,
                margin=dict(t=20, b=40, l=40, r=20),
                height=300,
                xaxis_title="Risk Level",
                yaxis_title="Count"
            )
        else:
            risk_bar = go.Figure()
            risk_bar.add_annotation(text="No data available", xref="paper", yref="paper",
                                   x=0.5, y=0.5, showarrow=False)

        # Recent transactions table
        if transactions:
            table = dbc.Table([
                html.Thead(html.Tr([
                    html.Th("Transaction ID"),
                    html.Th("Amount"),
                    html.Th("Risk Score"),
                    html.Th("Status"),
                    html.Th("Timestamp")
                ])),
                html.Tbody([
                    html.Tr([
                        html.Td(html.Code(t['transaction_id'][:20] + "...")),
                        html.Td(f"${t['amount']:,.2f}"),
                        html.Td(dbc.Badge(f"{t['risk_score']*100:.1f}%",
                                         color="danger" if t['risk_score'] >= 0.7 else "warning" if t['risk_score'] >= 0.5 else "success")),
                        html.Td(dbc.Badge("FRAUD" if t['is_fraud'] else "SAFE",
                                         color="danger" if t['is_fraud'] else "success")),
                        html.Td(datetime.fromisoformat(t['timestamp'].replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M'))
                    ]) for t in transactions[:10]
                ])
            ], striped=True, bordered=True, hover=True, responsive=True, className="table-dark")
        else:
            table = dbc.Alert([
                html.I(className="fas fa-info-circle me-2"),
                "No transactions available. Run ",
                html.Code("python generate_sample_data.py"),
                " to populate the database."
            ], color="info")

        return total_txn, fraud_count, fraud_rate, amount, risk_pie, risk_bar, table

    except Exception as e:
        print(f"Dashboard update error: {e}")
        return "0", "0", "0%", "$0", go.Figure(), go.Figure(), dbc.Alert("Error loading data", color="danger")

# Prediction callbacks
@app.callback(
    [Output('pred-amount', 'value'),
     Output('pred-state', 'value'),
     Output('pred-city', 'value'),
     Output('pred-mcc', 'value'),
     Output('pred-chip', 'value')],
    [Input('scenario-low', 'n_clicks'),
     Input('scenario-medium', 'n_clicks'),
     Input('scenario-high', 'n_clicks')],
    prevent_initial_call=True
)
def load_scenario(low, medium, high):
    """Load test scenarios"""
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    scenarios = {
        'scenario-low': (45.50, 'CA', 'San Francisco', '5411', 'Chip Transaction'),
        'scenario-medium': (250.00, 'NV', 'Las Vegas', '7995', 'Online Transaction'),
        'scenario-high': (2500.00, 'FL', 'Miami', '5944', 'Online Transaction')
    }

    return scenarios.get(button_id, (None, None, None, None, None))

@app.callback(
    Output('prediction-result', 'children'),
    Input('predict-button', 'n_clicks'),
    [State('pred-amount', 'value'),
     State('pred-state', 'value'),
     State('pred-city', 'value'),
     State('pred-mcc', 'value'),
     State('pred-chip', 'value')],
    prevent_initial_call=True
)
def make_prediction(n, amount, state, city, mcc, chip):
    """Make fraud prediction"""
    if not amount:
        return dbc.Alert("Please enter transaction amount", color="warning")

    try:
        transaction_data = {
            "Amount": float(amount),
            "Merchant State": state or "CA",
            "Merchant City": city or "Unknown",
            "MCC": int(mcc or 5411),
            "Use Chip": chip or "Chip Transaction"
        }

        response = requests.post(f'{API_BASE_URL}/api/predict', json=transaction_data, timeout=5)
        result = response.json()

        fraud_color = "danger" if result['is_fraud'] else "success"
        fraud_icon = "fa-exclamation-circle" if result['is_fraud'] else "fa-check-circle"
        fraud_text = "FRAUD DETECTED" if result['is_fraud'] else "TRANSACTION SAFE"

        return dbc.Card([
            dbc.CardHeader(html.H5([html.I(className="fas fa-chart-pie me-2"), "Prediction Result"])),
            dbc.CardBody([
                dbc.Alert([
                    html.H3([html.I(className=f"fas {fraud_icon} me-2"), fraud_text], className="mb-0")
                ], color=fraud_color, className="text-center"),

                html.Div([
                    html.H5("Fraud Probability", className="mb-2"),
                    dbc.Progress(value=result['fraud_probability'] * 100,
                                label=f"{result['fraud_probability']*100:.2f}%",
                                color=fraud_color, className="mb-3", style={"height": "30px"})
                ]),

                dbc.Table([
                    html.Tbody([
                        html.Tr([html.Td("Transaction ID"), html.Td(html.Code(result['transaction_id']))]),
                        html.Tr([html.Td("Amount"), html.Td(f"${result['amount']:,.2f}")]),
                        html.Tr([html.Td("Risk Level"), html.Td(dbc.Badge(result['risk_level'].upper(), color=fraud_color))]),
                        html.Tr([html.Td("Risk Score"), html.Td(f"{result['risk_score']:.2f}/100")]),
                        html.Tr([html.Td("Processed At"), html.Td(datetime.fromisoformat(result['processed_at'].replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M:%S'))])
                    ])
                ], bordered=True, className="table-dark"),

                dbc.Alert([
                    html.Strong([html.I(className="fas fa-lightbulb me-2"), "Recommendation:"]),
                    html.Br(),
                    result['recommendation']
                ], color="info")
            ])
        ], className="shadow-sm")

    except Exception as e:
        return dbc.Alert(f"Error making prediction: {str(e)}", color="danger")

# Alerts callbacks
@app.callback(
    [Output('critical-count', 'children'),
     Output('high-count', 'children'),
     Output('medium-count', 'children'),
     Output('total-count', 'children'),
     Output('alerts-container', 'children')],
    [Input('alerts-interval', 'n_intervals'),
     Input('refresh-alerts', 'n_clicks'),
     Input('alert-severity-filter', 'value'),
     Input('alert-limit-filter', 'value')]
)
def update_alerts(n, clicks, severity, limit):
    """Update alerts page"""
    try:
        url = f'{API_BASE_URL}/api/dashboard/alerts?limit={limit}'
        if severity:
            url += f'&severity={severity}'

        response = requests.get(url, timeout=5)
        alerts = response.json().get('alerts', [])

        counts = {'critical': 0, 'high': 0, 'medium': 0}
        for alert in alerts:
            if alert['severity'] in counts:
                counts[alert['severity']] += 1

        if alerts:
            alert_cards = []
            for alert in alerts:
                color_map = {'critical': 'danger', 'high': 'warning', 'medium': 'info'}
                icon_map = {'critical': 'fa-exclamation-circle', 'high': 'fa-exclamation-triangle', 'medium': 'fa-info-circle'}

                alert_cards.append(
                    dbc.Card([
                        dbc.CardHeader([
                            html.Div([
                                html.H6([html.I(className=f"fas {icon_map.get(alert['severity'], 'fa-bell')} me-2"), alert['title']], className="mb-0"),
                                dbc.Badge(alert['severity'].upper(), color=color_map.get(alert['severity'], 'secondary'))
                            ], className="d-flex justify-content-between align-items-center")
                        ], className=f"bg-{color_map.get(alert['severity'], 'secondary')} text-white"),
                        dbc.CardBody([
                            html.P([html.Strong("Description: "), alert['description']]),
                            html.P([html.Strong("Transaction ID: "), html.Code(alert['transaction_id'])]),
                            html.P([html.Strong("Amount: "), f"${alert['amount']:,.2f}"]),
                            html.P([html.Strong("Location: "), f"{alert.get('merchant_city', 'N/A')}, {alert.get('merchant_state', 'N/A')}"]),
                            html.P([html.Strong("Timestamp: "), datetime.fromisoformat(alert['timestamp'].replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M')]),
                            dbc.Progress(value=alert['risk_score']*100, label=f"{alert['risk_score']*100:.1f}%",
                                       color=color_map.get(alert['severity'], 'secondary'))
                        ])
                    ], className="mb-3 shadow-sm")
                )

            alert_container = html.Div(alert_cards)
        else:
            alert_container = dbc.Alert([
                html.I(className="fas fa-info-circle me-2"),
                "No alerts found. Run ", html.Code("python generate_sample_data.py"), " to populate the database."
            ], color="info")

        return counts['critical'], counts['high'], counts['medium'], len(alerts), alert_container

    except Exception as e:
        return 0, 0, 0, 0, dbc.Alert(f"Error loading alerts: {str(e)}", color="danger")

# Monitoring callbacks
@app.callback(
    [Output('monitor-txn-count', 'children'),
     Output('monitor-fraud-rate', 'children'),
     Output('monitor-avg-risk', 'children'),
     Output('timeline-chart', 'figure'),
     Output('transaction-stream', 'children')],
    [Input('monitoring-interval', 'n_intervals'),
     Input('refresh-monitoring', 'n_clicks')]
)
def update_monitoring(n, clicks):
    """Update monitoring page"""
    try:
        response = requests.get(f'{API_BASE_URL}/api/dashboard/recent-transactions?limit=100', timeout=5)
        transactions = response.json().get('transactions', [])

        txn_count = len(transactions)
        fraud_count = sum(1 for t in transactions if t['is_fraud'])
        fraud_rate = f"{(fraud_count/txn_count*100):.2f}%" if txn_count > 0 else "0%"
        avg_risk = f"{(sum(t['risk_score'] for t in transactions)/txn_count*100):.2f}%" if txn_count > 0 else "0%"

        # Timeline chart
        if transactions:
            df = pd.DataFrame(transactions)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp')

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df[~df['is_fraud']]['timestamp'],
                y=df[~df['is_fraud']]['risk_score'] * 100,
                mode='markers',
                name='Legitimate',
                marker=dict(color='#28a745', size=8)
            ))
            fig.add_trace(go.Scatter(
                x=df[df['is_fraud']]['timestamp'],
                y=df[df['is_fraud']]['risk_score'] * 100,
                mode='markers',
                name='Fraud',
                marker=dict(color='#dc3545', size=10, symbol='x')
            ))
            fig.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="High Risk Threshold")
            fig.update_layout(
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis_title="Timestamp",
                yaxis_title="Risk Score (%)",
                height=400,
                hovermode='closest'
            )
        else:
            fig = go.Figure()
            fig.add_annotation(text="No data available", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)

        # Transaction stream
        if transactions:
            stream_table = dbc.Table([
                html.Thead(html.Tr([
                    html.Th("Time"), html.Th("Transaction ID"), html.Th("Amount"),
                    html.Th("Location"), html.Th("Risk Score"), html.Th("Status")
                ])),
                html.Tbody([
                    html.Tr([
                        html.Td(datetime.fromisoformat(t['timestamp'].replace('Z', '+00:00')).strftime('%H:%M:%S')),
                        html.Td(html.Code(t['transaction_id'][:15] + "...")),
                        html.Td(f"${t['amount']:,.2f}"),
                        html.Td(f"{t.get('merchant_city', 'N/A')}, {t.get('merchant_state', 'N/A')}"),
                        html.Td(dbc.Badge(f"{t['risk_score']*100:.1f}%",
                                         color="danger" if t['risk_score'] >= 0.7 else "warning" if t['risk_score'] >= 0.5 else "success")),
                        html.Td(dbc.Badge("FRAUD" if t['is_fraud'] else "SAFE",
                                         color="danger" if t['is_fraud'] else "success"))
                    ]) for t in transactions[:20]
                ])
            ], striped=True, bordered=True, hover=True, responsive=True, className="table-dark")
        else:
            stream_table = dbc.Alert("No transactions available", color="info")

        return txn_count, fraud_rate, avg_risk, fig, stream_table

    except Exception as e:
        return "0", "0%", "0%", go.Figure(), dbc.Alert(f"Error: {str(e)}", color="danger")

# Reports callbacks
@app.callback(
    [Output('merchant-chart', 'figure'),
     Output('merchant-table', 'children')],
    [Input('refresh-reports', 'n_clicks')]
)
def update_reports(clicks):
    """Update reports page"""
    try:
        response = requests.get(f'{API_BASE_URL}/api/dashboard/merchant-stats', timeout=5)
        stats = response.json().get('merchant_stats', [])

        if stats:
            df = pd.DataFrame(stats[:10])  # Top 10

            fig = px.bar(
                df,
                x='fraud_count',
                y=[f"{row['merchant_city']}, {row['merchant_state']}" for _, row in df.iterrows()],
                orientation='h',
                color='fraud_count',
                color_continuous_scale='Reds',
                labels={'x': 'Fraud Count', 'y': 'Location'}
            )
            fig.update_layout(
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                height=400,
                title="Top 10 Locations by Fraud Count",
                showlegend=False
            )

            table = dbc.Table([
                html.Thead(html.Tr([
                    html.Th("Location"), html.Th("Total Txns"), html.Th("Fraud Count"),
                    html.Th("Fraud Rate"), html.Th("Total Amount"), html.Th("Avg Fraud Prob")
                ])),
                html.Tbody([
                    html.Tr([
                        html.Td(html.Strong(f"{s['merchant_city']}, {s['merchant_state']}")),
                        html.Td(f"{s['transaction_count']:,}"),
                        html.Td(dbc.Badge(s['fraud_count'], color="danger")),
                        html.Td(dbc.Badge(f"{(s['fraud_count']/s['transaction_count']*100):.2f}%",
                                         color="danger" if s['fraud_count']/s['transaction_count'] > 0.1 else "warning" if s['fraud_count']/s['transaction_count'] > 0.05 else "success")),
                        html.Td(f"${s['total_amount']:,.0f}"),
                        html.Td(f"{(s.get('avg_fraud_prob', 0)*100):.2f}%")
                    ]) for s in stats
                ])
            ], striped=True, bordered=True, hover=True, responsive=True, className="table-dark")
        else:
            fig = go.Figure()
            fig.add_annotation(text="No data available. Run generate_sample_data.py", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
            table = dbc.Alert("No merchant data available", color="info")

        return fig, table

    except Exception as e:
        return go.Figure(), dbc.Alert(f"Error: {str(e)}", color="danger")

if __name__ == '__main__':
    print("=" * 80)
    print("FraudGuard - Plotly Dash Dashboard")
    print("=" * 80)
    print("Dashboard URL: http://localhost:8050")
    print("API Backend: http://localhost:5000")
    print("=" * 80)
    app.run(debug=True, host='0.0.0.0', port=8050)
