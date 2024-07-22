import numpy as np
import sqlite3
from contextlib import closing
import re
import pandas as pd
from src.py.utils.utils import get_date

sqlite3.register_adapter(np.int32, lambda val: int(val))
sqlite3.register_adapter(np.int64, lambda val: int(val))

class Database:

    def __init__(self, db:str) -> None:
        '''
        crea una conexion con la base de datos al crear un objeto del tipo
        Registra otros tipos de datos para guardar en la base de datos, hay
        que ver que datos se van a guardar manualmente
        '''
        self.db = db

    def get_params_header(sensors:tuple, params:tuple) -> list[str]:
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
        conn = sqlite3.connect(self.db)
        with closing(conn.cursor()) as cur:
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
        conn.close()

    def session_table_exists(self)-> bool:
        '''
        revisa que la tabla de sesiones exista
        '''
        conn = sqlite3.connect(self.db)
        with closing(conn.cursor()) as cur:
            tmplist = cur.execute(
                '''
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='session';
                '''
            ).fetchall()
        conn.close()

        if tmplist == []:
             return 0
        else:
             return 1
        

    def record_session_info(self, uid:int, sensors:list, notes:str) -> None:
        '''
        registra los datos de los campos que se pueden llenar en la tabla de las sesiones
        '''
        conn = sqlite3.connect(self.db)
        with closing(conn.cursor()) as cur:
                cur.execute(
                    '''
                    INSERT INTO "session" ("id","sensors","notes")
                    VALUES (?, ?, ?)
                    ''',
                    (uid, len(sensors), notes)
                )
                conn.commit()
        conn.close()

    def update_notes(self, uid:int, notes:str) -> None:
        conn = sqlite3.connect(self.db)
        with closing(conn.cursor()) as cur:
                cur.execute(
                    f'''
                    UPDATE session
                    SET notes = ?
                    WHERE
                        session.id = ?
                    ''',
                    (notes,uid)
                )
                conn.commit()
        conn.close()

    def create_session(self, uid:int, header:str) -> None:
        '''
        crea una tabla para una sesion tomando en cuenta el header que corresponda a la sesion 
        y el uid que se usa para registrar la sesion, se espera que sea el mismo
        '''
        conn = sqlite3.connect(self.db)
        with closing(conn.cursor()) as cur:
            cur.execute(f'CREATE TABLE session_{uid}({header[0]})')
        conn.close()

    def session_exists(self, uid:int)-> bool:
        '''
        revisa que la tabla de sesiones exista
        '''
        conn = sqlite3.connect(self.db)
        with closing(conn.cursor()) as cur:
            tmplist = cur.execute(
                f'''
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='session_{uid}';
                '''
            ).fetchall()
        conn.close()

        if tmplist == []:
             return 0
        else:
             return 1

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

        conn = sqlite3.connect(self.db)
        with closing(conn.cursor()) as cur:
                cur.execute(
                    f'''
                    INSERT INTO "session_{uid}" ({header[0]})
                    VALUES ({header[1]})
                    ''',
                    to_rec
                )
                conn.commit()
        conn.close()
               
    def create_events(self, uid:int) -> None:
        '''
        crea una tabla para una sesion tomando en cuenta el header que corresponda a la sesion 
        y el uid que se usa para registrar la sesion, se espera que sea el mismo
        '''
        conn = sqlite3.connect(self.db)
        with closing(conn.cursor()) as cur:
            cur.execute(f'CREATE TABLE events_{uid}("time", "event")')
        conn.close()

    def events_exists(self, uid:int)-> bool:
        '''
        revisa que la tabla de sesiones exista
        '''
        conn = sqlite3.connect(self.db)
        with closing(conn.cursor()) as cur:
            tmplist = cur.execute(
                f'''
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='events_{uid}';
                '''
            ).fetchall()
        conn.close()

        if tmplist == []:
             return 0
        else:
             return 1

    def record_event(self, uid:int, time, event) -> None:
        '''
        registra los datos de los campos que se pueden llenar en la tabla de las sesiones
        '''
        conn = sqlite3.connect(self.db)
        with closing(conn.cursor()) as cur:
                cur.execute(
                    f'''
                    INSERT INTO "events_{uid}" ("time","event")
                    VALUES (?, ?)
                    ''',
                    (time, event)
                )
                conn.commit()
        conn.close()

    def get_session(self, uid:int, start:int, stop:int):
        with closing(sqlite3.connect(self.db)) as conn:
            return pd.read_sql(
                f"SELECT * FROM session_{uid} LIMIT {stop-start} OFFSET {start}", conn
            )
        
    def get_events(self, uid:int):
        with closing(sqlite3.connect(self.db)) as conn:
            return pd.read_sql(
                f"SELECT * FROM events_{uid}", conn
            )
        
    def list_sessions(self):
        with closing(sqlite3.connect(self.db)) as conn:
            sessions = pd.read_sql("SELECT id, notes FROM session", conn)
            sessions["date"] = sessions["id"].apply(get_date)

            return sessions