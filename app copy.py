from src.py.utils.utils import Utils
from src.py.database.database import Database
import numpy as np
from datetime import datetime


from dash import Dash, dcc, html, Input, Output, callback, State
import dash_bootstrap_components as dbc

sensors = Utils.SENSORS
params = Utils.SENSOR_PARAMS

uid = datetime.now().strftime('%Y%m%d%H%M%S')
header = Database.get_header(sensors.values(), params)

app = Dash(external_stylesheets=[dbc.themes.MATERIA])

sidebar_style = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "20vw",
    "padding": "2vw 2vw",
    "background-color":"var(--bs-gray-300)"
}

MAIN_STYLE = {

}

sidebar = dbc.Stack([
    html.H2("sidebar"),
    html.Hr(),
    dbc.Select(
        ["individual", "todos"],
        "individual"
    ),
    dbc.Select(
        ["individual", "todos"],
        "individual"
    ),
    dbc.Checklist(
        ['uwu'],
        switch=True
    ),
    dbc.Textarea(
        placeholder='notas',
        valid=False
    ),
    dbc.Button(
        'uwu',
        color='secondary'
    )
], style=sidebar_style)

graphs = dbc.Stack([
    html.Div([], style={'backgroundColor':'red'})
])

app.layout=dbc.Container(
    dbc.Row([
        dbc.Col(html.Div(
            sidebar
        ), width=4),
        dbc.Col(html.Div(
            graphs
        ), width=8),
    ])
)

if __name__ =="__main__":
    app.run(debug=True)
    
