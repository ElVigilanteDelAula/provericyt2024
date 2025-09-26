from dash import dcc, html
import plotly.graph_objects as go
from src.py.brain_viz.brain_visualizer import brain_viz

def create_brain_component():
    """
    Crear el componente de visualización del cerebro para el dashboard.
    
    Retorna:
    - dash.html.Div: Componente de visualización del cerebro
    """
    
    # Crear figura inicial del cerebro
    initial_figure = brain_viz.create_brain_figure()
    
    brain_graph = html.Div([
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
                ]
            }
        )
    ], style={
        'padding': '10px',
        'background-color': 'white',
        'border-radius': '5px',
        'box-shadow': '0 2px 4px rgba(0,0,0,0.1)'
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