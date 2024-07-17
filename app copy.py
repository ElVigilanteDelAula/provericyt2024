from src.py.utils.utils import Utils
from src.py.database.database import Database
import numpy as np
import src.py.components.components as components
from datetime import datetime

from dash import Dash, dcc, html, Input, Output, callback, State
import dash_bootstrap_components as dbc

uid = datetime.now().strftime('%Y%m%d%H%M%S')
header = Database.get_header(Utils.SENSORS.values(), Utils.SENSOR_PARAMS)

app = Dash(external_stylesheets=[dbc.themes.MATERIA])

app.layout= components.app_layout

def sim():
    return np.random.random_sample((11))

@callback(
    Output('graph_box', 'children'),
    Output('sensor_name', "children"),
    Input('quantity_select','value'),
    Input('sensor_select','value')
)
def select_quantity(qty, sensor):
    if qty == 'individual':
        return [components.graphs_ind], sensor
    elif qty == 'todos':
        return [components.graphs_all], "Todos los sensores"
    
@callback(
    Output('main_title', "children"),
    Output("memory", "data"),
    Input('all', "children")
)
def on_startup(children):
    return f"session_{uid}", {"uid":uid}

if __name__ =="__main__":
    app.run(debug=True)
    
