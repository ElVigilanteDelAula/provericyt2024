from src.py.utils.utils import Utils
from src.py.database.database import Database
import src.py.components.styles as styles
import numpy as np

from dash import Dash, dcc, html, Input, Output, callback, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

def scatter_factory(params, mode, colors=[]):
    tmp = []
    for param in params:
        tmp.append(
            go.Scatter(
                x=[],
                y=[],
                mode=mode,
                name=param,
            )
        )
    return tmp

def bar_factory(params, mode, colors=[]):
    tmp = []
    for param in params:
        tmp.append(
            go.Bar(
                x=[],
                y=[],
                name=param,
            )
        )
    return tmp

def heat_factory(sensors):
    tmp = []
    for i in np.arange(0,(len(sensors)*2)-1,2):
        tmp.append(
            go.Heatmap(
                z=[[0]],
                y=[],
                x=[i],
                colorscale="reds",
                zmax=1,
                zmin=0,
                showscale=False
            )
        )
        tmp.append(
            go.Heatmap(
                z=[[0]],
                y=[],
                x=[i+1],
                colorscale="greens",
                zmax=1,
                zmin=0,
                showscale=False
            )
        )
    return tmp

sidebar = dbc.Stack([
    html.H1("EEG"),
    html.H5("session", id='main_title'),
    html.Hr(),
    dbc.Select(
        ["individual", "todos"],
        "individual",
        id='quantity_select'
    ),
    dbc.Select(
        list(Utils.SENSORS.keys()),
        list(Utils.SENSORS.keys())[0],
        id='sensor_select'
    ),
    dbc.Checklist(
        Utils.SENSOR_PARAMS,
        ['signal_strength', 'attention', 'meditation'],
        switch=True,
        id='data_checklist'
    ),
    dbc.Textarea(
        placeholder='notas',
        valid=False,
        id='notes'
    ),
    dbc.Button(
        'Registrar',
        color='secondary',
        id='submit'
    )
], style=styles.SIDEBAR_STYLE)

line_layout = go.Layout(
    yaxis={
        "range":(0,1)
    }
)

line_figure = go.Figure(
    data=scatter_factory(Utils.SENSOR_PARAMS,"lines"),
    layout=line_layout
)


line_graph = html.Div([
    dcc.Graph(figure = line_figure, id='line_graph' )
])

bar_layout = go.Layout(
    yaxis={
        "range":(0,1)
    }
)

bar_figure = go.Figure(
    data=bar_factory(Utils.SENSOR_PARAMS, "markers"),
    layout=bar_layout
)

bar_graph = html.Div([
    dcc.Graph(figure=bar_figure,id='bar_graph')
])


heat_layout = {
    "xaxis":{
        "tickmode":"array",
        "tickvals":np.arange(0, len(Utils.SENSORS.keys())*2,2),
        "ticktext":list(Utils.SENSORS.keys())
    }
}

heat_figure = go.Figure(
    data=heat_factory(Utils.SENSORS),
    layout=heat_layout
)

heat_graph = html.Div([
    dcc.Graph(figure=heat_figure, id='heat_graph')
])

graphs_ind = dbc.Tabs([
        dbc.Tab([line_graph], label="lines"),
        dbc.Tab([bar_graph], label="bars")
    ], active_tab='lines')

graphs_all = dbc.Tabs([
        dbc.Tab([heat_graph], label="heatmap")
    ],active_tab='heatmap')

app_layout=html.Div([
    dcc.Store(id='memory'),
    dcc.Interval(
        id="timer",
        n_intervals=0,
        interval=1000
    ),
    sidebar,
    html.Div([
        html.H3("sensor", id='sensor_name'),
        html.Div([], id='graph_box')
    ], style=styles.MAIN_STYLE)
],id='all', style={"display":"flex"})