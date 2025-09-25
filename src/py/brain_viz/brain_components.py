"""
Brain visualization components for the live EEG dashboard.
"""

from dash import dcc, html
import plotly.graph_objects as go
from src.py.brain_viz.brain_visualizer import brain_viz

def create_brain_component():
    """
    Create the brain visualization component for the dashboard.
    
    Returns:
    - dash.html.Div: Brain visualization component
    """
    
    # Create initial brain figure
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
    Get the brain visualization tab for the dashboard tabs.
    
    Returns:
    - dash_bootstrap_components.Tab: Brain tab component
    """
    import dash_bootstrap_components as dbc
    
    return dbc.Tab([create_brain_component()], label="Cerebro 3D", tab_id="brain-tab")