import requests
import numpy as np
import json

class Utils:

    TEST_PARAMS = ['a', 'b']
    SENSOR_PARAMS = [
        'signal_strength',
        'attention',
        'meditation',
        'delta',
        'theta',
        'low_alpha',
        'high_alpha',
        'low_beta',
        'high_beta',
        'low_gamma',
        'high_gamma'
    ]

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
            return np.full(shape=len(Utils.TEST_PARAMS), fill_value=None)
            

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
    # sensors = ('http://127.0.0.1:100', 'http://127.0.0.1:101', 'http://127.0.0.1:102')
    # sensor_data = [Utils.get_data(sensor) for sensor in sensors]

    # print(sensor_data)
    # print(Utils.avg_data(*sensor_data))
    ...


