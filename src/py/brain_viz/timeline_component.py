"""
Componente de línea de tiempo para la visualización del cerebro 3D.
Permite navegar por el historial de datos de la sesión actual.
"""

import plotly.graph_objects as go
import numpy as np
from dash import dcc, html
import dash_bootstrap_components as dbc

def create_timeline_component():
    """
    Crear el componente de línea de tiempo para navegación temporal.
    
    Retorna:
    - dash.html.Div: Componente completo de timeline
    """
    
    # Figura inicial del timeline (vacía)
    initial_timeline = go.Figure()
    initial_timeline.add_trace(go.Scatter(
        x=[], y=[], mode='lines+markers',
        name='Signal Strength', line=dict(color='#1f77b4', width=2)
    ))
    initial_timeline.add_trace(go.Scatter(
        x=[], y=[], mode='lines+markers', 
        name='Attention', line=dict(color='#ff7f0e', width=2)
    ))
    initial_timeline.add_trace(go.Scatter(
        x=[], y=[], mode='lines+markers',
        name='Meditation', line=dict(color='#2ca02c', width=2)
    ))
    
    initial_timeline.update_layout(
        title="Timeline de Activación - Sesión Actual",
        xaxis_title="Tiempo (segundos)",
        yaxis_title="Activación (%)",
        height=300,
        margin=dict(l=50, r=50, t=50, b=50),
        hovermode='x unified',
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor='rgba(240,240,240,0.8)',
        paper_bgcolor='white',
        yaxis=dict(range=[0, 100]),
        xaxis=dict(type='linear', range=[0, 10])  # Rango inicial para tiempo
    )
    
    # Área de controles
    controls = dbc.Row([
        dbc.Col([
            dbc.ButtonGroup([
                dbc.Button(
                    "⏸️ Pausar", 
                    id="timeline_pause_btn", 
                    color="warning",
                    size="sm",
                    disabled=True
                ),
                dbc.Button(
                    "▶️ Reanudar", 
                    id="timeline_resume_btn", 
                    color="success",
                    size="sm",
                    disabled=True
                ),
                dbc.Button(
                    "🔄 Resetear", 
                    id="timeline_reset_btn", 
                    color="secondary",
                    size="sm"
                )
            ])
        ], width=6),
        dbc.Col([
            html.Small(
                "📍 Click en cualquier punto del timeline para ver esos datos",
                className="text-muted",
                style={'fontSize': '0.8em'}
            )
        ], width=6, className="d-flex align-items-center justify-content-end")
    ], className="mb-2")
    
    # Estado actual
    status_indicator = dbc.Alert(
        [
            html.Strong("🔴 TIEMPO REAL"), 
            " - Actualizaciones automáticas activas"
        ],
        color="success",
        id="timeline_status",
        className="py-2 mb-2"
    )
    
    timeline_component = html.Div([
        # Store para el historial completo de la sesión
        dcc.Store(id='session_history_store', data={'timestamps': [], 'data_points': []}),
        # Store para el estado del timeline (paused/live/historical)
        dcc.Store(id='timeline_state_store', data={
            'mode': 'live',  # 'live', 'paused', 'historical'
            'selected_time': None,
            'session_start': None
        }),
        
        controls,
        status_indicator,
        
        dcc.Graph(
            figure=initial_timeline,
            id='timeline_graph',
            config={
                'displayModeBar': False,
                'doubleClick': False,
                'scrollZoom': False,
                'showTips': True,
                'staticPlot': False
            },
            style={'height': '300px', 'width': '100%'}
        )
    ], style={
        'padding': '15px',
        'background-color': '#f8f9fa',
        'border-radius': '8px',
        'border': '1px solid #dee2e6',
        'margin-bottom': '10px'
    })
    
    return timeline_component

def create_timeline_data_trace(timestamps, values, name, color):
    """
    Crear una traza para el timeline con los datos especificados.
    
    Args:
        timestamps (list): Lista de timestamps
        values (list): Lista de valores correspondientes
        name (str): Nombre de la traza
        color (str): Color de la línea
    
    Returns:
        plotly.graph_objects.Scatter: Traza configurada
    """
    return go.Scatter(
        x=timestamps,
        y=values,
        mode='lines+markers',
        name=name,
        line=dict(color=color, width=2),
        marker=dict(size=4),
        hovertemplate=f'<b>{name}</b><br>' +
                     'Tiempo: %{x:.1f}s<br>' +
                     'Valor: %{y:.1f}%<br>' +
                     '<extra></extra>'
    )