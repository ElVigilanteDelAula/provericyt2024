from src.py.utils.utils import Utils, event_factory
from src.py.database.database import Database
import numpy as np
import src.py.live_gui.components as components
import src.py.brain_viz.live_brain_callbacks_clean as brain_callbacks  # Import simplified brain callbacks
from datetime import datetime

from dash import Dash, Input, Output, callback, State, no_update, ctx
import dash_bootstrap_components as dbc

# Generar UID más estable (solo hasta segundos para evitar cambios)
uid = int(datetime.now().strftime('%Y%m%d%H%M%S'))
header = Database.get_params_header(Utils.SENSORS.values(), Utils.SENSOR_PARAMS)

db = Database(Utils.DATABASE_PATH)

# Verificar y crear todas las tablas necesarias al inicio
if not db.session_table_exists():
    db.create_session_table()

# Verificar si la sesión ya existe para evitar errores de duplicado
if not db.session_info_exists(uid):
    db.record_session_info(uid, Utils.SENSORS.keys(),"")

# Crear las tablas de datos específicas de la sesión
if not db.session_exists(uid):
    db.create_session(uid, header)

if not db.events_exists(uid):
    db.create_events(uid)

custom_css = r'''
.accordion-item:last-of-type > .accordion-header .accordion-button.collapsed {
  border-bottom-right-radius: var(--bs-accordion-inner-border-radius);
  border-bottom-left-radius: var(--bs-accordion-inner-border-radius);
  background-color: green;
}
'''
app = Dash(external_stylesheets=[dbc.themes.MATERIA, custom_css])

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
    # Solo retornar los datos iniciales, la inicialización ya se hizo
    return f"session_{uid}", {"uid":uid}

@callback(
    Output("memory", "data",  allow_duplicate=True),
    Output("time_text", "children"),
    State("memory", "data"),
    Input('timer', "n_intervals"),
    prevent_initial_call=True
)
def store_data(data, intervals):
    
    # Validar que data no sea None y contenga uid
    if data is None or 'uid' not in data:
        return data, intervals  # Retornar sin procesar si no hay datos válidos

    sensor_live = [Utils.get_data(sensor) for sensor in Utils.SENSORS.values()]

    db.record_data(data['uid'],header,sensor_live)

    tmp = {
        "uid":data['uid'],
    }

    for sensor, readings in zip(Utils.SENSORS.keys(),sensor_live):
        tmp.update({sensor:{}})
        for key, value in zip(Utils.SENSOR_PARAMS_MAP.keys(), readings):
            tmp[sensor].update(
                {key:value}
            )

    return tmp, intervals

@callback(
    Output("line_graph", "extendData"),
    State('sensor_select','value'),
    State('data_checklist','value'),
    State('timer', "n_intervals"),
    Input("memory", "data"),
    prevent_initial_call=True
)
def update_lines(sensor,checked,timer,data):
    
    # Validar que data no sea None y contenga el sensor
    if data is None or sensor not in data:
        return [{"x":[], "y":[]}, [], 0]  # Retornar datos vacíos si no hay datos válidos

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
    
    # Validar que data no sea None y contenga el sensor
    if data is None or sensor not in data:
        return [{"x":[], "y":[]}, [], 0]  # Retornar datos vacíos si no hay datos válidos

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
    
    # Validar que data no sea None y contenga los sensores necesarios
    if data is None:
        return [{"x":[], "y":[], "z":[]}, [], 0]  # Retornar datos vacíos si no hay datos válidos
    
    to_z = []
    for key in Utils.SENSORS.keys():
        if key in data and "attention" in data[key] and "meditation" in data[key]:
            to_z.append([[data[key]["attention"]]])
            to_z.append([[data[key]["meditation"]]])
        else:
            to_z.append([[0]])  # Valor por defecto si no hay datos
            to_z.append([[0]])
    
    t = np.full(
        (len(Utils.SENSORS.keys())*2,1),
        timer
    )

    return [
        {"z":to_z, "y":t}, 
        np.arange(len(Utils.SENSORS.keys())*2), 
        30
    ]


@callback(
    Output("all", "children"),
    State("memory", "data"),
    State('timer', "n_intervals"),
    event_factory(Utils.EVENTS)[1],
    prevent_initial_call=True
)
def record_event(data, time, *args):
    
    # Validar que data no sea None y contenga uid
    if data is None or 'uid' not in data:
        return no_update
        
    db.record_event(data["uid"], time, ctx.triggered_id)
    return no_update

@callback(
    Output("submit", "color"),
    State("notes", "value"),
    State("memory", "data"),
    Input("submit", "n_clicks"),
    prevent_initial_call=True
)
def update_notes(notas, data, n_clicks):
    
    # Validar que data no sea None y contenga uid
    if data is None or 'uid' not in data:
        return "secondary"  # Color por defecto si no hay datos válidos
        
    db.update_notes(data["uid"], notas)
    return "success"

@callback(
    Output("offcanvas", "is_open"),
    Input("open-offcanvas", "n_clicks"),
    [State("offcanvas", "is_open")],
)
def toggle_offcanvas(n1, is_open):
    if n1:
        return not is_open
    return is_open

if __name__ =="__main__":
    # Registrar callbacks del cerebro
    brain_callbacks.register_brain_callbacks(app)
    app.run(host="0.0.0.0", debug=True, port=8050)
    
