import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import requests
import numpy as np
import json
from dash import Input, Output, State
import re
from datetime import datetime

class Utils:

    with open('config.json') as file:

        config = json.load(file)

        SENSOR_PARAMS = config['parameters']

        SENSOR_PARAMS_MAP = config['parameter_map']

        SENSORS = config['sensors']

        SENSORS_MAP = config["sensors_map"]

        EVENTS = config["events"]


    def get_data(sensor: str) -> np.ndarray:
        '''
        luego de definir un sensor con el ip y puerto correspondientes, e.g.

        'http://192.168.1.12:105/'

        manda una instruccion de GET al servidor que establece el sensor, para
        recibir la informacion del sensor

        espera una respuesta en JSON de tipo
        
        {"data":"[0.8014442490425848, 0.12287946936057148, ...]"}

        si no se obtiene, devuelve None
        '''
        try:
            request = requests.get(sensor, stream=True, timeout=0.5)
            return np.array(
                request.json()['data']
            )
        except:
            print(f'Hay un problema con {sensor}')
            return np.full(shape=len(Utils.SENSOR_PARAMS), fill_value=None)
            

    def avg_data(*arrays: np.ndarray) -> np.ndarray:
        '''
        toma arreglos [a, b, c] y devuelve [a_avg, b_avg, c_avg]

        Si un arreglo es none, lo ignora
        '''
        to_avg = []
        for array in arrays:
            if array.any() is not None:
                to_avg.append(array)
        return np.average(
            np.array(to_avg), axis=0
        )


if __name__ =="__main__":
    # request = requests.get('http://192.168.152.123:85/', stream=True, timeout=0.5)
    # print(json.loads(request.json()["data"]))
    # sensors = ('http://192.168.152.123:85/', )
    # sensor_data = [Utils.get_data(sensor) for sensor in sensors]

    # print(sensor_data)
    ...


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
                colorscale="sunsetdark",
                zmax=100,
                zmin=0,
                showscale=False
            )
        )
        tmp.append(
            go.Heatmap(
                z=[[0]],
                y=[],
                x=[i+1],
                colorscale="deep",
                zmax=100,
                zmin=0,
                showscale=False
            )
        )
    return tmp

def event_factory(events:dict):
    tmp_components = []
    tmp_inputs = [
        Input("inicio", "n_clicks"),
        Input("final", "n_clicks")
    ]
    for key, value in events.items():
        tmp_components.append(
            dbc.Button(
                key,
                color="secondary",
                id=key,
                style=value
            )
        )
        tmp_inputs.append(
            Input(key, "n_clicks")
        )
    return tmp_components,tmp_inputs

def get_uid(name:str)->str:
    return re.findall(r"\d+", name)

def get_date(name:int)->datetime:
    return datetime.strptime(
        re.findall(r"\d+", str(name))[0],
        r'%Y%m%d%H%M%S'
    ).strftime(r"%c")

def static_line_plot_factory(uid, db, checked, sensors):

    line_figure = go.Figure()

    index=[]
    for sensor in sensors:
        index += map(
            lambda x:x+str(Utils.SENSORS_MAP[sensor]),
            Utils.SENSOR_PARAMS
        )

    events = db.get_events(uid)
    session = db.get_session(uid, events.iloc[0, 0], events.iloc[-1,0]).loc[:,index]

    for wave in checked:

        for name, data in session.items():
            if wave in name:
                line_figure.add_trace(
                    go.Scatter(
                        x=session.index,
                        y=data,
                        name=name
                    )
                )
        
    for time, event in events.loc[:,["time", "event"]].values:
        line_figure.add_vline(time, annotation_text=event)

    line_figure.update_layout(
        {
            "xaxis":{
                "rangeslider":{
                    "visible":True
                }
            }
        }
    )
    
    return line_figure

def static_heat_plot_factory(uid, db, checked, sensors):

    graph_figure = go.Figure()

    index=[]
    for sensor in sensors:
        index += map(
            lambda x:x+str(Utils.SENSORS_MAP[sensor]),
            Utils.SENSOR_PARAMS
        )

    events = db.get_events(uid)
    session = db.get_session(uid, events.iloc[0, 0], events.iloc[-1,0]).loc[:,index]
    normalized=(session-session.min())/(session.max()-session.min())

    # for wave in checked:

    #     for name, data in session.items():
    #         if wave in name:
    #             ...

    graph_figure.add_trace(
        go.Heatmap(
            x=session.index,
            y=session.columns,
            z=normalized.transpose(),
            colorscale="deep"
        )
    )
        
    for time, event in events.loc[:,["time", "event"]].values:
        graph_figure.add_vline(time, annotation_text=event)

    graph_figure.update_layout(
        {
            "xaxis":{
                "rangeslider":{
                    "visible":True
                }
            }
        }
    )
    
    return graph_figure