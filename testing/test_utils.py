import unittest
import utils
import utils.utils


json_text = '''
{
    "parameters":[
        "signal_strength",
        "attention"
    ],
    "parameter_map":{
        "signal_strength":0,
        "attention":1
    },
    "sensors":{
        "sensor_a":"http://127.0.0.1:5000",
        "sensor_b":"http://127.0.0.1:5001"
    }

}
'''
class TestUtilsConfig(unittest.TestCase):
    '''
    Verifica que se genere bien las variables con el archivo de configuracion
    '''
    def setUp(self) -> None:
        ...

    def tearDown(self) -> None:
        ...
    
    def test_sensorparams(self):
        self.assertIsInstance(
            utils.utils.Utils,
            list[str]
        )

    