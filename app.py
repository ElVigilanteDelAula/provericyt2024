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

db = Database("test.db")

if not db.session_table_exists():
    db.create_session_table()

if not db.session_exists(uid):
    db.create_session(uid, header)

figure_lines = {
    'data':[],
    'layout':{'template':'solar'}
}

for param in Utils.SENSOR_PARAMS:
    figure_lines['data'].append({
        'x': [], 
        'y': [], 
        'type':'lines', 
        'name':param
        })
for param in Utils.SENSOR_PARAMS:
    figure_lines['data'].append({
        'x': [], 
        'y': [], 
        'type':'bar', 
        'name':param
        })

dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc_css])
app.layout = html.Div([
    html.Div([
        html.H1('Test', id='title'),
        dcc.Dropdown(
            list(sensors.keys()),
            list(sensors.keys())[0],
            id="dropdown"
        ),
        dcc.Checklist(
            Utils.SENSOR_PARAMS,
            ['signal_strength', 'attention', 'meditation'],
            id='view_params'
        ),
        dcc.Textarea(
            id='notes'
        ),
        html.Button('Submit', id='submit-val')
    ],style={
        'display':'block-flex',
        'flex_direction':'column',
        'justify-content':'space-between',
        'align-items':'center',
        'width': '25vw', 
        'height': '90vh'
    }),
    html.Div([
        dcc.Graph(
            id='graph1',
            figure = figure_lines,
            animate=True,
        ),
        dcc.Graph(
            id='graph2',
            figure = figure_lines,
            animate=True,
        )
    ], style={
        'display':'block-flex',
        'flex_direction':'column',
        'justify-content':'center',
        'align-items':'center',
        'width': '70vw', 
        'height': '90vh'
    }),
    dcc.Interval(
            id='interval-component',
            interval=1*1000, # in milliseconds
            n_intervals=0
        )
],className="dbc" ,style={'display':'flex'})

@callback(
        Output('graph2', 'extendData'),
        Output('graph1', 'extendData'),
        Input('interval-component', 'n_intervals'),
        Input('dropdown', 'value'),
        State('view_params', 'value'),
        prevent_initial_call=True
    )
def update_graph_live(n_intervals, sensor, value):

    sensor_live = [Utils.get_data(sensor) for sensor in sensors.values()]

    db = Database('test.db')

    db.record_data(uid, header, sensor_live)

    to_plot = sensor_live[list(sensors.keys()).index(sensor)]

    for key in Utils.SENSOR_PARAMS_MAP:
        if key not in value:
            to_plot[Utils.SENSOR_PARAMS_MAP[key]] = 0

    t = np.full((to_plot.size,1), n_intervals)
    return [
        ({'x':t, 'y':to_plot[:, np.newaxis]}, np.arange(to_plot.size), 10),
        ({'x':np.arange(to_plot.size)[:, np.newaxis], 'y':to_plot[:, np.newaxis]}, np.arange(to_plot.size,to_plot.size*2), 1)
    ]

@callback(
    Output('title', 'children'),
    Input('submit-val', 'n_clicks'),
    State('notes', 'value'),
    prevent_initial_call=True
)
def update_output(n_clicks, notes):
    '''
    esto probablemente no es la manera de hacerlo pero equis
    '''
    db = Database('test.db')
    db.record_session_info(uid, sensors.values(),notes)

    return 'Test (recorded)'



if __name__ =="__main__":
    app.run()
    
