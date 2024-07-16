from dash import Dash, dcc, html, Input, Output, callback, State
from utils import Utils

sensors = Utils.SENSORS
params = Utils.SENSOR_PARAMS

def sidebar(dropdown_id:str, checklist_id:str, text_id:str, submit_id:str):
    return html.Div([
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
    })
