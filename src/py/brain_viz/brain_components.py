from dash import dcc, html
import plotly.graph_objects as go
from src.py.brain_viz.brain_visualizer import brain_viz
from src.py.brain_viz.simple_timeline import create_simple_timeline

def create_brain_component():
    """
    Crear el componente de visualización del cerebro para el dashboard.
    
    Retorna:
    - dash.html.Div: Componente de visualización del cerebro con timeline
    """
    
    # Crear figura inicial del cerebro
    initial_figure = brain_viz.create_brain_figure()
    
    # Crear el timeline component simplificado
    timeline_component = create_simple_timeline()
    
    brain_graph = html.Div([
        # Store para mantener el estado de la cámara
        dcc.Store(id='brain_camera_store', data={}),
        # Store para controlar si se debe pausar las actualizaciones durante interacción
        dcc.Store(id='brain_interaction_store', data={'is_interacting': False, 'last_interaction': 0}),
        # Timer para detectar cuando termina la interacción
        dcc.Interval(id='interaction_timer', interval=200, n_intervals=0),
        
        # Timeline component (parte superior)
        timeline_component,
        
        # Visualización 3D del cerebro
        html.Div([
            dcc.Graph(
                figure=initial_figure,
                id='brain_graph',
                style={
                    'height': '600px',
                    'width': '100%'
                },
                config={
                    'displayModeBar': True,
                    'displaylogo': False,
                    'modeBarButtonsToRemove': [
                        'pan2d', 'lasso2d', 'select2d', 'autoScale2d',
                        'hoverClosestCartesian', 'hoverCompareCartesian'
                    ],
                    # Configuración mejorada para interacción 3D
                    'scrollZoom': True,
                    'doubleClick': 'reset'
                }
            )
        ], style={
            'padding': '10px',
            'background-color': 'white',
            'border-radius': '5px',
            'box-shadow': '0 2px 4px rgba(0,0,0,0.1)'
        })
    ], style={
        'padding': '10px'
    })
    
    return brain_graph

def get_brain_tab():
    """
    Obtener la pestaña de visualización del cerebro para las pestañas del dashboard.
    
    Retorna:
    - dash_bootstrap_components.Tab: Componente de pestaña del cerebro
    """
    import dash_bootstrap_components as dbc
    
    return dbc.Tab([create_brain_component()], label="Cerebro 3D", tab_id="brain-tab")