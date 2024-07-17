from src.py.utils.utils import Utils
from src.py.database.database import Database
import src.py.components.styles as styles

from dash import Dash, dcc, html, Input, Output, callback, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

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

line_figure = go.Figure(
    data=go.Scatter(
    )
)

line_graph = html.Div([
    dcc.Graph(figure = line_figure, id='line_graph')
])

bar_graph = html.Div([
    dcc.Graph(id='bar_graph')
])

heat_graph = html.Div([
    dcc.Graph(id='heat_graph')
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