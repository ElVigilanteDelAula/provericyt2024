import requests
import numpy as np
import json

def get_data(sensor: str) -> np.ndarray:
    '''
    luego de definir un sensor con el ip y puerto correspondientes, e.g.

    'http://192.168.1.12:105/'

    manda una instruccion de GET al servidor que establece el sensor, para
    recibir la informacion del sensor

    espera una respuesta en JSON de tipo
    
    {"data":"[0.8014442490425848, 0.12287946936057148, ...]"}

    '''
    request = requests.get(sensor, stream=True)

    return np.array(
        json.loads(request.json()['data'])
    )

def to_db(db):
    ...

print(get_data("http://192.168.1.12:105/"))