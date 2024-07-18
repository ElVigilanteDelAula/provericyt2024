from src.py.utils.utils import Utils
from src.py.database.database import Database
import numpy as np
import src.py.components.components as components
from datetime import datetime

from dash import Dash, Input, Output, callback, State, no_update
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

@callback(
    Output("memory", "data",  allow_duplicate=True),
    State("memory", "data"),
    Input('timer', "n_intervals"),
    prevent_initial_call=True
)
def store_data(data, intervals):
    tmp = {
        "uid":data['uid'],
    }

    for sensor in Utils.SENSORS.keys():
        tmp.update({sensor:{}})
        for key, value in Utils.SENSOR_PARAMS_MAP.items():
            tmp[sensor].update({key:sim()[value]})

    return tmp

@callback(
    Output("line_graph", "extendData"),
    State('sensor_select','value'),
    State('data_checklist','value'),
    State('timer', "n_intervals"),
    Input("memory", "data"),
    prevent_initial_call=True
)
def update_lines(sensor,checked,timer,data):

    to_plot = []

    for key, value in data[sensor].items():
        if key in checked:
            to_plot.append([value])
        else:
            to_plot.append([None])
    
    t = np.full((len(to_plot),1), timer)

    return [{"x":t, "y":to_plot}, np.arange(len(to_plot)), 15]

@callback(
    Output("bar_graph", "extendData"),
    State('sensor_select','value'),
    State('data_checklist','value'),
    State('timer', "n_intervals"),
    Input("memory", "data"),
    prevent_initial_call=True
)
def update_bars(sensor,checked,timer,data):

    to_plot = []

    for key, value in data[sensor].items():
        if key in checked:
            to_plot.append([value])
        else:
            to_plot.append([None])
    
    t = np.arange(len(to_plot))[:, np.newaxis]

    return [{"x":t, "y":to_plot}, np.arange(len(to_plot)), 1]

@callback(
    Output("heat_graph", "extendData"),
    State("heat_graph", "figure"),
    State('timer', "n_intervals"),
    Input("memory", "data"),
    prevent_initial_call=True
)
def update_heatmap(fig, timer, data):
    to_z = []
    for key in Utils.SENSORS.keys():
        to_z.append([[data[key]["attention"]]])
        to_z.append([[data[key]["meditation"]]])
    
    t = np.full(
        (len(Utils.SENSORS.keys())*2,1),
        timer
    )

    return [
        {"z":to_z, "y":t}, 
        np.arange(len(Utils.SENSORS.keys())*2), 
        15
    ]


if __name__ =="__main__":
    app.run(debug=True)
    
