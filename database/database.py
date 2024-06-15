import numpy as np
import sqlite3
from contextlib import closing
import re

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

sqlite3.register_adapter(np.int32, lambda val: int(val))

class Database:

    def __init__(self, db:str) -> None:
        '''
        crea una conexion con la base de datos al crear un objeto del tipo
        Registra otros tipos de datos para guardar en la base de datos, hay
        que ver que datos se van a guardar manualmente
        '''
        self.conn = sqlite3.connect(db)
        

    def close(self) -> None:
        '''
        acaba la conexion con la base de datos
        '''
        self.conn.close()

    def get_header(sensors:tuple, params:tuple) -> list[str]:
        '''
        devuelve el encabezado de la tabla tomando en cuenta a los parametros y sensores,
        y tambien un elemento para hacer reemplazos en sql
        '''
        header = ''
        for i in range(len(sensors)):
            for param in params:
                header += f'"{param}{i}",'
        return [header[:len(header)-1], re.sub(r'.\w{0,20}\d.', '?', header[:len(header)-1])]


    def create_session_table(self)-> None:
        '''
        crea una tabla en la base de datos
        '''
        with closing(self.conn.cursor()) as cur:
            cur.execute(
                '''
                CREATE TABLE "session" (
                    "id"	INTEGER UNIQUE,
                    "sensors"	INTEGER,
                    "notes"	TEXT,
                    PRIMARY KEY("id")
                )
                '''
            )
        

    def record_session_info(self, uid:int, sensors:list, notes:str) -> None:
        '''
        registra los datos de los campos que se pueden llenar en la tabla de las sesiones
        '''
        with closing(self.conn.cursor()) as cur:
                cur.execute(
                    '''
                    INSERT INTO "session" ("id","sensors","notes")
                    VALUES (?, ?, ?)
                    ''',
                    (uid, len(sensors), notes)
                )
                self.conn.commit()

    def create_session(self, uid:int, header:str) -> None:
        '''
        crea una tabla para una sesion tomando en cuenta el header que corresponda a la sesion 
        y el uid que se usa para registrar la sesion, se espera que sea el mismo
        '''
        with closing(self.conn.cursor()) as cur:
            cur.execute(f'CREATE TABLE session_{uid}({header[0]})')

    def record_data(self, uid:int, header:list[str], data:list[np.ndarray]) -> None:
        '''
        espera una lista de los arreglos que contienen los datos de los sensores,
        en el mismo orden en el que estan declarados los sensores en el header

        Igualmente se espera que ya se haya creado una sesion con create_session,
        y pone los datos de los sensores en donde corresponden en la tabla
        '''
        to_rec = []
        for array in data:
             for i in array:
                  to_rec.append(i)

        with closing(self.conn.cursor()) as cur:
                cur.execute(
                    f'''
                    INSERT INTO "session_{uid}" ({header[0]})
                    VALUES ({header[1]})
                    ''',
                    to_rec
                )
                self.conn.commit()
               

            
if __name__ == '__main__':
    # sensors = (1,2)
    # params = SENSOR_PARAMS
    # data = [np.array([1,1,1]), np.array([None, None, None])]
    # db = Database('test.db')
    # header = Database.get_header(sensors, params)
    # print(header)
    # uid = np.random.randint(0, 100)
    # db.create_session(uid, header)
    # db.record_data(uid, header, data)
    # db.close()
    ...