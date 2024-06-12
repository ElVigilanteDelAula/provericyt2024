import requests
import numpy as np
import json
import sqlite3

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
        request = requests.get(sensor, stream=True, timeout=0.1)
        return np.array(
            json.loads(request.json()['data'])
        )
    except:
        print(f'Hay un problema con {sensor}')
        return None
        

def avg_data(*arrays: np.ndarray) -> np.ndarray:
    '''
    toma arreglos [a, b, c] y devuelve [a_avg, b_avg, c_avg]

    Si un arreglo es none, lo ignora
    '''
    to_avg = []
    for array in arrays:
        if array is not None:
            to_avg.append(array)
    return np.average(
        np.array(to_avg), axis=0
    )

sensors = ['http://127.0.0.1:100', 'http://127.0.0.1:101', 'http://127.0.0.1:102']
sensor_data = [get_data(sensor) for sensor in sensors]

print(sensor_data)
print(avg_data(*sensor_data))


