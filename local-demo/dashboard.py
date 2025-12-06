"""
Simple local dashboard using Dash (like QuickSight)
"""

import dash
from dash import dcc, html
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sqlite3
import os

DB_PATH = "data/analytics.db"
app = dash.Dash(__name__)

def load_data():
    """Load data from SQLite"""
    if not os.path.exists(DB_PATH):
        return None
    
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM transactions", conn)
    conn.close()
    return df

def create_dashboard():
    """Create dashboard layout"""
    df = load_data()
    
    if df is None:
        return html.Div([
            html.H1("Dashboard Error"),
            html.P("Database not found. Please run 'python etl_process.py' first.")
        ])
    
    # Calculate KPIs
    total_revenue = df['total_amount'].sum()
    total_transactions = len(df)
    avg_transaction = df['total_amount'].mean()
    unique_customers = df['customer_id'].nunique()
    
    # Revenue by Category
    category_revenue = df.groupby('category')['total_amount'].sum().reset_index()
    fig_category = px.bar(category_revenue, x='category', y='total_amount',
                          title='Revenue by Category', labels={'total_amount': 'Revenue ($)'})
    
    # Transactions by Hour
    hourly_transactions = df.groupby('hour').size().reset_index(name='count')
    fig_hour = px.line(hourly_transactions, x='hour', y='count',
                       title='Transaction Volume by Hour')
    
    # Payment Methods
    payment_data = df.groupby('payment_method')['total_amount'].sum().reset_index()
    fig_payment = px.pie(payment_data, values='total_amount', names='payment_method',
                         title='Revenue by Payment Method')
    
    # Revenue by Region
    region_revenue = df.groupby('region')['total_amount'].sum().reset_index()
    fig_region = px.bar(region_revenue, x='region', y='total_amount',
                       title='Revenue by Region', labels={'total_amount': 'Revenue ($)'})
    
    return html.Div([
        html.H1("E-Commerce Analytics Dashboard", style={'textAlign': 'center'}),
        
        # KPI Cards
        html.Div([
            html.Div([
                html.H3("Total Revenue"),
                html.H2(f"${total_revenue:,.2f}")
            ], className='kpi-card'),
            html.Div([
                html.H3("Total Transactions"),
                html.H2(f"{total_transactions:,}")
            ], className='kpi-card'),
            html.Div([
                html.H3("Avg Transaction"),
                html.H2(f"${avg_transaction:.2f}")
            ], className='kpi-card'),
            html.Div([
                html.H3("Unique Customers"),
                html.H2(f"{unique_customers:,}")
            ], className='kpi-card'),
        ], style={'display': 'flex', 'justifyContent': 'space-around', 'margin': '20px'}),
        
        # Charts
        html.Div([
            dcc.Graph(figure=fig_category),
            dcc.Graph(figure=fig_hour),
        ], style={'display': 'flex', 'flexDirection': 'column'}),
        
        html.Div([
            dcc.Graph(figure=fig_payment),
            dcc.Graph(figure=fig_region),
        ], style={'display': 'flex'}),
        
    ], style={'padding': '20px'})

app.layout = create_dashboard()

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8050))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    print("=" * 60)
    print("Starting E-Commerce Analytics Dashboard...")
    print("=" * 60)
    print(f"Server running on port: {port}")
    print(f"Debug mode: {debug}")
    print("=" * 60)
    app.run(debug=debug, port=port, host='0.0.0.0')

