import plotly.graph_objects
import plotly.subplots
from utils.utils import Utils
from database.database import Database
import numpy as np
import time
from datetime import datetime


from dash import Dash, dcc, html, Input, Output, callback, State
import plotly

sensors = ('http://127.0.0.1:100', 'http://127.0.0.1:101')
params = Utils.SENSOR_PARAMS

uid = datetime.now().strftime('%Y%m%d%H%M%S')
header = Database.get_header(sensors, params)

figure_lines = {
    'data':[],
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

app = Dash(__name__)
app.layout = html.Div([
    html.Div([
        html.H2('Test')
    ]),
    html.Div([
        dcc.Checklist(
            Utils.SENSOR_PARAMS,
            Utils.SENSOR_PARAMS,
            id='view_params'
        ),
        html.Button('Submit', id='submit-val')
    ],style={'display':'inline-block'}),
    html.Div([
        dcc.Graph(
            id='graph1',
            figure = figure_lines,
            animate=True
        ),
        dcc.Graph(
            id='graph2',
            figure = figure_lines,
            animate=True
        )
    ], style={'display':'inline-block','width': '90vw', 'height': '90vh'}),
    dcc.Interval(
            id='interval-component',
            interval=1*1000, # in milliseconds
            n_intervals=0
        )
], style={})

@callback(
        Output('graph2', 'extendData'),
        Output('graph1', 'extendData'),
        Input('interval-component', 'n_intervals'),
        State('view_params', 'value'),
        prevent_initial_call=True
    )
def update_graph_live(n_intervals, value):

    sensor_live = [Utils.get_data(sensor) for sensor in sensors]
    db = Database('test.db')
    db.record_data(uid, header, sensor_live)
    db.close()

    

    to_plot = Utils.avg_data(*sensor_live)

    for key in Utils.SENSOR_PARAMS_MAP:
        if key not in value:
            to_plot[Utils.SENSOR_PARAMS_MAP[key]] = None

    t = np.full((to_plot.size,1), n_intervals)
    return [
        ({'x':t, 'y':to_plot[:, np.newaxis]}, np.arange(to_plot.size), 10),
        ({'x':np.arange(to_plot.size)[:, np.newaxis], 'y':to_plot[:, np.newaxis]}, np.arange(to_plot.size,to_plot.size*2), 1)
    ]

@callback(
    Output('none', 'children'),
    Input('submit-val', 'n_clicks'),
    prevent_initial_call=True
)
def update_output(n_clicks):
    db = Database('test.db')
    db.record_session_info(uid, sensors,'test')
    db.close()
    return n_clicks



if __name__ =="__main__":
    db = Database('test.db')
    time.sleep(0.5)
    db.create_session(uid, header)
    time.sleep(0.5)
    db.close()

    app.run(debug=True)
    # db = Database('test.db')
    # db.create_session(uid, header)
    # try:
    #     while True:
    #         # app.run(debug=True)
    #         # time.sleep(2)
    #         # sensor_data = [Utils.get_data(sensor) for sensor in sensors]
    #         # print(sensor_data) 
    #         # db.record_data(uid, header, sensor_data)

    # except KeyboardInterrupt:
    #     # 
    #     # db.close()
    
