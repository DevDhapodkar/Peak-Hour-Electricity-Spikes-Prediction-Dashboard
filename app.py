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

# Initialize app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

def create_layout():
    df, predictions = get_processed_data()
    dorms = df['dorm'].unique()
    
    return dbc.Container([
        dbc.Row([
            dbc.Col(html.H1("Peak Hour Electricity Dashboard", className="text-center my-4 text-primary"), width=12)
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H4("Predicted Evening Peaks (kWh)")),
                    dbc.CardBody([
                        html.Div([
                            html.Div([
                                html.Span(f"{dorm}: ", className="fw-bold"),
                                html.Span(f"{predictions[dorm]:.2f}", className="text-info h4")
                            ], className="mb-2") for dorm in dorms
                        ])
                    ])
                ], color="secondary", outline=True)
            ], width=4),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H4("Dorm Selection")),
                    dbc.CardBody([
                        dcc.Dropdown(
                            id='dorm-dropdown',
                            options=[{'label': d, 'value': d} for d in dorms],
                            value=dorms[0],
                            clearable=False,
                            className="bg-dark text-white"
                        )
                    ])
                ], color="secondary", outline=True)
            ], width=8)
        ], className="mb-4"),
        
        dbc.Row([
            dbc.Col([
                dcc.Loading(dcc.Graph(id='main-graph'))
            ], width=12)
        ]),
        
        dbc.Row([
            dbc.Col([
                html.P("This dashboard displays hourly meter data, smoothed trends using a 3-hour moving average, and predicts future peaks via linear regression.", className="text-muted mt-4")
            ])
        ])
    ], fluid=True)

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
        line=dict(color='rgba(100, 100, 100, 0.4)', width=1),
        mode='lines'
    ))
    
    # Smoothed Data
    fig.add_trace(go.Scatter(
        x=dorm_df['timestamp'],
        y=dorm_df['smoothed_usage'],
        name='Smoothed (Moving Avg)',
        line=dict(color='#00bc8c', width=3),
        mode='lines'
    ))
    
    fig.update_layout(
        title=f"Electricity Consumption for {selected_dorm} (Past 7 Days)",
        xaxis_title="Time",
        yaxis_title="Usage (kWh)",
        template='plotly_dark',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode='x unified'
    )
    
    return fig

if __name__ == '__main__':
    app.run(debug=True, port=8050)
