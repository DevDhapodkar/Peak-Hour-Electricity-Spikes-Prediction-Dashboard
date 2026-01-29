import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
from data_generator import main as generate_data
from processor import get_processed_data
import os

# Ensure data exists
if not os.path.exists('electricity_data.csv'):
    generate_data()

# Start of replacement
# Initialize app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

def create_layout():
    df, predictions = get_processed_data()
    dorms = df['dorm'].unique()
    
    return dbc.Container([
        dbc.Row([
            dbc.Col(html.H1("Peak Hour Electricity Dashboard", className="skeuo-title text-center my-4"), width=12)
        ]),
        
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H4("Predicted Evening Peaks (kWh)", className="mb-3 fw-bold"),
                    html.Div([
                        html.Div([
                            html.Span(f"{dorm}: ", className="fw-bold"),
                            html.Span(f"{predictions[dorm]:.2f}", className="skeuo-stat-value")
                        ], className="mb-2 d-flex justify-content-between align-items-center") for dorm in dorms
                    ])
                ], className="skeuo-card")
            ], width=4),
            
            dbc.Col([
                html.Div([
                    html.H4("Dorm Selection", className="mb-3 fw-bold"),
                    dcc.Dropdown(
                        id='dorm-dropdown',
                        options=[{'label': d, 'value': d} for d in dorms],
                        value=dorms[0],
                        clearable=False,
                        className="skeuo-dropdown"
                    )
                ], className="skeuo-card")
            ], width=8)
        ], className="mb-4"),
        
        dbc.Row([
            dbc.Col([
                html.Div([
                    dcc.Loading(dcc.Graph(id='main-graph', config={'displayModeBar': False}))
                ], className="skeuo-graph-container skeuo-card")
            ], width=12)
        ]),
        
        dbc.Row([
            dbc.Col([
                html.P("This dashboard displays hourly meter data, smoothed trends using a 3-hour moving average, and predicts future peaks via linear regression.", className="text-skeuo-muted text-center mt-4")
            ])
        ])
    ], fluid=True, className="skeuo-container")

app.layout = create_layout

@app.callback(
    Output('main-graph', 'figure'),
    Input('dorm-dropdown', 'value')
)
def update_graph(selected_dorm):
    df, _ = get_processed_data()
    dorm_df = df[df['dorm'] == selected_dorm].tail(168) # Last 7 days
    
    fig = go.Figure()
    
    # Raw Data
    fig.add_trace(go.Scatter(
        x=dorm_df['timestamp'],
        y=dorm_df['usage_kwh'],
        name='Raw Data',
        line=dict(color='rgba(100, 100, 100, 0.2)', width=1),
        mode='lines'
    ))
    
    # Smoothed Data
    fig.add_trace(go.Scatter(
        x=dorm_df['timestamp'],
        y=dorm_df['smoothed_usage'],
        name='Smoothed (Moving Avg)',
        line=dict(color='#00bc8c', width=4),
        mode='lines'
    ))
    
    fig.update_layout(
        title=dict(
            text=f"Electricity Consumption for {selected_dorm} (Past 7 Days)",
            font=dict(color='#44476a', size=20)
        ),
        xaxis=dict(
            title="Time",
            gridcolor='rgba(163, 177, 198, 0.3)',
            tickfont=dict(color='#7a829c')
        ),
        yaxis=dict(
            title="Usage (kWh)",
            gridcolor='rgba(163, 177, 198, 0.3)',
            tickfont=dict(color='#7a829c')
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#44476a'),
        legend=dict(
            orientation="h", 
            yanchor="bottom", 
            y=1.02, 
            xanchor="right", 
            x=1,
            font=dict(color='#44476a')
        ),
        hovermode='x unified',
        margin=dict(l=40, r=40, t=80, b=40)
    )
    
    return fig

if __name__ == '__main__':
    app.run(debug=True, port=8050)
