"""
Timeline simplificado y robusto para la visualización del cerebro 3D.
Utiliza extendData para mejor rendimiento y evita problemas de redibujado.
"""

import plotly.graph_objects as go
from dash import dcc, html
import dash_bootstrap_components as dbc

def create_simple_timeline():
    """
    Crear un timeline simple y funcional con enfoque incremental.
    
    Retorna:
    - dash.html.Div: Componente completo de timeline
    """
    
    # Figura inicial del timeline con configuración correcta
    fig = go.Figure()
    
    # Agregar trazas vacías con configuración específica
    fig.add_trace(go.Scatter(
        x=[], y=[], 
        mode='lines+markers',
        name='Attention',
        line=dict(color='orange', width=3),
        marker=dict(size=6),
        hovertemplate='<b>Attention</b><br>Tiempo: %{x:.1f}s<br>Valor: %{y:.1f}%<extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=[], y=[], 
        mode='lines+markers',
        name='Meditation', 
        line=dict(color='green', width=3),
        marker=dict(size=6),
        hovertemplate='<b>Meditation</b><br>Tiempo: %{x:.1f}s<br>Valor: %{y:.1f}%<extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=[], y=[], 
        mode='lines+markers',
        name='Signal Strength',
        line=dict(color='blue', width=3),
        marker=dict(size=6),
        hovertemplate='<b>Signal Strength</b><br>Tiempo: %{x:.1f}s<br>Valor: %{y:.1f}%<extra></extra>'
    ))
    
    # Configuración del layout
    fig.update_layout(
        title={
            'text': "📊 Timeline de Activación Neural - Sesión Actual",
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis={
            'title': 'Tiempo (segundos)',
            'showgrid': True,
            'gridcolor': 'lightgray',
            'autorange': True
        },
        yaxis={
            'title': 'Activación (%)',
            'range': [0, 100],
            'showgrid': True,
            'gridcolor': 'lightgray'
        },
        height=350,
        margin=dict(l=60, r=40, t=80, b=60),
        plot_bgcolor='white',
        paper_bgcolor='#f8f9fa',
        hovermode='x unified',
        showlegend=True,
        legend=dict(
            orientation="h", 
            yanchor="bottom", 
            y=1.02, 
            xanchor="right", 
            x=1
        )
    )
    
    # Controles mejorados
    controls = dbc.Row([
        dbc.Col([
            dbc.ButtonGroup([
                dbc.Button(
                    "⏸️ Pausar", 
                    id="simple_timeline_pause_btn", 
                    color="warning",
                    size="sm"
                ),
                dbc.Button(
                    "▶️ Reanudar", 
                    id="simple_timeline_resume_btn", 
                    color="success",
                    size="sm"
                ),
                # dbc.Button(
                #     "🔄 Resetear", 
                #     id="simple_timeline_reset_btn", 
                #     color="secondary",
                #     size="sm"
                # )
            ], className="me-2"),
            dbc.Badge(
                "🔴 EN VIVO", 
                id="simple_timeline_status_badge",
                color="success",
                className="fs-6"
            )
        ], width=8),
        dbc.Col([
            html.Small(
                "💡 Haz click en cualquier punto para navegar en el tiempo",
                className="text-muted fst-italic"
            )
        ], width=4, className="d-flex align-items-center justify-content-end")
    ], className="mb-3")
    
    # Componente completo
    timeline_component = html.Div([
        # Stores para datos
        dcc.Store(id='simple_session_data', data={
            'timestamps': [],
            'attention': [],
            'meditation': [],
            'signal_strength': [],
            'full_history': [],
            'session_start': None,
            'max_points': 120  # 2 minutos de datos
        }),
        dcc.Store(id='simple_timeline_mode', data={
            'mode': 'live',  # 'live', 'paused', 'historical'
            'selected_time': None,
            'selected_data': None
        }),
        
        controls,
        
        dcc.Graph(
            figure=fig,
            id='simple_timeline_graph',
            config={
                'displayModeBar': False,
                'doubleClick': False,
                'scrollZoom': False,
                'showTips': True
            },
            style={'border': '1px solid #dee2e6', 'border-radius': '8px'}
        )
    ], style={
        'padding': '15px',
        'background-color': '#f8f9fa',
        'border-radius': '10px',
        'margin-bottom': '15px',
        'box-shadow': '0 2px 8px rgba(0,0,0,0.1)'
    })
    
    return timeline_component

def get_timeline_extend_data(new_time, attention, meditation, signal):
    """
    Crear datos para extender el timeline usando extendData.
    
    Args:
        new_time (float): Nuevo timestamp
        attention (float): Valor de atención
        meditation (float): Valor de meditación
        signal (float): Intensidad de señal
    
    Returns:
        dict: Datos formatados para extendData
    """
    return {
        'x': [[new_time], [new_time], [new_time]],
        'y': [[attention], [meditation], [signal]]
    }