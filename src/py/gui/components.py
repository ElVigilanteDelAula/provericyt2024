from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc
import src.py.gui.styles as styles
from src.py.database.database import Database
import plotly.graph_objects as go
from src.py.utils.utils import Utils
import numpy as np
from plotly.subplots import make_subplots

db = Database("test.db")
session_list = db.list_sessions()

sidebar = dbc.Stack([
    html.H1("EEG"),
    dbc.Button(
        "Refresh",
        id="refreshed_button",
        color="transparent"
    ),
    html.Hr(),
    dash_table.DataTable(
        data=session_list.to_dict("records"),
        columns=[{"name": i, "id": i} for i in session_list.loc[:,["date","notes"]].columns],
        row_selectable="single",
        filter_action="native",
        sort_action="native",
        style_data={
            'whiteSpace': 'normal',
            'height': 'auto',
            'backgroundColor': 'var(--bs-gray-300)',
            'color': 'var(--bs-btn-color)'
        },
        style_cell={
            'textOverflow': 'ellipsis',
            'maxWidth': "8vw",
            'minWidth': "5vw"
        },
        style_header={
            'backgroundColor': 'var(--bs-gray-400)',
            'color': 'var(--bs-btn-color)'
        },
        style_filter={
            'backgroundColor': 'var(--bs-gray-400)',
            'color': 'var(--bs-btn-color)'
        },
        page_size=6,
        style_as_list_view=True,
        id="data_table"
    ),
     dbc.Button("Open Offcanvas", id="open-offcanvas", color="transparent"),
], style=styles.SIDEBAR_STYLE, gap=1)

offcanvas = dbc.Offcanvas([
    dbc.Checklist(
        list(Utils.SENSORS.keys()),
        list(Utils.SENSORS.keys()),
        id='sensor_select',
        switch=True
    ),
    html.Hr(),
    dbc.Checklist(
                Utils.SENSOR_PARAMS,
                ['signal_strength', 'attention', 'meditation'],
                switch=True,
                id='data_checklist'
            )
], id="offcanvas")

spec_figure = go.Figure()

spec_graph = html.Div([
    dcc.Graph(
        figure=spec_figure,
        id="spec_graph",
        style=styles.GRAPH_STYLE
    )
])

line_figure = go.Figure()

line_graph = html.Div([
    dcc.Graph(
        figure = line_figure, 
        id='line_graph',
        style=styles.GRAPH_STYLE
    )
])

graphs = dbc.Tabs([
        dbc.Tab([line_graph], label="lines"),
        dbc.Tab([spec_graph], label="spectrogram")
    ],active_tab="tab-0")

main_view = html.Div([
    html.H3("session", id="session_title"),
    html.P("notes", id="session_notes"),
    html.Hr(),
    graphs
],style=styles.MAIN_STYLE)

app_layout = html.Div([
    sidebar,
    offcanvas,
    main_view
], className="dbc dbc-row-selectable", style={"display":"flex"})